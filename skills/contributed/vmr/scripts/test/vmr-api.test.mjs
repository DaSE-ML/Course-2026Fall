import assert from 'node:assert/strict';
import test from 'node:test';
import {
  buildCreateMeetingPayload,
  buildListMeetingsForm,
  extractTokenFromPostData,
  findMatchingMeetings,
  findOverlappingMeetingViaApi,
  normalizeMeetingList,
  parseZoomInfo,
  verifyDeletionOnceViaApi,
  verifySubmittedOnceViaApi,
  waitForApprovalViaApi,
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

test('list 请求带分页与范围参数避免落入默认首页快照', () => {
  const form = buildListMeetingsForm('TOKEN_VALUE');
  assert.equal(form.user_token, 'TOKEN_VALUE');
  assert.equal(form.page_size, '200');
  assert.equal(form.page, '1');
  assert.equal(form.search, '');
  assert.ok(typeof form['date_range[0]'] === 'string' && form['date_range[0]'].length > 0);
  assert.ok(typeof form['date_range[1]'] === 'string' && form['date_range[1]'].length > 0);
  assert.equal(form.use_date_range, '0');
});

test('parseZoomInfo 解析会议号与密码并容忍格式差异', () => {
  assert.deepEqual(parseZoomInfo('会议号:987654321<br>密码:135790'), { meetingCode: '987654321', password: '135790' });
  assert.deepEqual(parseZoomInfo('会议号：987-654-321\n密码：aB12'), { meetingCode: '987-654-321', password: 'aB12' });
  assert.deepEqual(parseZoomInfo('会议号:987654321'), { meetingCode: '987654321' });
  assert.deepEqual(parseZoomInfo(null), {});
  assert.deepEqual(parseZoomInfo('审批中，详情暂不可见'), {});
});

test('waitForApprovalViaApi 轮询至批准并携带入会信息', async () => {
  const rowsByPoll = [
    [{ applicationId: '12345', subject: '课程讨论', approveStatus: '待审批', raw: {} }],
    [{ applicationId: '12345', subject: '课程讨论', approveStatus: '待审批', raw: {} }],
    [{ applicationId: '12345', subject: '课程讨论', approveStatus: '批准', raw: { zoom_info: '会议号:987654321<br>密码:135790' } }],
  ];
  let calls = 0;
  const api = { listMeetings: async () => rowsByPoll[Math.min(calls++, rowsByPoll.length - 1)] };
  const sleeps = [];
  const result = await waitForApprovalViaApi(api, '12345', {
    timeoutMs: 60_000,
    intervals: [1_000],
    sleepFn: (ms) => { sleeps.push(ms); },
    nowFn: () => 0,
  });
  assert.equal(result.status, 'approved');
  assert.equal(result.polls, 3);
  assert.deepEqual(result.joinInfo, { meetingCode: '987654321', password: '135790' });
  assert.deepEqual(sleeps, [1_000, 1_000]);
});

test('waitForApprovalViaApi 默认按 500ms→1s→2s→5s→10s 退避并封顶', async () => {
  const pending = [{ applicationId: '12345', subject: '课程讨论', approveStatus: '待审批', raw: {} }];
  const api = { listMeetings: async () => pending };
  let clock = 0;
  const sleeps = [];
  const delays = [];
  const result = await waitForApprovalViaApi(api, '12345', {
    timeoutMs: 60_000,
    sleepFn: (ms) => { sleeps.push(ms); clock += ms; },
    nowFn: () => clock,
    onPoll: (_status, _polls, delayMs) => delays.push(delayMs),
  });
  assert.equal(result.status, 'approval_timeout');
  assert.deepEqual(sleeps, [500, 1_000, 2_000, 5_000, 10_000, 10_000, 10_000, 10_000, 10_000]);
  assert.deepEqual(delays, [500, 1_000, 2_000, 5_000, 10_000, 10_000, 10_000, 10_000, 10_000, 10_000]);
});

test('waitForApprovalViaApi 超时返回当前状态、始终未出现则返回 missing', async () => {
  const pendingApi = { listMeetings: async () => [{ applicationId: '12345', subject: '课程讨论', approveStatus: '待审批', raw: {} }] };
  let clock = 0;
  const timeout = await waitForApprovalViaApi(pendingApi, '12345', {
    timeoutMs: 60_000,
    intervals: [5_000],
    sleepFn: () => { clock += 30_000; },
    nowFn: () => clock,
  });
  assert.equal(timeout.status, 'approval_timeout');
  assert.equal(timeout.record.approveStatus, '待审批');
  assert.ok(timeout.polls >= 2);

  let clock2 = 0;
  const missing = await waitForApprovalViaApi({ listMeetings: async () => [] }, '12345', {
    timeoutMs: 10_000,
    intervals: [5_000],
    sleepFn: () => { clock2 += 5_000; },
    nowFn: () => clock2,
  });
  assert.equal(missing.status, 'missing');
  assert.equal(missing.record, null);
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
