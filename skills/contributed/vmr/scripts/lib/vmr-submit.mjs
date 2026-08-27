import { withMeetingPage } from './browser.mjs';
import { ensureAuthenticated } from './sso.mjs';
import { createVmrApiClient, findOverlappingMeetingViaApi, verifySubmittedOnceViaApi, verifyDeletionOnceViaApi } from './vmr-api.mjs';
import { fetchMeetingDetailsViaPage } from './calendar.mjs';
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
    return fetchMeetingDetailsViaPage(page, applicationId);
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
