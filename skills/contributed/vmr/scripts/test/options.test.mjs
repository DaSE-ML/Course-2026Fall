import assert from 'node:assert/strict';
import test from 'node:test';
import { normalizeMeetingOptions, validatePassword } from '../lib/options.mjs';
import { buildCreateMeetingPayload, normalizeMeetingDetail } from '../lib/vmr-api.mjs';

const MEETING = {
  subject: '课程讨论',
  start: '2026-09-01T14:00:00+08:00',
  durationMinutes: 60,
};

test('空选项产出空覆盖与空备注', () => {
  const { payloadOverrides, notes } = normalizeMeetingOptions({});
  assert.deepEqual(payloadOverrides, {});
  assert.deepEqual(notes, []);
});

test('size 与容量枚举校验', () => {
  const ok = normalizeMeetingOptions({ size: '300' });
  assert.equal(ok.payloadOverrides.size, '300');
  assert.match(ok.notes.join('\n'), /容量 300 人/);
  assert.throws(() => normalizeMeetingOptions({ size: '250' }), /size 只支持/);
});

test('密码规则：6 位数字或 8 位含大小写数字', () => {
  assert.equal(normalizeMeetingOptions({ password: '123456' }).payloadOverrides.password, '123456');
  assert.equal(
    normalizeMeetingOptions({ password: 'Aa123456' }).payloadOverrides.password,
    'Aa123456',
  );
  assert.throws(() => normalizeMeetingOptions({ password: 'abcdef' }), /密码只能/);
  assert.throws(() => validatePassword('Aa12'), /密码只能/);
});

test('布尔开关映射到官方字段', () => {
  const { payloadOverrides, notes } = normalizeMeetingOptions({
    waitingRoom: '',
    ssoOnly: 'true',
    waterMark: '0',
    autoRecord: 'false',
    mute: '1',
    joinBeforeHost: '0',
    h323: 'true',
    live: '',
    interpreter: '',
  });
  assert.equal(payloadOverrides.waiting_room, '1');
  assert.equal(payloadOverrides.option_sso_only, '1');
  assert.equal(payloadOverrides.option_water_mark, '0');
  assert.equal(payloadOverrides.auto_record, '0');
  assert.equal(payloadOverrides.option_mute, '1');
  assert.equal(payloadOverrides.option_jbh, '0');
  assert.equal(payloadOverrides.option_h323, '1');
  assert.equal(payloadOverrides.option_live, '1');
  assert.equal(payloadOverrides.option_interpreter, '1');
  assert.ok(notes.length >= 9);
  assert.throws(() => normalizeMeetingOptions({ waitingRoom: 'yes' }), /只接受 true\/false/);
});

test('周期会议映射 repeat_type 并要求 until/times', () => {
  const { payloadOverrides } = normalizeMeetingOptions({ recurrence: 'weekly', times: '8' });
  assert.equal(payloadOverrides.is_recurrent, '1');
  assert.equal(payloadOverrides.repeat_type, '2');
  assert.equal(payloadOverrides.end_meeting_times, '8');
  const daily = normalizeMeetingOptions({ recurrence: 'daily', until: '2026-12-31' });
  assert.equal(daily.payloadOverrides.repeat_type, '1');
  assert.equal(daily.payloadOverrides.end_meeting_date, '2026-12-31');
  assert.throws(() => normalizeMeetingOptions({ recurrence: 'yearly', until: '2026-12-31' }), /daily\/weekly\/monthly/);
  assert.throws(() => normalizeMeetingOptions({ recurrence: 'weekly' }), /until.*times/s);
});

test('--field 透传与受控字段保护', () => {
  const { payloadOverrides } = normalizeMeetingOptions({ fields: ['description=组会说明'] });
  assert.equal(payloadOverrides.description, '组会说明');
  assert.throws(() => normalizeMeetingOptions({ fields: ['user_token=evil'] }), /受控字段/);
  assert.throws(() => normalizeMeetingOptions({ fields: ['topic=x'] }), /受控字段/);
  assert.throws(() => normalizeMeetingOptions({ fields: ['bad-key=1'] }), /键名非法/);
});

test('显式 --field 不能伪造主题/时间/密码', () => {
  assert.throws(() => normalizeMeetingOptions({ fields: ['password=Aa123456'] }), /受控字段/);
});

test('详情响应规范化：提取三要素与审批状态', () => {
  const detail = normalizeMeetingDetail({
    id: 60001,
    topic: '组会',
    start_time: '2026-09-01 14:00:00',
    end_time: '2026-09-01 15:00:00',
    approve: '批准',
    is_approved: true,
    join_url: 'https://meeting.tencent.com/dm/XXXXXX',
    meeting_id: '123456789',
    meeting_code: '123456789',
    password: '881610',
    auto_record: 1,
    waiting_room: 0,
    usage: '办公',
  });
  assert.equal(detail.approvalState, 'approved');
  assert.equal(detail.link, 'https://meeting.tencent.com/dm/XXXXXX');
  assert.equal(detail.meetingId, '123456789');
  assert.equal(detail.password, '881610');
  assert.equal(detail.autoRecord, true);
});

test('详情规范化区分待审批/驳回', () => {
  assert.equal(normalizeMeetingDetail({ approve: '待审批' }).approvalState, 'pending');
  assert.equal(normalizeMeetingDetail({ approve: '驳回' }).approvalState, 'rejected');
});

test('payload 合并：默认值不变，overrides 生效，密码优先级正确', () => {
  const base = JSON.parse(JSON.stringify(buildCreateMeetingPayload(MEETING, 'TOKEN')));
  assert.equal(base.size, '100');
  assert.equal(base.usage, '办公');
  assert.equal(base.is_recurrent, '0');
  assert.match(base.password, /^\d{6}$/);

  const merged = buildCreateMeetingPayload(MEETING, 'TOKEN', {
    overrides: { size: '500', password: 'Aa123456', description: '注明设备' },
  });
  assert.equal(merged.size, '500');
  assert.equal(merged.description, '注明设备');
  assert.equal(merged.password, 'Aa123456');

  const legacy = buildCreateMeetingPayload(MEETING, 'TOKEN', '654321');
  assert.equal(legacy.password, '654321');

  const explicit = buildCreateMeetingPayload(MEETING, 'TOKEN', { password: '123456' });
  assert.equal(explicit.password, '123456');
});
