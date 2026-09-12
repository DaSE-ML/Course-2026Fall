import { MeetingPlanError } from './request.mjs';

const HALF_HOUR_MS = 30 * 60 * 1000;
const MAX_DURATION_MS = 6 * 60 * 60 * 1000;
// 服务端要求开始时间严格在未来；预留提交流程耗时，避免临界被拒。
const ASAP_BUFFER_MS = 90_000;

export function assertFutureStart(start, now = new Date()) {
  if (start.getTime() <= now.getTime()) {
    throw new MeetingPlanError('开始时间必须在未来（服务端拒绝过去的会议）。', 'PAST_START');
  }
}

export function ceilStartToHalfHour(start) {
  const remainder = start.getTime() % HALF_HOUR_MS;
  if (remainder === 0) return start;
  return new Date(start.getTime() + (HALF_HOUR_MS - remainder));
}

export function nextHalfHourSlot(now = new Date()) {
  return ceilStartToHalfHour(new Date(now.getTime() + ASAP_BUFFER_MS));
}

export function ceilEndToHalfHour(start, end) {
  const requestedDuration = end.getTime() - start.getTime();
  const effectiveDuration = Math.ceil(requestedDuration / HALF_HOUR_MS) * HALF_HOUR_MS;
  return new Date(start.getTime() + effectiveDuration);
}

export function splitIntoMeetings(subject, start, effectiveEnd) {
  const meetings = [];
  let cursor = start.getTime();
  const end = effectiveEnd.getTime();

  while (cursor < end) {
    const next = Math.min(cursor + MAX_DURATION_MS, end);
    meetings.push({ start: new Date(cursor), end: new Date(next) });
    cursor = next;
  }

  return meetings.map((meeting, index) => ({
    ...meeting,
    sequence: index + 1,
    subject: meetings.length === 1 ? subject : `${subject}（${index + 1}/${meetings.length}）`,
    durationMinutes: (meeting.end.getTime() - meeting.start.getTime()) / 60000,
  }));
}
