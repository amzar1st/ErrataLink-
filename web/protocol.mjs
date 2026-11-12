export async function reviewId(args) {
  const data = new TextEncoder().encode(JSON.stringify(args));
  const digest = new Uint8Array(await globalThis.crypto.subtle.digest('SHA-256', data));
  return Array.from(digest, byte => byte.toString(16).padStart(2, '0')).join('');
}

export function lifecycle(receipt) {
  if (!receipt) return { label: 'Waiting for the transaction to appear', stop: false };
  const states = ['UNINITIALIZED', 'PENDING', 'PROPOSING', 'COMMITTING', 'REVEALING', 'ACCEPTED', 'UNDETERMINED', 'FINALIZED', 'CANCELED'];
  const status = receipt.statusName ?? receipt.status_name ?? states[receipt.status] ?? receipt.status;
  const leaders = receipt.consensus_data?.leader_receipt;
  const leader = Array.isArray(leaders) ? leaders.at(-1) : leaders;
  const result = receipt.txExecutionResultName ?? receipt.execution_result ?? leader?.result?.status;
  if (status === 'FINALIZED') {
    const success = /^(SUCCESS|FINISHED_WITH_RETURN|RETURN)$/i.test(result ?? '');
    const label = success ? 'Finalized · execution succeeded'
      : result ? 'Finalized · execution failed (' + result + ')' : 'Finalized · execution result unavailable';
    return { label, stop: true, success };
  }
  if (status === 'CANCELED') return { label: 'Canceled', stop: true };
  return { label: status === 'ACCEPTED' ? 'Accepted · awaiting finalization' : String(status ?? 'Pending').replaceAll('_', ' '), stop: false };
}
