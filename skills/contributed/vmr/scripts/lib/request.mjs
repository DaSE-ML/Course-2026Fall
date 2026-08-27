export class MeetingPlanError extends Error {
  constructor(message, code = 'INVALID_REQUEST') {
    super(message);
    this.name = 'MeetingPlanError';
    this.code = code;
  }
}

const SHANGHAI_OFFSET = '+08:00';

export function parseRequest(input) {
  const subject = typeof input.subject === 'string' ? input.subject.trim() : '';
  if (!subject) {
    throw new MeetingPlanError('会议主题不能为空。');
  }

  if (input.timeZone !== 'Asia/Shanghai') {
    throw new MeetingPlanError('时区必须为 Asia/Shanghai。');
  }

  const start = parseShanghaiDateTime(input.start, '开始时间');
  const end = parseShanghaiDateTime(input.end, '结束时间');
  if (end.getTime() <= start.getTime()) {
    throw new MeetingPlanError('结束时间必须晚于开始时间。');
  }

  return { subject, start, end, timeZone: 'Asia/Shanghai' };
}

function parseShanghaiDateTime(value, label) {
  if (typeof value !== 'string' || !value.endsWith(SHANGHAI_OFFSET)) {
    throw new MeetingPlanError(`${label}必须是带 +08:00 偏移量的 ISO-8601 时间。`);
  }

  const result = new Date(value);
  if (Number.isNaN(result.getTime())) {
    throw new MeetingPlanError(`${label}不是有效时间。`);
  }

  return result;
}

export function formatShanghai(date) {
  const parts = new Intl.DateTimeFormat('sv-SE', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
  }).formatToParts(date);
  const value = Object.fromEntries(parts.map(({ type, value }) => [type, value]));
  return `${value.year}-${value.month}-${value.day}T${value.hour}:${value.minute}:00+08:00`;
}
