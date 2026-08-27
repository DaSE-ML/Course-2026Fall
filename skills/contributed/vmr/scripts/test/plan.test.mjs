import assert from 'node:assert/strict';
import test from 'node:test';
import { createMeetingPlan } from '../lib/plan.mjs';
import { MeetingPlanError } from '../lib/request.mjs';

const NOW = new Date('2026-07-22T00:00:00+08:00');

function plan(overrides = {}) {
  return createMeetingPlan({
    subject: '课程讨论',
    start: '2026-08-01T14:10:00+08:00',
    end: '2026-08-01T15:05:00+08:00',
    timeZone: 'Asia/Shanghai',
    ...overrides,
  }, NOW);
}

test('保持开始时间并将结束时间向上取整到半小时', () => {
  const result = plan();
  assert.equal(result.start, '2026-08-01T14:10:00+08:00');
  assert.equal(result.effectiveEnd, '2026-08-01T15:10:00+08:00');
  assert.equal(result.meetings[0].durationMinutes, 60);
});

test('超过六小时会连续拆分并增加标题序号', () => {
  const result = plan({ end: '2026-08-01T21:01:00+08:00' });
  assert.equal(result.meetings.length, 2);
  assert.deepEqual(result.meetings.map(({ subject, durationMinutes }) => ({ subject, durationMinutes })), [
    { subject: '课程讨论（1/2）', durationMinutes: 360 },
    { subject: '课程讨论（2/2）', durationMinutes: 60 },
  ]);
});

test('相同请求产生稳定指纹，不同请求产生新指纹', () => {
  assert.equal(plan().fingerprint, plan().fingerprint);
  assert.notEqual(plan().fingerprint, plan({ subject: '不同主题' }).fingerprint);
});

test('拒绝过去开始时间、无主题、非上海时区和反向时间', () => {
  assert.throws(() => plan({ start: '2026-07-21T14:00:00+08:00' }), MeetingPlanError);
  assert.throws(() => plan({ subject: '  ' }), MeetingPlanError);
  assert.throws(() => createMeetingPlan({ subject: '课程讨论', start: '2026-08-01T14:00:00+00:00', end: '2026-08-01T15:00:00+00:00', timeZone: 'Asia/Shanghai' }, NOW), MeetingPlanError);
  assert.throws(() => plan({ end: '2026-08-01T14:00:00+08:00' }), MeetingPlanError);
});
