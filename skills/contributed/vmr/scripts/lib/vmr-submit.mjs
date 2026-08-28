import { withMeetingPage } from './browser.mjs';
import { ensureAuthenticated } from './sso.mjs';
import {
  createVmrApiClient,
  findOverlappingMeetingViaApi,
  verifySubmittedOnceViaApi,
  verifyDeletionOnceViaApi,
  waitForApprovalViaApi,
  APPROVAL_POLL_INTERVALS_MS,
} from './vmr-api.mjs';
import { VmrPageError } from './vmr-read.mjs';

export async function bookMeetings(plan, options = {}) {
  return withMeetingPage(async (page) => {
    await ensureAuthenticated(page);
    const api = await createVmrApiClient(page);
    const results = [];

    for (const meeting of plan.meetings) {
      const existing = await findOverlappingMeetingViaApi(api, meeting);
      if (existing && !options.allowDuplicate) {
        console.log(`提示：发现同主题同开始时间的已有申请（申请 ${existing.applicationId}），仍继续提交；如不需要请稍后 delete。`);
      }

      await api.createMeeting(meeting, { payloadOverrides: plan.options?.payloadOverrides });
      results.push(await verifySubmittedOnceViaApi(api, meeting));
      if (results.at(-1).status !== 'submitted_pending_approval') break;
    }

    for (const result of results) {
      console.log(`${result.subject}：${result.status}${result.applicationId ? `（申请 ${result.applicationId}）` : ''}${result.detail ? `（${result.detail}）` : ''}`);
    }
    return results;
  }, options);
}

export async function listMeetings(options = {}) {
  return withMeetingPage(async (page) => {
    await ensureAuthenticated(page);
    const api = await createVmrApiClient(page);
    return api.listMeetings();
  }, options);
}

export async function fetchMeetingDetails(applicationId, options = {}) {
  return withMeetingPage(async (page) => {
    await ensureAuthenticated(page);
    const api = await createVmrApiClient(page);
    const detail = await api.getMeeting(applicationId);
    if (detail.approvalState === 'pending') {
      throw new VmrPageError(`申请 ${detail.applicationId} 尚未批准，暂无入会信息。`, 'PENDING_APPROVAL');
    }
    if (detail.approvalState === 'rejected') {
      throw new VmrPageError(`申请 ${detail.applicationId} 已被驳回，无入会信息。`, 'APPLICATION_REJECTED');
    }
    if (!detail.link || !detail.meetingId || !detail.password) {
      throw new VmrPageError(
        `申请 ${detail.applicationId} 详情缺少入会三要素（链接/会议号/密码），请人工查看详情页。`,
        'DETAILS_UNAVAILABLE',
      );
    }
    return detail;
  }, options);
}

export async function waitForApproval(applicationId, options = {}) {
  if (!applicationId || !/^\d+$/.test(String(applicationId))) {
    throw new VmrPageError('wait 需要数字申请编号：--id <applicationId>（可用 status 查看）。', 'WAIT_ID_REQUIRED');
  }
  return withMeetingPage(async (page) => {
    await ensureAuthenticated(page);
    const api = await createVmrApiClient(page);
    let lastStatus;
    const result = await waitForApprovalViaApi(api, applicationId, {
      timeoutMs: options.timeoutMs,
      intervals: options.intervals,
      onPoll: (status, polls, delayMs) => {
        if (status !== lastStatus) {
          console.log(`当前状态：${status || '未知'}，继续等待…（500ms→1s→2s→5s→10s 退避轮询）`);
          lastStatus = status;
        } else if (polls - 1 === APPROVAL_POLL_INTERVALS_MS.length) {
          console.log(`已退避至 ${delayMs / 1000}s 间隔，继续等待…`);
        }
      },
    });
    if (result.status === 'approved') {
      const { meetingCode, password } = result.joinInfo;
      console.log(`申请 ${result.applicationId}：approved${meetingCode ? `（会议号 ${meetingCode}${password ? `，密码 ${password}` : ''}）` : '（未解析到会议号/密码）'}`);
    } else if (result.status === 'approval_timeout') {
      console.log(`申请 ${result.applicationId}：approval_timeout（当前状态：${result.record?.approveStatus || '未知'}）`);
    } else {
      console.log(`申请 ${result.applicationId}：missing（会议列表中未找到该申请）`);
    }
    if (result.status !== 'approved') process.exitCode = 1;
    return result;
  }, options);
}

export async function deleteMeetingById(applicationId, options = {}) {
  if (!applicationId || !/^\d+$/.test(String(applicationId))) {
    throw new VmrPageError('delete 需要数字申请编号：--id <applicationId>（可用 status 查看）。', 'DELETE_ID_REQUIRED');
  }
  return withMeetingPage(async (page) => {
    await ensureAuthenticated(page);
    const api = await createVmrApiClient(page);
    await api.deleteMeeting(applicationId);
    const result = await verifyDeletionOnceViaApi(api, applicationId);
    console.log(`申请 ${result.applicationId}：${result.status}${result.detail ? `（${result.detail}）` : ''}`);
    return result;
  }, options);
}
