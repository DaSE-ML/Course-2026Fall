import { randomInt } from 'node:crypto';
import { postFormInPage, VMR_MEETINGS_URL, VMR_ORIGIN, bodyText } from './browser.mjs';
import { VmrPageError } from './vmr-read.mjs';

const API_BASE = `${VMR_ORIGIN}/api/v1`;
const TOKEN_TIMEOUT_MS = 15_000;

export async function createVmrApiClient(page, options = {}) {
  const token = await acquireUserToken(page, options);
  return new VmrApiClient({ page, token, passwordProvider: options.passwordProvider });
}

export class VmrApiClient {
  constructor({ page, token, passwordProvider = generatePassword }) {
    this.page = page;
    this.token = token;
    this.passwordProvider = passwordProvider;
  }

  async listMeetings() {
    const data = await postVmrForm(this.page, '/meeting/list', { user_token: this.token });
    return normalizeMeetingList(data);
  }

  async createMeeting(meeting) {
    const payload = buildCreateMeetingPayload(meeting, this.token, this.passwordProvider());
    const data = await postVmrForm(this.page, '/meeting/edit', payload);
    if (!data?.success) {
      throw new VmrPageError('会议创建接口返回失败；已停止且不会自动重试。', 'API_CREATE_REJECTED');
    }
    return data;
  }

  async deleteMeeting(applicationId) {
    const data = await postVmrForm(this.page, '/meeting/delete', {
      user_token: this.token,
      'ids[0]': String(applicationId),
    });
    if (!data?.success) {
      throw new VmrPageError(`删除接口未确认申请 ${applicationId} 删除成功；已停止且不会自动重试。`, 'API_DELETE_REJECTED');
    }
    return data;
  }
}

export async function acquireUserToken(page, options = {}) {
  const captured = await captureTokenFromMeetingListRequest(page, options);
  if (captured) return captured;
  throw new VmrPageError('无法从已登录页面动态取得会议接口令牌；未调用创建或删除接口。', 'API_TOKEN_UNAVAILABLE');
}

async function captureTokenFromMeetingListRequest(page, options = {}) {
  let captured = null;

  const handler = (request) => {
    const url = request.url() ?? '';
    if (!url.startsWith(API_BASE)) return;
    const token = extractTokenFromPostData(request.postData() ?? '');
    if (token) captured = token;
  };
  page.on('request', handler);

  try {
    await page.goto(VMR_MEETINGS_URL, { waitUntil: 'domcontentloaded', timeout: 30_000 });
    await page.reload({ waitUntil: 'domcontentloaded', timeout: 30_000 }).catch(() => undefined);

    const started = Date.now();
    while (!captured && Date.now() - started < (options.tokenTimeoutMs ?? TOKEN_TIMEOUT_MS)) {
      await page.waitForTimeout(250);
      const text = await bodyText(page);
      if (/您好,/.test(text) && text.includes('会议列表') && !captured) {
        await page.waitForTimeout(1_000);
      }
    }
  } finally {
    page.off('request', handler);
  }

  return captured;
}

export function extractTokenFromPostData(postData) {
  const params = new URLSearchParams(postData);
  return params.get('user_token');
}

export function buildCreateMeetingPayload(meeting, userToken, password) {
  return {
    user_token: userToken,
    duration: String(meeting.durationMinutes),
    meeting_date: datePart(meeting.start),
    meeting_time: timePart(meeting.start),
    option_mute: '1',
    option_jbh: '1',
    option_h323: '0',
    group_id: '2',
    usage: '办公',
    is_recurrent: '0',
    recurrent_id: '0',
    end_meeting_date: datePart(meeting.start),
    end_meeting_times: '2',
    repeat_type: '2',
    size: '100',
    auto_record: '0',
    assistant: '',
    option_enroll: '0',
    enroll_attendees: '',
    option_water_mark: '0',
    option_sso_only: '0',
    meeting_guests: '',
    waiting_room: '0',
    option_interpreter: '0',
    id: '0',
    quite: 'true',
    password,
    option_live: '0',
    topic: meeting.subject,
    attendees: '[]',
    ask: '1',
  };
}

export function normalizeMeetingList(response) {
  const rows = findArray(response?.data) ?? findArray(response) ?? [];
  return rows.map(normalizeMeetingRecord).filter((record) => record.applicationId && record.subject);
}

export function normalizeMeetingRecord(row) {
  return {
    applicationId: String(row.id ?? row.application_id ?? row.applicationId ?? ''),
    subject: String(row.topic ?? row.subject ?? ''),
    startTime: String(row.start_time ?? row.startTime ?? ''),
    durationText: String(row.duration_hour ?? row.duration ?? ''),
    approveStatus: stripHtml(String(row.approve_status ?? row.approveStatus ?? row.status ?? '')),
    raw: row,
  };
}

export function findMatchingMeetings(records, meeting) {
  const expectedDate = datePart(meeting.start);
  const expectedTime = timePart(meeting.start);
  return records.filter((record) => (
    subjectMatches(record.subject, meeting.subject)
    && record.startTime.includes(expectedDate)
    && record.startTime.includes(expectedTime)
  ));
}

function subjectMatches(recordSubject, plannedSubject) {
  return recordSubject === plannedSubject
    || plannedSubject.startsWith(recordSubject)
    || recordSubject.startsWith(plannedSubject);
}

export async function findOverlappingMeetingViaApi(api, meeting) {
  const matches = findMatchingMeetings(await api.listMeetings(), meeting);
  if (!matches.length) return null;
  return {
    subject: meeting.subject,
    applicationId: matches[0].applicationId,
    reason: '会议列表接口中发现同主题、同开始时间的申请。',
  };
}

export async function verifySubmittedOnceViaApi(api, meeting) {
  const matches = findMatchingMeetings(await api.listMeetings(), meeting);
  return matches.length > 0
    ? { subject: meeting.subject, status: 'submitted_pending_approval', applicationId: matches[0].applicationId }
    : { subject: meeting.subject, status: 'submission_unknown', detail: '创建接口返回后一次列表核验未找到对应申请' };
}

export async function verifyDeletionOnceViaApi(api, applicationId) {
  const remaining = (await api.listMeetings()).filter((record) => record.applicationId === String(applicationId));
  if (remaining.length === 0) {
    return { applicationId: String(applicationId), status: 'deletion_confirmed' };
  }
  return {
    applicationId: String(applicationId),
    status: 'deletion_unknown',
    detail: '删除接口返回后一次列表核验仍找到该申请；未重试删除。',
  };
}

async function postVmrForm(page, path, form) {
  const response = await postFormInPage(page, `${API_BASE}${path}`, form);
  const { text } = response;
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    throw new VmrPageError(`会议接口 ${path} 返回非 JSON 内容；已停止。`, 'API_BAD_RESPONSE');
  }
  if (!response.ok) {
    throw new VmrPageError(`会议接口 ${path} 返回 HTTP ${response.status}；已停止。`, 'API_HTTP_ERROR');
  }
  return data;
}

function findArray(value) {
  if (Array.isArray(value)) return value;
  if (!value || typeof value !== 'object') return null;
  for (const child of Object.values(value)) {
    const found = findArray(child);
    if (found) return found;
  }
  return null;
}

function stripHtml(value) {
  return value.replace(/<[^>]*>/gu, '').trim();
}

function generatePassword() {
  return String(randomInt(0, 1_000_000)).padStart(6, '0');
}

function datePart(value) {
  return value.slice(0, 10);
}

function timePart(value) {
  return value.slice(11, 16);
}
