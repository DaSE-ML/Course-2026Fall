import { withMeetingPage } from './browser.mjs';
import { ensureAuthenticated } from './sso.mjs';
import {
  createVmrApiClient,
  findOverlappingMeetingViaApi,
  verifySubmittedOnceViaApi,
  verifyDeletionOnceViaApi,
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
