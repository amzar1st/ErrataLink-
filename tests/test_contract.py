import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sdk = types.ModuleType("genlayer")
sdk.TreeMap = dict
sdk.gl = types.SimpleNamespace(
    Contract=object, vm=types.SimpleNamespace(UserError=ValueError),
    public=types.SimpleNamespace(view=lambda fn: fn, write=lambda fn: fn),
)
spec = importlib.util.spec_from_file_location("errata_link", ROOT / "contracts/errata_link.py")
module = importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, {"genlayer": sdk}):
    spec.loader.exec_module(module)


class ErrataTests(unittest.TestCase):
    def setUp(self):
        self.document = (ROOT / "evidence/harbor-ridership-v1.json").read_bytes()
        self.notice = (ROOT / "evidence/harbor-ridership-correction-1.json").read_bytes()
        self.rfc = "B.1.  Appendix subsection\nB.1.1.  Detail\nB.2.  Another subsection\n"
        self.page = ("<pre><b><i><a href='/e'>EID 7105</a> (Verified) is as follows:</i></b>"
                     "<b>Section:</b> B.1. <b>Original Text:</b> Before &amp; old "
                     "<b>Corrected Text:</b> After</pre>")
        self.pin = module.fingerprint(["B.1.", "Before & old", "After"])

    def check_cell(self, cell, pin=module.TABLE_NOTICE, document=None):
        return module.table_result("table:2/" + cell, pin, document or self.document, self.notice)

    def test_corrected_cell(self):
        self.assertEqual(self.check_cell("east.weekday")["verdict"], "AFFECTED")

    def test_neighboring_cell(self):
        self.assertEqual(self.check_cell("west.weekday")["verdict"], "UNAFFECTED")

    def test_unknown_cell(self):
        self.assertEqual(self.check_cell("north.weekday")["reason"], "CITATION_NOT_FOUND")

    def test_bad_pin_and_changed_source(self):
        self.assertEqual(self.check_cell("east.weekday", "0" * 64)["reason"], "EVIDENCE_HASH_MISMATCH")
        self.assertEqual(self.check_cell("east.weekday", document=b"changed")["verdict"], "INCONCLUSIVE")

    def test_rfc_exact_match_and_distinct_section(self):
        for section, expected in [("B.1", "AFFECTED"), ("B.2", "UNAFFECTED"), ("B.1.1", "INCONCLUSIVE")]:
            with self.subTest(section=section):
                self.assertEqual(module.rfc_result(section, "7105", self.pin, self.rfc, self.page)["verdict"], expected)

    def test_ambiguous_or_unverified_notice(self):
        for page in [self.page * 2, self.page.replace("Verified", "Rejected")]:
            self.assertEqual(module.rfc_result("B.1", "7105", self.pin, self.rfc, page)["reason"],
                             "VERIFIED_NOTICE_NOT_FOUND")

    def test_modified_notice_and_missing_section(self):
        self.assertEqual(module.rfc_result("B.1", "7105", self.pin, self.rfc, self.page.replace("After", "Different"))["reason"],
                         "EVIDENCE_HASH_MISMATCH")
        self.assertEqual(module.rfc_result("B.10", "7105", self.pin, self.rfc, self.page)["reason"],
                         "CITATION_NOT_FOUND")

    def test_input_allowlist(self):
        for values in [("https://host", "B.1", "7105", self.pin),
                       ("rfc9110", "B.1", "../7105", self.pin),
                       ("harbor-v1", "table:2/unknown", "1", self.pin)]:
            with self.assertRaises(ValueError):
                module.request_for(*values)

    def test_duplicate_review_reuses_result(self):
        contract = module.ErrataLink()
        contract.reviews = {}
        values = ("harbor-v1", "table:2/east.weekday", "1", module.TABLE_NOTICE)
        with patch.object(module, "fetch", side_effect=[self.document, self.notice]) as fetch:
            with patch.object(sdk.gl, "eq_principle", types.SimpleNamespace(strict_eq=lambda fn: fn()), create=True):
                key = contract.verify(*values)
                self.assertEqual(contract.verify(*values), key)
        self.assertEqual(fetch.call_count, 2)
        self.assertIn('"verdict":"AFFECTED"', contract.get_review(key))
        self.assertEqual(contract.get_review("0" * 64), "")


if __name__ == "__main__":
    unittest.main()
