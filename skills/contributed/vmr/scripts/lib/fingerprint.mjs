import { createHash } from 'node:crypto';

export function fingerprintPlan(value) {
  const canonical = JSON.stringify(value);
  return createHash('sha256').update(canonical).digest('hex');
}

export function requestIdFromFingerprint(fingerprint) {
  return `meeting-${fingerprint.slice(0, 12)}`;
}
