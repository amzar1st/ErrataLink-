import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { lifecycle, reviewId } from '../web/protocol.mjs';
import { samples } from '../web/config.mjs';

test('review key uses compact JSON and SHA-256', async () => {
  assert.equal(await reviewId(samples.affected), createHash('sha256').update(JSON.stringify(samples.affected)).digest('hex'));
  assert.notEqual(await reviewId(samples.affected), await reviewId(samples.unaffected));
});
test('queued and accepted transactions continue polling', () => {
  assert.equal(lifecycle(undefined).stop, false);
  assert.deepEqual(lifecycle({statusName: 'ACCEPTED'}), {label: 'Accepted · awaiting finalization', stop: false});
});
test('successful finalization is distinct from failure and unknown result', () => {
  assert.equal(lifecycle({status: 7, txExecutionResultName: 'FINISHED_WITH_RETURN'}).success, true);
  assert.equal(lifecycle({status: 7, txExecutionResultName: 'FINISHED_WITH_ERROR'}).success, false);
  assert.match(lifecycle({status: 7}).label, /unavailable/);
  assert.equal(lifecycle({statusName: 'CANCELED'}).stop, true);
});
