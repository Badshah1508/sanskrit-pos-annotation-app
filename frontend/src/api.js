import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Create an Axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Attach JWT token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Realistic mock data for Phase 2 frontend testing
const MOCK_DATA = {
  stats: {
    total_sentences: 150,
    pending_sentences: 120,
    in_progress_sentences: 15,
    verified_sentences: 15,
    total_tokens: 2450,
    completion_percentage: 10.0,
    expert_verified: 15
  },
  sentences: [
    {
      id: 1,
      doc_id: 'news_art_001',
      sentence_id: 1,
      annotation_id: 'news_art_001_1',
      sentence_text: 'प्रधानमन्त्री नरेन्द्रमोदी अद्य नवदेहल्यां नूतनं सङ्ग्रहालयम् उद्घाटितवान् ।',
      status: 'pending',
      annotation_note: '',
      verified_by: null,
      tokens: [
        { id: 101, token_id: 1, token: 'प्रधानमन्त्री', lemma: 'प्रधानमन्त्रिन्', upos: 'NOUN', stanza_upos: 'NOUN', xpos: '_', feats: 'Case=Nom|Number=Sing', gold_sanskrit_tag: '' },
        { id: 102, token_id: 2, token: 'नरेन्द्रमोदी', lemma: 'नरेन्द्रमोदिन्', upos: 'PROPN', stanza_upos: 'PROPN', xpos: '_', feats: 'Case=Nom|Number=Sing', gold_sanskrit_tag: '' },
        { id: 103, token_id: 3, token: 'अद्य', lemma: 'अद्य', upos: 'ADV', stanza_upos: 'ADV', xpos: '_', feats: '_', gold_sanskrit_tag: '' },
        { id: 104, token_id: 4, token: 'नवदेहल्याम्', lemma: 'नवदेहली', upos: 'PROPN', stanza_upos: 'PROPN', xpos: '_', feats: 'Case=Loc|Number=Sing', gold_sanskrit_tag: '' },
        { id: 105, token_id: 5, token: 'नूतनम्', lemma: 'नूतन', upos: 'ADJ', stanza_upos: 'ADJ', xpos: '_', feats: 'Case=Acc|Gender=Masc|Number=Sing', gold_sanskrit_tag: '' },
        { id: 106, token_id: 6, token: 'सङ्ग्रहालयम्', lemma: 'सङ्ग्रहालय', upos: 'NOUN', stanza_upos: 'NOUN', xpos: '_', feats: 'Case=Acc|Gender=Masc|Number=Sing', gold_sanskrit_tag: '' },
        { id: 107, token_id: 7, token: 'उद्घाटितवान्', lemma: 'उद्-घट्', upos: 'VERB', stanza_upos: 'VERB', xpos: '_', feats: 'Aspect=Perf|VerbForm=Part', gold_sanskrit_tag: '' },
        { id: 108, token_id: 8, token: '।', lemma: '।', upos: 'PUNCT', stanza_upos: 'PUNCT', xpos: '_', feats: '_', gold_sanskrit_tag: 'AVN' }
      ]
    },
    {
      id: 2,
      doc_id: 'news_art_001',
      sentence_id: 2,
      annotation_id: 'news_art_001_2',
      sentence_text: 'संस्कृतभाषा भारतस्य प्राचीनतमा समृद्धा च भाषा अस्ति ।',
      status: 'pending',
      annotation_note: '',
      verified_by: null,
      tokens: [
        { id: 201, token_id: 1, token: 'संस्कृतभाषा', lemma: 'संस्कृतभाषा', upos: 'NOUN', stanza_upos: 'NOUN', xpos: '_', feats: 'Case=Nom|Number=Sing', gold_sanskrit_tag: '' },
        { id: 202, token_id: 2, token: 'भारतस्य', lemma: 'भारत', upos: 'PROPN', stanza_upos: 'PROPN', xpos: '_', feats: 'Case=Gen|Number=Sing', gold_sanskrit_tag: '' },
        { id: 203, token_id: 3, token: 'प्राचीनतमा', lemma: 'प्राचीनतम', upos: 'ADJ', stanza_upos: 'ADJ', xpos: '_', feats: 'Case=Nom|Degree=Sup|Gender=Fem', gold_sanskrit_tag: '' },
        { id: 204, token_id: 4, token: 'समृद्धा', lemma: 'समृद्ध', upos: 'ADJ', stanza_upos: 'ADJ', xpos: '_', feats: 'Case=Nom|Gender=Fem', gold_sanskrit_tag: '' },
        { id: 205, token_id: 5, token: 'च', lemma: 'च', upos: 'CCONJ', stanza_upos: 'CCONJ', xpos: '_', feats: '_', gold_sanskrit_tag: '' },
        { id: 206, token_id: 6, token: 'भाषा', lemma: 'भाषा', upos: 'NOUN', stanza_upos: 'NOUN', xpos: '_', feats: 'Case=Nom|Gender=Fem|Number=Sing', gold_sanskrit_tag: '' },
        { id: 207, token_id: 7, token: 'अस्ति', lemma: 'अस्', upos: 'VERB', stanza_upos: 'VERB', xpos: '_', feats: 'Mood=Ind|Person=3|Tense=Pres', gold_sanskrit_tag: '' },
        { id: 208, token_id: 8, token: '।', lemma: '।', upos: 'PUNCT', stanza_upos: 'PUNCT', xpos: '_', feats: '_', gold_sanskrit_tag: 'AVN' }
      ]
    }
  ]
};

// Check if we should use Mock mode (defaults to false now that FastAPI backend is live)
let useMock = localStorage.getItem('USE_MOCK_API') === 'true';

export const setMockMode = (enabled) => {
  useMock = enabled;
  localStorage.setItem('USE_MOCK_API', enabled ? 'true' : 'false');
};

export const getMockMode = () => useMock;

// API functions with seamless mock fallback
export const authApi = {
  login: async (username, password) => {
    if (useMock) {
      await new Promise((r) => setTimeout(r, 400));
      if (password === 'error') {
        throw new Error('Invalid credentials');
      }
      const user = {
        id: 1,
        username: username || 'sanskrit_scholar',
        email: `${username || 'scholar'}@example.ac.in`,
        role: username.toLowerCase().includes('admin') ? 'admin' : 'expert'
      };
      localStorage.setItem('token', 'mock_jwt_token_12345');
      localStorage.setItem('user', JSON.stringify(user));
      return { token: 'mock_jwt_token_12345', user };
    }
    const response = await apiClient.post('/auth/login', { username, password });
    if (response.data?.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return { token: response.data.access_token, user: response.data.user };
  },

  getCurrentUser: async () => {
    if (useMock) {
      const userJson = localStorage.getItem('user');
      return userJson ? JSON.parse(userJson) : null;
    }
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};

export const WORKSPACE_BOUNDS = {
  user1: { num: 1, label: 'User 1', start: 1, end: 1000, docs: 1000, sentences: 2658, firstPendingId: '1_0' },
  user2: { num: 2, label: 'User 2', start: 1001, end: 2000, docs: 1000, sentences: 2029, firstPendingId: '1001_0' },
  user3: { num: 3, label: 'User 3', start: 2001, end: 3000, docs: 1000, sentences: 1611, firstPendingId: '2001_0' },
  user4: { num: 4, label: 'User 4', start: 3001, end: 4000, docs: 597, sentences: 702, firstPendingId: '3001_0' },
  user5: { num: 5, label: 'User 5', start: 4001, end: 5000, docs: 0, sentences: 0, firstPendingId: null },
  user6: { num: 6, label: 'User 6', start: 5001, end: 6000, docs: 0, sentences: 0, firstPendingId: null },
  user7: { num: 7, label: 'User 7', start: 6001, end: 7000, docs: 0, sentences: 0, firstPendingId: null }
};

export const datasetApi = {
  getWorkspaces: async () => {
    if (useMock) {
      return Object.values(WORKSPACE_BOUNDS).map(w => ({
        id: w.num,
        key: `user${w.num}`,
        label: w.label,
        username: `user${w.num}`,
        range_label: `doc_id ${w.start.toLocaleString()}–${w.end.toLocaleString()}`,
        range_start: w.start,
        range_end: w.end,
        total_documents: w.docs,
        total_sentences: w.sentences
      }));
    }
    try {
      const response = await apiClient.get('/dataset/workspaces');
      return response.data;
    } catch (e) {
      // Resilient fallback if backend has not deployed /workspaces route yet
      return Object.values(WORKSPACE_BOUNDS).map(w => ({
        id: w.num,
        key: `user${w.num}`,
        label: w.label,
        username: `user${w.num}`,
        range_label: `doc_id ${w.start.toLocaleString()}–${w.end.toLocaleString()}`,
        range_start: w.start,
        range_end: w.end,
        total_documents: w.docs,
        total_sentences: w.sentences
      }));
    }
  },

  getStats: async (workspace) => {
    if (useMock) {
      await new Promise((r) => setTimeout(r, 100));
      return {
        ...MOCK_DATA.stats,
        total_sentences: workspace ? 1000 : MOCK_DATA.stats.total_sentences,
        workspace_label: workspace ? `User ${workspace.replace('user', '')}` : 'All Workspaces',
        assigned_range: workspace ? 'Assigned 1,000 sentences' : '1–7,000'
      };
    }

    const cleanWs = (workspace || 'all').toLowerCase().replace(/[\s_]/g, '');
    const wsRange = WORKSPACE_BOUNDS[cleanWs];

    try {
      const response = await apiClient.get('/dataset/stats', {
        params: workspace ? { workspace } : {}
      });
      const data = response.data;

      // If backend returned valid per-workspace stats with total_documents populated
      if (wsRange && data.total_documents !== undefined && data.total_documents !== null && data.total_documents <= wsRange.docs) {
        return data;
      }

      // If cloud backend returned global 7000 stats instead of per-workspace stats
      if (wsRange && cleanWs !== 'all') {
        const verifiedCount = data.verified_sentences || 0;
        return {
          total_documents: wsRange.docs,
          total_sentences: wsRange.sentences,
          pending_sentences: Math.max(0, wsRange.sentences - (cleanWs === 'user1' ? verifiedCount : 0)),
          in_progress_sentences: 0,
          verified_sentences: cleanWs === 'user1' ? verifiedCount : 0,
          verified_documents: cleanWs === 'user1' ? Math.min(verifiedCount, wsRange.docs) : 0,
          total_tokens: Math.round(wsRange.sentences * 9.9),
          completion_percentage: wsRange.sentences > 0 ? Number(((cleanWs === 'user1' ? verifiedCount : 0) / wsRange.sentences * 100).toFixed(2)) : 0,
          expert_verified: cleanWs === 'user1' ? verifiedCount : 0,
          workspace_label: wsRange.label,
          assigned_range: `doc_id ${wsRange.start.toLocaleString()}–${wsRange.end.toLocaleString()}`
        };
      }

      return data;
    } catch (err) {
      if (wsRange) {
        return {
          total_documents: wsRange.docs,
          total_sentences: wsRange.sentences,
          pending_sentences: wsRange.sentences,
          in_progress_sentences: 0,
          verified_sentences: 0,
          verified_documents: 0,
          total_tokens: Math.round(wsRange.sentences * 9.9),
          completion_percentage: 0,
          expert_verified: 0,
          workspace_label: wsRange.label,
          assigned_range: `doc_id ${wsRange.start.toLocaleString()}–${wsRange.end.toLocaleString()}`
        };
      }
      throw err;
    }
  },

  getNextSentence: async (workspace) => {
    if (useMock) {
      await new Promise((r) => setTimeout(r, 100));
      const wsNum = workspace ? parseInt(workspace.replace('user', '')) || 1 : 1;
      const basePos = (wsNum - 1) * 1000 + 1;
      return {
        id: basePos,
        doc_id: `${basePos}`,
        sentence_id: 0,
        annotation_id: `${basePos}_0`,
        sentence_position: basePos,
        sentence_text: `संस्कृतवार्तापत्रे अयं वाक्यविशेषः (doc_id ${basePos}) अधुना परीक्षार्थं दर्शितः ।`,
        status: 'pending',
        annotation_note: '',
        tokens: [
          { id: basePos * 10 + 1, token_id: 1, token: 'संस्कृतवार्तापत्रे', lemma: 'संस्कृतवार्तापत्र', upos: 'NOUN', stanza_upos: 'NOUN', xpos: '_', feats: 'Case=Loc|Number=Sing', gold_sanskrit_tag: '' },
          { id: basePos * 10 + 2, token_id: 2, token: 'अयं', lemma: 'इदम्', upos: 'PRON', stanza_upos: 'PRON', xpos: '_', feats: 'Case=Nom|Gender=Masc|Number=Sing', gold_sanskrit_tag: '' },
          { id: basePos * 10 + 3, token_id: 3, token: 'वाक्यविशेषः', lemma: 'वाक्यविशेष', upos: 'NOUN', stanza_upos: 'NOUN', xpos: '_', feats: 'Case=Nom|Gender=Masc|Number=Sing', gold_sanskrit_tag: '' },
          { id: basePos * 10 + 4, token_id: 4, token: 'परीक्षार्थं', lemma: 'परीक्षार्थ', upos: 'ADV', stanza_upos: 'ADV', xpos: '_', feats: '_', gold_sanskrit_tag: '' },
          { id: basePos * 10 + 5, token_id: 5, token: 'दर्शितः', lemma: 'दृश्', upos: 'VERB', stanza_upos: 'VERB', xpos: '_', feats: 'Aspect=Perf|VerbForm=Part', gold_sanskrit_tag: '' },
          { id: basePos * 10 + 6, token_id: 6, token: '।', lemma: '।', upos: 'PUNCT', stanza_upos: 'PUNCT', xpos: '_', feats: '_', gold_sanskrit_tag: 'AVN' }
        ]
      };
    }

    const cleanWs = (workspace || 'user1').toLowerCase().replace(/[\s_]/g, '');
    const wsRange = WORKSPACE_BOUNDS[cleanWs];

    // If workspace has 0 documents (Users 5, 6, 7), immediately throw 404
    if (wsRange && wsRange.docs === 0) {
      const err = new Error(`No sentences exist in ${wsRange.label} range (doc_id ${wsRange.start}–${wsRange.end}).`);
      err.response = {
        status: 404,
        data: {
          detail: `All sentences in the 70% annotation queue end at doc_id 3,597. There are no documents in ${wsRange.label} (doc_id ${wsRange.start.toLocaleString()}–${wsRange.end.toLocaleString()}).`
        }
      };
      throw err;
    }

    // 1. Check user-specific saved draft in localStorage first
    const savedResumeId = localStorage.getItem(`resume_annotation_${cleanWs}`);
    if (savedResumeId) {
      try {
        const savedSentence = await datasetApi.getSentenceByAnnotationId(savedResumeId);
        const docNum = parseInt(savedSentence.doc_id, 10);
        if (wsRange && docNum >= wsRange.start && docNum <= wsRange.end && savedSentence.status !== 'verified') {
          return savedSentence;
        }
      } catch (e) {
        localStorage.removeItem(`resume_annotation_${cleanWs}`);
      }
    }

    // 2. Query backend for next sentence
    try {
      const response = await apiClient.get('/dataset/sentences/next', {
        params: workspace ? { workspace } : {}
      });
      const data = response.data;

      // 3. Strict Range Verification: verify doc_id strictly belongs to this user
      if (wsRange && data && data.doc_id) {
        const docNum = parseInt(data.doc_id, 10);
        if (docNum >= wsRange.start && docNum <= wsRange.end) {
          return data;
        }
        console.warn(`[RANGE SAFETY] Backend returned doc_id ${data.doc_id} outside ${wsRange.label} range (${wsRange.start}-${wsRange.end}). Enforcing range filter.`);
      } else if (!wsRange) {
        return data;
      }
    } catch (err) {
      if (err.response?.status === 404) {
        throw err;
      }
      console.warn('Backend /dataset/sentences/next error:', err.message);
    }

    // 4. Defensive client guard: fetch first eligible annotation for this workspace directly
    if (wsRange && wsRange.firstPendingId) {
      try {
        const directSentence = await datasetApi.getSentenceByAnnotationId(wsRange.firstPendingId);
        const docNum = parseInt(directSentence.doc_id, 10);
        if (docNum >= wsRange.start && docNum <= wsRange.end) {
          return directSentence;
        }
      } catch (e) {
        console.error(`Failed to fetch default first pending sentence for ${cleanWs}:`, e);
      }
    }

    throw new Error(`Unable to fetch an annotation in ${wsRange?.label || cleanWs} range.`);
  },

  getSentenceByAnnotationId: async (annotationId) => {
    if (useMock) {
      await new Promise((r) => setTimeout(r, 100));
      const s = MOCK_DATA.sentences.find(item => item.annotation_id === annotationId);
      if (!s) throw new Error('Sentence not found');
      return JSON.parse(JSON.stringify(s));
    }
    const response = await apiClient.get(`/dataset/sentences/${annotationId}`);
    return response.data;
  }
};

export const annotationApi = {
  saveDraft: async (annotationId, { tokens, note }, workspace) => {
    const cleanWs = (workspace || 'user1').toLowerCase().replace(/[\s_]/g, '');
    localStorage.setItem(`resume_annotation_${cleanWs}`, annotationId);

    if (useMock) {
      await new Promise((r) => setTimeout(r, 300));
      const target = MOCK_DATA.sentences.find(s => s.annotation_id === annotationId);
      if (target) {
        target.tokens = tokens;
        target.annotation_note = note;
        target.status = 'in_progress';
      }
      return { success: true, message: 'Draft saved successfully' };
    }
    const response = await apiClient.put(`/annotations/${annotationId}/draft`, { tokens, note }, {
      params: workspace ? { workspace } : {}
    });
    return response.data;
  },

  verifySentence: async (annotationId, { tokens, note }, workspace) => {
    const cleanWs = (workspace || 'user1').toLowerCase().replace(/[\s_]/g, '');
    localStorage.removeItem(`resume_annotation_${cleanWs}`);

    if (useMock) {
      await new Promise((r) => setTimeout(r, 400));
      const target = MOCK_DATA.sentences.find(s => s.annotation_id === annotationId);
      if (target) {
        target.tokens = tokens;
        target.annotation_note = note;
        target.status = 'verified';
        MOCK_DATA.stats.verified_sentences += 1;
        MOCK_DATA.stats.pending_sentences = Math.max(0, MOCK_DATA.stats.pending_sentences - 1);
        MOCK_DATA.stats.completion_percentage = (
          (MOCK_DATA.stats.verified_sentences / MOCK_DATA.stats.total_sentences) * 100
        ).toFixed(1);
      }
      return { success: true, message: 'Sentence marked as verified and saved' };
    }
    const response = await apiClient.post(`/annotations/${annotationId}/verify`, { tokens, note }, {
      params: workspace ? { workspace } : {}
    });
    return response.data;
  }
};

export const exportApi = {
  downloadVerifiedCsv: async () => {
    if (useMock) {
      const mockCsvContent = "\uFEFFdoc_id,sentence_id,annotation_id,sentence_text,token_id,token,lemma,upos,stanza_upos,xpos,feats,gold_sanskrit_tag,annotation_status,annotation_note,verified_by,verified_at\n" +
        "news_art_001,1,news_art_001_1,प्रधानमन्त्री नरेन्द्रमोदी अद्य नवदेहल्यां नूतनं सङ्ग्रहालयम् उद्घाटितवान् ।,1,प्रधानमन्त्री,प्रधानमन्त्रिन्,NOUN,NOUN,_,Case=Nom|Number=Sing,N,verified,,expert_01,2026-10-11T12:00:00\n";
      return new Blob([mockCsvContent], { type: 'text/csv;charset=utf-8;' });
    }
    const response = await apiClient.get('/export/verified.csv', {
      responseType: 'blob'
    });
    return response.data;
  }
};

export default apiClient;

