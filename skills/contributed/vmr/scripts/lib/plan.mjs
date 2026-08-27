import { fingerprintPlan, requestIdFromFingerprint } from './fingerprint.mjs';
import { normalizeMeetingOptions } from './options.mjs';
import { formatShanghai, parseRequest } from './request.mjs';
import { assertFutureStart, ceilEndToHalfHour, splitIntoMeetings } from './time-policy.mjs';

export function createMeetingPlan(input, now = new Date()) {
  const request = parseRequest(input);
  const normalizedOptions = normalizeMeetingOptions(rawOptions(input));
  assertFutureStart(request.start, now);

  const effectiveEnd = ceilEndToHalfHour(request.start, request.end);
  const meetings = splitIntoMeetings(request.subject, request.start, effectiveEnd).map((meeting) => ({
    ...meeting,
    start: formatShanghai(meeting.start),
    end: formatShanghai(meeting.end),
  }));
  const canonical = {
    schemaVersion: 1,
    subject: request.subject,
    start: formatShanghai(request.start),
    end: formatShanghai(request.end),
    effectiveEnd: formatShanghai(effectiveEnd),
    timeZone: request.timeZone,
    options: {
      payloadOverrides: normalizedOptions.payloadOverrides,
      notes: normalizedOptions.notes,
    },
    meetings,
  };
  const fingerprint = fingerprintPlan(canonical);

  return {
    ...canonical,
    status: 'ready_for_confirmation',
    requestId: requestIdFromFingerprint(fingerprint),
    fingerprint: `sha256:${fingerprint}`,
    shortFingerprint: fingerprint.slice(0, 12),
    confirmation: {
      required: true,
      acceptedValues: [requestIdFromFingerprint(fingerprint), fingerprint.slice(0, 12)],
    },
    calendar: { policy: 'after_approval_only' },
  };
}

export function renderPlanSummary(plan) {
  const rows = plan.meetings.map((meeting) => (
    `  ${meeting.sequence}. ${meeting.subject}\n     ${meeting.start} → ${meeting.end}（${meeting.durationMinutes} 分钟）`
  ));

  const optionLines = plan.options?.notes?.length ? [`已启用自定义选项：`, ...plan.options.notes.map((note) => `  · ${note}`)] : [];

  return [
    `请求 ID：${plan.requestId}`,
    `原始时间：${plan.start} → ${plan.end}`,
    `有效结束时间：${plan.effectiveEnd}`,
    ...optionLines,
    '以下申请提交后均须等待管理员审批：',
    ...rows,
  ].join('\n');
}

function rawOptions(input) {
  const raw = input?.options;
  if (!raw || typeof raw !== 'object') return {};
  return {
    ...raw,
    fields: typeof raw.fields === 'string' ? [raw.fields] : raw.fields,
  };
}
