# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import hashlib
import html
import json
import re

RFC = "https://www.rfc-editor.org/rfc/"
FIXTURE = ("https://raw.githubusercontent.com/amzar1st/ErrataLink-/"
           "fc6063e9b7cbe76de480a14d0980e780041a159a/evidence/")
TABLE_DOC = "edd053cd5ce4aed429cc785d2e7ddae506021fbb4dc8b4d41fa665e1b15b11da"
TABLE_NOTICE = "e84a6ff035044b54255eb85ffc4346a6bd281878cde5a5b73504fbb060d356e6"
POLICY = "erratalink-v1"
SECTION = r"(?:[1-9][0-9]{0,2}|[A-Z])(?:\.[0-9]{1,3}){0,5}"
CELL = r"table:2/[a-z]{1,20}\.[a-z]{1,20}"


def pack(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fingerprint(value):
    return sha(pack(value).encode("utf-8"))


def require(condition, message):
    if not condition:
        raise gl.vm.UserError(message)


def evidence_urls(document, notice):
    if document == "harbor-v1":
        return (FIXTURE + "harbor-ridership-v1.json",
                FIXTURE + "harbor-ridership-correction-1.json")
    return (RFC + document + ".txt",
            RFC + "inline-errata/" + document + ".html")


def request_for(document, locator, notice, pin):
    require(len(document) <= 12 and len(locator) <= 40 and len(notice) <= 8
            and len(pin) == 64 and re.fullmatch(r"[a-f0-9]{64}", pin),
            "Invalid input size or SHA-256")
    if document == "harbor-v1":
        require(notice == "1" and re.fullmatch(CELL, locator), "Invalid demo citation")
    else:
        require(re.fullmatch(r"rfc[1-9][0-9]{0,4}", document)
                and re.fullmatch(r"[1-9][0-9]{0,7}", notice)
                and re.fullmatch(SECTION, locator), "Invalid RFC citation")
    return [document, locator, notice, pin]


def fetch(url):
    try:
        response = gl.nondet.web.get(url.split("#", 1)[0])
        if 0 < len(response.body) <= 2_000_000:
            return response.body
    except Exception:
        pass
    raise gl.vm.UserError("Evidence retrieval failed. Retry this request when the source is available.")


def verdict(outcome, reason, target="", kind="none"):
    return {"verdict": outcome, "reason": reason, "affected_locator": target, "change_type": kind}


def table_result(locator, pin, document, notice):
    if sha(document) != TABLE_DOC or sha(notice) != TABLE_NOTICE or pin != TABLE_NOTICE:
        return verdict("INCONCLUSIVE", "EVIDENCE_HASH_MISMATCH")
    source = json.loads(document)
    correction = json.loads(notice)
    cell = locator.split("/", 1)[1]
    target = "table:2/east.weekday"
    if cell not in source["cells"]:
        return verdict("INCONCLUSIVE", "CITATION_NOT_FOUND", target, "replace")
    change = correction["changes"]["east.weekday"]
    if source["cells"]["east.weekday"] != change["before"] or change["before"] == change["after"]:
        return verdict("INCONCLUSIVE", "UNSUPPORTED_CHANGE")
    return (verdict("AFFECTED", "SAME_CELL", target, "replace") if locator == target
            else verdict("UNAFFECTED", "DISJOINT_CELL", target, "replace"))


def notice_fields(page, notice):
    pattern = (r"<pre[^>]*>\s*<b><i><a\b[^>]*>\s*EID\s+" + notice
               + r"\s*</a>\s*\(Verified\)\s+is as follows:</i></b>(.*?)</pre>")
    blocks = re.findall(pattern, page, re.DOTALL | re.IGNORECASE)
    if len(blocks) != 1:
        return None
    body = html.unescape(re.sub(r"<[^>]+>", " ", blocks[0]))
    fields = re.fullmatch(
        r"\s*Section:\s*(.*?)\s*Original Text:\s*(.*?)\s*Corrected Text:\s*(.*?)\s*",
        body, re.DOTALL)
    if not fields:
        return None
    return [" ".join(value.split()) for value in fields.groups()]


def has_section(document, section):
    # A TOC line is indented further than a heading in RFC plain text.
    return re.search(r"^ {0,3}(?:Appendix )?" + re.escape(section)
                     + r"\.?[ \t]{2,}\S", document, re.MULTILINE) is not None


def rfc_result(locator, notice_id, pin, document, page):
    fields = notice_fields(page, notice_id)
    if not fields:
        return verdict("INCONCLUSIVE", "VERIFIED_NOTICE_NOT_FOUND")
    if fingerprint(fields) != pin:
        return verdict("INCONCLUSIVE", "EVIDENCE_HASH_MISMATCH")
    section, before, after = fields
    target = section.rstrip(".")
    if not re.fullmatch(SECTION, target) or not before or not after or before == after:
        return verdict("INCONCLUSIVE", "UNSUPPORTED_CHANGE")
    if not has_section(document, locator) or not has_section(document, target):
        return verdict("INCONCLUSIVE", "CITATION_NOT_FOUND", target, "replace")
    if locator == target or target.startswith(locator + "."):
        return verdict("AFFECTED", "CITED_SECTION_INCLUDES_CHANGE", target, "replace")
    if locator.startswith(target + "."):
        return verdict("INCONCLUSIVE", "NOTICE_NAMES_ANCESTOR", target, "replace")
    return verdict("UNAFFECTED", "DISJOINT_SECTION", target, "replace")


def inspect(request):
    document, locator, notice, pin = request
    source_url, notice_url = evidence_urls(document, notice)
    original = fetch(source_url)
    correction = fetch(notice_url)
    if document == "harbor-v1":
        result = table_result(locator, pin, original, correction)
    else:
        result = rfc_result(locator, notice, pin, original.decode("utf-8"), correction.decode("utf-8"))
    result.update({"policy": POLICY, "request": request, "document_url": source_url,
                   "notice_url": notice_url, "document_sha256": sha(original)})
    return result


class ErrataLink(gl.Contract):
    reviews: TreeMap[str, str]

    def __init__(self):
        pass

    @gl.public.write
    def verify(self, document: str, locator: str, notice: str, pin: str) -> str:
        request = request_for(document, locator, notice, pin)
        key = fingerprint(request)
        if key not in self.reviews:
            decision = gl.eq_principle.strict_eq(lambda: inspect(request))
            decision["decision_sha256"] = fingerprint(decision)
            self.reviews[key] = pack(decision)
        return key

    @gl.public.view
    def get_review(self, review_id: str) -> str:
        require(len(review_id) == 64 and re.fullmatch(r"[a-f0-9]{64}", review_id),
                "Invalid review ID")
        return self.reviews[review_id] if review_id in self.reviews else ""

    @gl.public.view
    def policy(self) -> str:
        return POLICY
