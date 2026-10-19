/**
 * API client to communicate with the FastAPI backend.
 */

const API_BASE = '/api';

export async function fetchBills() {
  const res = await fetch(`${API_BASE}/bills`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch bills');
  }
  return res.json();
}

export async function fetchBillDetail(billId) {
  const res = await fetch(`${API_BASE}/bills/${billId}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to fetch bill ${billId}`);
  }
  return res.json();
}

export async function uploadBillImage(file, onProgress) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/bills/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to upload and extract bill');
  }

  return res.json();
}

export async function askBillQuestions(billId, questions) {
  // questions can be string or array of { question_id, question }
  const payload = typeof questions === 'string' 
    ? { question: questions } 
    : { questions };

  const res = await fetch(`${API_BASE}/bills/${billId}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to query bill QA engine');
  }

  return res.json();
}

export async function deleteBillRecord(billId) {
  const res = await fetch(`${API_BASE}/bills/${billId}`, {
    method: 'DELETE',
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to delete bill');
  }

  return res.json();
}

export function getBillImageUrl(billId) {
  return `${API_BASE}/bills/${billId}/image`;
}

export function getBillExportUrl(billId) {
  return `${API_BASE}/bills/${billId}/export`;
}
