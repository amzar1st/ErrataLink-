import { createClient } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';
import { TransactionHashVariant } from 'genlayer-js/types';
import { address, explorer, samples, demoTransactions } from './config.mjs';
import { lifecycle, reviewId } from './protocol.mjs';

const client = createClient({ chain: studionet });
const $ = id => document.getElementById(id);
const names = ['document', 'locator', 'notice', 'pin'];
const reason = {
  SAME_CELL: 'The notice replaces the cited cell.',
  DISJOINT_CELL: 'This notice replaces a different cell.',
  CITED_SECTION_INCLUDES_CHANGE: 'The cited section contains the replacement.',
  DISJOINT_SECTION: 'The notice names a separate section.',
  NOTICE_NAMES_ANCESTOR: 'The notice is broader than the citation.',
  CITATION_NOT_FOUND: 'The cited or affected location could not be confirmed.',
  EVIDENCE_HASH_MISMATCH: 'The evidence differs from the pinned revision.',
  VERIFIED_NOTICE_NOT_FOUND: 'A supported verified notice could not be identified.',
  UNSUPPORTED_CHANGE: 'The notice could not be interpreted under this policy.',
};
const argsList = $('args');
let lookupSequence = 0;
let prepareSequence = 0;
let trackingSequence = 0;
let trackingTimer;

function showLink(node, url) {
  node.href = url;
  node.target = '_blank';
  node.rel = 'noreferrer';
  node.hidden = false;
}
if (address) showLink($('contract'), explorer + '/address/' + address);

function render(record) {
  $('verdict').textContent = record.verdict;
  $('verdict').dataset.verdict = record.verdict;
  $('reason').textContent = reason[record.reason] ?? record.reason;
  $('details').replaceChildren();
  const [documentVersion, locator, notice, pin] = record.request;
  for (const [key, value] of Object.entries({
    'Document version': documentVersion, 'Citation': locator, 'Notice ID': notice,
    'Affected location': record.affected_locator || 'Unconfirmed', 'Change': record.change_type,
    'Policy': record.policy, 'Notice SHA-256': pin, 'Document SHA-256': record.document_sha256,
    'Decision SHA-256': record.decision_sha256,
  })) {
    const label = document.createElement('dt');
    const content = document.createElement('dd');
    label.textContent = key;
    content.textContent = value;
    $('details').append(label, content);
  }
  $('sources').replaceChildren();
  for (const [label, url] of [['Original document ↗', record.document_url], ['Correction evidence ↗', record.notice_url]]) {
    if (!/^https:\/\/(?:www\.rfc-editor\.org\/rfc\/|raw\.githubusercontent\.com\/amzar1st\/ErrataLink-\/)/.test(url)) continue;
    const anchor = document.createElement('a');
    anchor.textContent = label;
    showLink(anchor, url);
    $('sources').append(anchor);
  }
  $('result').hidden = false;
}

async function loadReview(id) {
  const sequence = ++lookupSequence;
  $('result').hidden = true;
  $('review-status').textContent = address ? 'Reading finalized Studionet state…' : 'Contract address is not configured.';
  if (!address) return;
  try {
    const raw = await client.readContract({ address, functionName: 'get_review', args: [id], transactionHashVariant: TransactionHashVariant.LATEST_FINAL });
    if (sequence !== lookupSequence) return;
    if (!raw) {
      $('review-status').textContent = 'No finalized review for this ID. Check the transaction or verify the inputs.';
      return;
    }
    render(JSON.parse(raw));
    $('review-status').textContent = 'Read from finalized Studionet state.';
  } catch {
    if (sequence === lookupSequence) $('review-status').textContent = 'Could not read Studionet. Try again.';
  }
}

async function prepare(args) {
  const sequence = ++prepareSequence;
  const id = await reviewId(args);
  if (sequence !== prepareSequence) return;
  argsList.replaceChildren();
  args.forEach((value, index) => {
    const row = document.createElement('li');
    row.textContent = names[index] + ' = ' + value + ' ';
    const copy = document.createElement('button');
    copy.type = 'button';
    copy.textContent = 'Copy';
    copy.setAttribute('aria-label', 'Copy ' + names[index]);
    copy.onclick = async () => {
      try {
        await navigator.clipboard.writeText(value);
        copy.textContent = 'Copied';
      } catch {
        copy.textContent = 'Select text';
      }
    };
    row.append(copy);
    argsList.append(row);
  });
  $('prepared').hidden = false;
  $('review-id').value = id;
  $('prepare-status').textContent = 'Review ID generated.';
  await loadReview(id);
}

async function track(hash) {
  const sequence = ++trackingSequence;
  clearTimeout(trackingTimer);
  $('tx-status').textContent = 'Reading Studionet transaction…';
  showLink($('tx-link'), explorer + '/tx/' + hash);
  let attempts = 0;
  async function poll() {
    let receipt;
    try {
      receipt = await client.getTransaction({ hash });
    } catch {
      receipt = undefined;
    }
    if (sequence !== trackingSequence) return;
    const progress = lifecycle(receipt);
    $('tx-status').textContent = progress.label;
    if (progress.stop) {
      if (progress.success && $('lookup').checkValidity()) void loadReview($('review-id').value);
      return;
    }
    if (++attempts >= 30) {
      $('tx-status').textContent += ' · polling paused. Select Track to resume.';
      return;
    }
    trackingTimer = setTimeout(poll, 6000);
  }
  await poll();
}

$('prepare').addEventListener('submit', event => {
  event.preventDefault();
  const args = names.map(name => $('prepare').elements.namedItem(name).value.trim());
  const [documentVersion, locator, notice, pin] = args;
  const valid = documentVersion === 'harbor-v1'
    ? notice === '1' && /^table:2\/[a-z]{1,20}\.[a-z]{1,20}$/.test(locator)
    : /^rfc[1-9]\d{0,4}$/.test(documentVersion) && /^[1-9]\d{0,7}$/.test(notice)
      && /^(?:[1-9]\d{0,2}|[A-Z])(?:\.\d{1,3}){0,5}$/.test(locator);
  if (!valid || !/^[a-f0-9]{64}$/.test(pin)) {
    ++prepareSequence;
    $('prepared').hidden = true;
    $('prepare-status').textContent = 'Check the version, locator, notice ID and SHA-256.';
    return;
  }
  void prepare(args);
});
$('lookup').addEventListener('submit', event => {
  event.preventDefault();
  void loadReview($('review-id').value);
});
$('track').addEventListener('submit', event => {
  event.preventDefault();
  void track($('tx').value);
});
function chooseSample(sample) {
  names.forEach((name, i) => { $('prepare').elements.namedItem(name).value = samples[sample][i]; });
  if (demoTransactions[sample]) {
    $('tx').value = demoTransactions[sample];
    void track($('tx').value);
  }
  return prepare(samples[sample]);
}
document.querySelectorAll('[data-sample]').forEach(button => {
  button.addEventListener('click', () => { void chooseSample(button.dataset.sample); });
});
void chooseSample('affected');
