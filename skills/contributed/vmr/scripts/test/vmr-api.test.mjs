import assert from 'node:assert/strict';
import test from 'node:test';
import {
  buildCreateMeetingPayload,
  extractTokenFromPostData,
  findMatchingMeetings,
  findOverlappingMeetingViaApi,
  normalizeMeetingList,
  verifyDeletionOnceViaApi,
  verifySubmittedOnceViaApi,
} from '../lib/vmr-api.mjs';
import { createMeetingPlan } from '../lib/plan.mjs';
import { VmrPageError } from '../lib/vmr-read.mjs';

const NOW = new Date('2026-07-22T00:00:00+08:00');

function testMeeting(overrides = {}) {
  const plan = createMeetingPlan({
    subject: '课程讨论',
    start: '2026-07-23T16:00:00+08:00',
    end: '2026-07-23T16:30:00+08:00',
    timeZone: 'Asia/Shanghai',
    ...overrides,
  }, NOW);
  return plan.meetings[0];
}

function apiWithRows(rows) {
  return { listMeetings: async () => rows };
}

test('从接口 POST body 中提取 user_token 且不依赖其他字段', () => {
  assert.equal(extractTokenFromPostData('foo=bar&user_token=abc123TOKEN_xyz&topic=x'), 'abc123TOKEN_xyz');
  assert.equal(extractTokenFromPostData('foo=bar'), null);
});

test('创建会议 payload 使用计划时间、时长和默认会议选项', () => {
  const payload = buildCreateMeetingPayload(testMeeting(), 'TOKEN_VALUE', '123456');
  assert.equal(payload.user_token, 'TOKEN_VALUE');
  assert.equal(payload.duration, '30');
  assert.equal(payload.meeting_date, '2026-07-23');
  assert.equal(payload.meeting_time, '16:00');
  assert.equal(payload.topic, '课程讨论');
  assert.equal(payload.password, '123456');
  assert.equal(payload.group_id, '2');
  assert.equal(payload.usage, '办公');
  assert.equal(payload.ask, '1');
  assert.equal(payload.attendees, '[]');
});

test('规范化会议列表兼容嵌套 data rows 结构', () => {
  const records = normalizeMeetingList({
    success: true,
    data: {
      rows: [{
        id: 10001,
        start_time: '2026-07-23 16:00',
        duration_hour: '30分钟',
        topic: '课程讨论',
        approve_status: "<span class='text-cyan'>批准</span>",
      }],
    },
  });
  assert.deepEqual(records, [{
    applicationId: '10001',
    subject: '课程讨论',
    startTime: '2026-07-23 16:00',
    durationText: '30分钟',
    approveStatus: '批准',
    raw: {
      id: 10001,
      start_time: '2026-07-23 16:00',
      duration_hour: '30分钟',
      topic: '课程讨论',
      approve_status: "<span class='text-cyan'>批准</span>",
    },
  }]);
});

test('结构化匹配要求同主题和同开始时间', () => {
  const meeting = testMeeting();
  const rows = [
    { applicationId: '1', subject: '课程讨论', startTime: '2026-07-23 16:00' },
    { applicationId: '2', subject: '课程讨论', startTime: '2026-07-23 17:00' },
    { applicationId: '3', subject: '其他会议', startTime: '2026-07-23 16:00' },
  ];
  assert.deepEqual(findMatchingMeetings(rows, meeting).map((row) => row.applicationId), ['1']);
});

test('重复检查通过接口返回同主题同开始时间提示', async () => {
  const existing = await findOverlappingMeetingViaApi(apiWithRows([
    { applicationId: '1', subject: '课程讨论', startTime: '2026-07-23 16:00' },
  ]), testMeeting());
  assert.equal(existing.applicationId, '1');
  assert.match(existing.reason, /同主题、同开始时间/);
});

test('提交后一次接口核验返回申请编号或 unknown', async () => {
  assert.deepEqual(
    await verifySubmittedOnceViaApi(apiWithRows([
      { applicationId: '1', subject: '课程讨论', startTime: '2026-07-23 16:00' },
    ]), testMeeting()),
    { subject: '课程讨论', status: 'submitted_pending_approval', applicationId: '1' }
  );

  assert.deepEqual(
    await verifySubmittedOnceViaApi(apiWithRows([]), testMeeting()),
    { subject: '课程讨论', status: 'submission_unknown', detail: '创建接口返回后一次列表核验未找到对应申请' }
  );
});

test('删除后一次接口核验确认申请编号消失', async () => {
  const target = { applicationId: '1', subject: '测试申请' };
  assert.deepEqual(await verifyDeletionOnceViaApi(apiWithRows([]), target.applicationId), {
    applicationId: '1',
    status: 'deletion_confirmed',
  });
  assert.deepEqual(await verifyDeletionOnceViaApi(apiWithRows([target]), target.applicationId), {
    applicationId: '1',
    status: 'deletion_unknown',
    detail: '删除接口返回后一次列表核验仍找到该申请；未重试删除。',
  });
});
