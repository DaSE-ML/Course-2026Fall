import { MeetingPlanError } from './request.mjs';

const HALF_HOUR_MS = 30 * 60 * 1000;
const MAX_DURATION_MS = 6 * 60 * 60 * 1000;

export function assertFutureStart(start, now = new Date()) {
  if (start.getTime() <= now.getTime()) {
    throw new MeetingPlanError('开始时间必须在未来。', 'PAST_START');
  }
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
