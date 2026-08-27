import { MeetingPlanError } from './request.mjs';

export const SIZE_OPTIONS = [100, 200, 300, 500, 1000, 2000];
const REPEAT_TYPE_MAP = { daily: '1', weekly: '2', monthly: '3' };

const BOOLEAN_FIELDS = {
  waitingRoom: ['waiting_room', '等候室'],
  ssoOnly: ['option_sso_only', '仅内部用户'],
  waterMark: ['option_water_mark', '水印'],
  autoRecord: ['auto_record', '自动录制'],
  mute: ['option_mute', '入会静音'],
  joinBeforeHost: ['option_jbh', '成员可在主持人前入会'],
  h323: ['option_h323', 'H.323 设备入会'],
  live: ['option_live', '直播'],
  interpreter: ['option_interpreter', '传译'],
};

const PROTECTED_KEYS = new Set([
  'user_token',
  'id',
  'quite',
  'duration',
  'meeting_date',
  'meeting_time',
  'topic',
  'password',
]);

const META_LINES = {
  size: (value) => `容量 ${value} 人`,
  password: () => '自定义入会密码',
  usage: (value) => `用途「${value}」`,
  groupId: (value) => `会议室组 ${value}`,
};

function toBool(name, raw) {
  const value = String(raw ?? '').toLowerCase();
  if (['1', 'true'].includes(value)) return '1';
  if (['0', 'false'].includes(value)) return '0';
  throw new MeetingPlanError(`选项 ${name} 只接受 true/false 或 1/0。`);
}

export function normalizeMeetingOptions(rawOptions = {}) {
  const overrides = {};
  const notes = [];

  if (rawOptions.size !== undefined) {
    const size = Number(rawOptions.size);
    if (!SIZE_OPTIONS.includes(size)) {
      throw new MeetingPlanError(`size 只支持 ${SIZE_OPTIONS.join('/')}。`, 'INVALID_OPTION');
    }
    overrides.size = String(size);
    notes.push(META_LINES.size(size));
  }

  if (rawOptions.groupId !== undefined) {
    if (!/^\d+$/.test(String(rawOptions.groupId))) throw new MeetingPlanError('groupId 必须是数字。', 'INVALID_OPTION');
    overrides.group_id = String(rawOptions.groupId);
    notes.push(META_LINES.groupId(rawOptions.groupId));
  }

  if (rawOptions.usage !== undefined && String(rawOptions.usage).trim() !== '') {
    const usage = String(rawOptions.usage).trim();
    if (usage.length > 20) throw new MeetingPlanError('usage 过长（≤20 字）。', 'INVALID_OPTION');
    overrides.usage = usage;
    notes.push(META_LINES.usage(usage));
  }

  if (rawOptions.password !== undefined) {
    validatePassword(String(rawOptions.password));
    overrides.password = String(rawOptions.password);
    notes.push(META_LINES.password());
  }

  for (const [name, [key, label]] of Object.entries(BOOLEAN_FIELDS)) {
    if (rawOptions[name] === undefined) continue;
    overrides[key] = toBool(label, rawOptions[name] === '' ? 'true' : rawOptions[name]);
    notes.push(`${label} ${overrides[key] === '1' ? '开' : '关'}`);
  }

  if (rawOptions.recurrence !== undefined || rawOptions.until !== undefined || rawOptions.times !== undefined) {
    applyRecurrence(overrides, notes, rawOptions);
  }

  for (const pair of rawOptions.fields ?? []) {
    applyExtraField(overrides, pair);
  }

  return { payloadOverrides: overrides, notes };
}

function applyRecurrence(overrides, notes, rawOptions) {
  const repeatType = REPEAT_TYPE_MAP[rawOptions.recurrence];
  if (!repeatType) {
    throw new MeetingPlanError('recurrence 只支持 daily/weekly/monthly。', 'INVALID_OPTION');
  }
  if (rawOptions.until === undefined && rawOptions.times === undefined) {
    throw new MeetingPlanError('周期会议需要同时提供 until（结束日期）或 times（次数）至少一项。', 'INVALID_OPTION');
  }
  if (rawOptions.until !== undefined && !/^\d{4}-\d{2}-\d{2}$/.test(String(rawOptions.until))) {
    throw new MeetingPlanError('until 必须是 YYYY-MM-DD 格式。', 'INVALID_OPTION');
  }
  if (rawOptions.times !== undefined && !/^[1-9]\d{0,2}$/.test(String(rawOptions.times))) {
    throw new MeetingPlanError('times 必须是正整数（≤999）。', 'INVALID_OPTION');
  }
  overrides.is_recurrent = '1';
  overrides.repeat_type = repeatType;
  if (rawOptions.until !== undefined) overrides.end_meeting_date = String(rawOptions.until);
  if (rawOptions.times !== undefined) overrides.end_meeting_times = String(rawOptions.times);
  const names = { daily: '每日', weekly: '每周', monthly: '每月' };
  const parts = [`周期会议（${names[rawOptions.recurrence]}）`];
  if (rawOptions.until !== undefined) parts.push(`截止 ${rawOptions.until}`);
  if (rawOptions.times !== undefined) parts.push(`共 ${rawOptions.times} 次`);
  notes.push(parts.join('，'));
}

function applyExtraField(overrides, pair) {
  const eq = String(pair).indexOf('=');
  const key = eq === -1 ? String(pair).trim() : String(pair).slice(0, eq).trim();
  const value = eq === -1 ? '' : String(pair).slice(eq + 1);
  if (!/^[a-z][a-z0-9_]*$/.test(key)) {
    throw new MeetingPlanError(`--field 键名非法：${key}（需符合 snake_case）。`, 'INVALID_OPTION');
  }
  if (PROTECTED_KEYS.has(key)) {
    throw new MeetingPlanError(`--field 不允许覆盖受控字段：${key}。`, 'PROTECTED_FIELD');
  }
  overrides[key] = value;
}

export function validatePassword(password) {
  const sixDigits = /^\d{6}$/.test(password);
  const complex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8}$/.test(password);
  if (!sixDigits && !complex) {
    throw new MeetingPlanError('密码只能是 6 位数字，或 8 位且同时包含大写字母、小写字母和数字的组合。', 'INVALID_PASSWORD');
  }
}
