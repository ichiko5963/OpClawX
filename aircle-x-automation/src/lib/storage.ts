import { DraftPost, XPost, MonitoredKeyword } from '@/types';

const DRAFTS_KEY = 'aircle_drafts';
const LAST_CHECKED_KEY = 'aircle_last_checked';
const MONITORED_ACCOUNTS_KEY = 'aircle_monitored_accounts';

// Draft Posts
export function saveDraft(draft: DraftPost): void {
  const drafts = getDrafts();
  const existingIndex = drafts.findIndex(d => d.id === draft.id);
  
  if (existingIndex >= 0) {
    drafts[existingIndex] = { ...draft, updatedAt: new Date().toISOString() };
  } else {
    drafts.push(draft);
  }
  
  localStorage.setItem(DRAFTS_KEY, JSON.stringify(drafts));
}

export function getDrafts(): DraftPost[] {
  if (typeof window === 'undefined') return [];
  const data = localStorage.getItem(DRAFTS_KEY);
  return data ? JSON.parse(data) : [];
}

export function getDraftById(id: string): DraftPost | null {
  const drafts = getDrafts();
  return drafts.find(d => d.id === id) || null;
}

export function updateDraftStatus(
  id: string, 
  status: DraftPost['status'], 
  xPostId?: string
): void {
  const drafts = getDrafts();
  const draft = drafts.find(d => d.id === id);
  if (draft) {
    draft.status = status;
    draft.updatedAt = new Date().toISOString();
    if (status === 'posted') {
      draft.postedAt = new Date().toISOString();
    }
    if (xPostId) {
      draft.xPostId = xPostId;
    }
    localStorage.setItem(DRAFTS_KEY, JSON.stringify(drafts));
  }
}

export function deleteDraft(id: string): void {
  const drafts = getDrafts().filter(d => d.id !== id);
  localStorage.setItem(DRAFTS_KEY, JSON.stringify(drafts));
}

export function archiveOldDrafts(days: number = 7): void {
  const drafts = getDrafts();
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);
  
  const updatedDrafts = drafts.map(d => {
    if (new Date(d.createdAt) < cutoffDate && d.status === 'draft') {
      return { ...d, status: 'archived' as const, updatedAt: new Date().toISOString() };
    }
    return d;
  });
  
  localStorage.setItem(DRAFTS_KEY, JSON.stringify(updatedDrafts));
}

// Monitored Accounts State
interface MonitoredAccountState {
  username: string;
  lastTweetId: string | null;
  lastCheckedAt: string;
}

export function getMonitoredAccountsState(): MonitoredAccountState[] {
  if (typeof window === 'undefined') return [];
  const data = localStorage.getItem(MONITORED_ACCOUNTS_KEY);
  return data ? JSON.parse(data) : [];
}

export function updateMonitoredAccountState(
  username: string, 
  lastTweetId: string
): void {
  const states = getMonitoredAccountsState();
  const existingIndex = states.findIndex(s => s.username === username);
  
  const state: MonitoredAccountState = {
    username,
    lastTweetId,
    lastCheckedAt: new Date().toISOString(),
  };
  
  if (existingIndex >= 0) {
    states[existingIndex] = state;
  } else {
    states.push(state);
  }
  
  localStorage.setItem(MONITORED_ACCOUNTS_KEY, JSON.stringify(states));
}

// Last checked timestamps
export function getLastChecked(type: 'bookmarks' | 'keywords'): string | null {
  if (typeof window === 'undefined') return null;
  const data = localStorage.getItem(`${LAST_CHECKED_KEY}_${type}`);
  return data || null;
}

export function setLastChecked(type: 'bookmarks' | 'keywords'): void {
  localStorage.setItem(`${LAST_CHECKED_KEY}_${type}`, new Date().toISOString());
}

// Export/Import
export function exportData(): string {
  const data = {
    drafts: getDrafts(),
    lastChecked: {
      bookmarks: getLastChecked('bookmarks'),
      keywords: getLastChecked('keywords'),
    },
    exportedAt: new Date().toISOString(),
  };
  return JSON.stringify(data, null, 2);
}

export function importData(json: string): { success: boolean; message: string } {
  try {
    const data = JSON.parse(json);
    if (data.drafts) {
      localStorage.setItem(DRAFTS_KEY, JSON.stringify(data.drafts));
    }
    return { success: true, message: 'データをインポートしました' };
  } catch (error) {
    return { success: false, message: 'データのインポートに失敗しました' };
  }
}

// Stats
export function getStats() {
  const drafts = getDrafts();
  return {
    total: drafts.length,
    posted: drafts.filter(d => d.status === 'posted').length,
    scheduled: drafts.filter(d => d.status === 'scheduled').length,
    draft: drafts.filter(d => d.status === 'draft').length,
    archived: drafts.filter(d => d.status === 'archived').length,
  };
}
