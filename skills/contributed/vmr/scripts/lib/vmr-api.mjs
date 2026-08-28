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
    const data = await postVmrForm(this.page, '/meeting/list', buildListMeetingsForm(this.token));
    return normalizeMeetingList(data);
  }

  async getMeeting(applicationId) {
    const id = String(applicationId ?? '').trim();
    if (!/^\d+$/.test(id)) {
      throw new VmrPageError('details 需要数字申请编号：--id <applicationId>（可用 status 查看）。', 'DETAILS_ID_REQUIRED');
    }
    const data = await postVmrForm(this.page, '/meeting/get', {
      user_token: this.token,
      id,
      review: 'true',
    });
    if (!data?.success || !data?.data) {
      throw new VmrPageError(`会议详情接口未返回申请 ${id} 的数据；已停止。`, 'API_GET_REJECTED');
    }
    return normalizeMeetingDetail(data.data);
  }

  async createMeeting(meeting, options = {}) {
    const payload = buildCreateMeetingPayload(meeting, this.token, {
      generatePassword: this.passwordProvider,
      ...options,
    });
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

export function buildCreateMeetingPayload(meeting, userToken, opts = {}) {
  const normalized = typeof opts === 'string' ? { password: opts } : (opts ?? {});
  const overrides = normalized.overrides ?? {};
  const fallbackPassword = typeof normalized.generatePassword === 'function'
    ? normalized.generatePassword()
    : generatePassword();
  const payload = { ...baseCreateMeetingPayload(meeting, userToken), ...overrides };
  payload.password = overrides.password ?? normalized.password ?? fallbackPassword;
  return payload;
}

function baseCreateMeetingPayload(meeting, userToken) {
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
    password: '',
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

export function normalizeMeetingDetail(data) {
  const approve = stripHtml(String(data?.approve ?? data?.approve_status ?? ''));
  let state = 'unknown';
  if (/待审批|审批中/.test(approve)) state = 'pending';
  else if (/驳回|拒绝|不通过/.test(approve)) state = 'rejected';
  else if (approve.includes('批准')) state = 'approved';

  return {
    applicationId: String(data?.id ?? ''),
    subject: String(data?.topic ?? ''),
    startTime: String(data?.start_time ?? ''),
    endTime: String(data?.end_time ?? ''),
    approvalState: state,
    approveStatus: approve,
    link: data?.join_url ? String(data.join_url) : '',
    meetingId: String(data?.meeting_id ?? data?.meeting_code ?? ''),
    password: data?.password == null ? '' : String(data.password),
    hostUrl: data?.host_url ? String(data.host_url) : '',
    autoRecord: Boolean(data?.auto_record),
    waitingRoom: Boolean(data?.waiting_room),
    usage: String(data?.usage ?? ''),
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

export function buildListMeetingsForm(userToken) {
  return {
    user_token: userToken,
    search: '',
    page_size: '200',
    page: '1',
    'date_range[0]': '2025-01-01 00:00',
    'date_range[1]': '2035-12-31 23:59',
    use_date_range: '0',
  };
}

export function parseZoomInfo(value) {
  const text = String(value ?? '').replace(/<br\s*\/?>/giu, '\n');
  const meetingCode = text.match(/会议号[:：]\s*([0-9-]+)/u)?.[1];
  const password = text.match(/密码[:：]\s*([0-9A-Za-z]+)/u)?.[1];
  const joinInfo = {};
  if (meetingCode) joinInfo.meetingCode = meetingCode;
  if (password) joinInfo.password = password;
  return joinInfo;
}

export function isApprovedStatus(status) {
  return String(status ?? '').includes('批准');
}

export const APPROVAL_POLL_INTERVALS_MS = [500, 1_000, 2_000, 5_000, 10_000];

export async function waitForApprovalViaApi(api, applicationId, options = {}) {
  const timeoutMs = options.timeoutMs ?? 120_000;
  const intervals = options.intervals ?? APPROVAL_POLL_INTERVALS_MS;
  const sleep = options.sleepFn ?? ((ms) => new Promise((resolve) => setTimeout(resolve, ms)));
  const now = options.nowFn ?? Date.now;
  const deadline = now() + timeoutMs;
  let last = null;
  let polls = 0;

  while (true) {
    polls += 1;
    const records = await api.listMeetings();
    last = records.find((record) => record.applicationId === String(applicationId)) ?? null;
    if (last && isApprovedStatus(last.approveStatus)) {
      return { applicationId: String(applicationId), status: 'approved', record: last, joinInfo: parseZoomInfo(last.raw?.zoom_info), polls };
    }
    const delayMs = intervals[Math.min(polls - 1, intervals.length - 1)];
    if (options.onPoll) options.onPoll(last?.approveStatus ?? null, polls, delayMs);
    if (now() + delayMs > deadline) break;
    await sleep(delayMs);
  }

  return {
    applicationId: String(applicationId),
    status: last ? 'approval_timeout' : 'missing',
    record: last,
    polls,
  };
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
