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

export const datasetApi = {
  getWorkspaces: async () => {
    if (useMock) {
      return [
        { id: 1, key: 'user1', label: 'User 1', username: 'user1', range_label: '1–1,000', range_start: 1, range_end: 1000, total_sentences: 1000 },
        { id: 2, key: 'user2', label: 'User 2', username: 'user2', range_label: '1,001–2,000', range_start: 1001, range_end: 2000, total_sentences: 1000 },
        { id: 3, key: 'user3', label: 'User 3', username: 'user3', range_label: '2,001–3,000', range_start: 2001, range_end: 3000, total_sentences: 1000 },
        { id: 4, key: 'user4', label: 'User 4', username: 'user4', range_label: '3,001–4,000', range_start: 3001, range_end: 4000, total_sentences: 1000 },
        { id: 5, key: 'user5', label: 'User 5', username: 'user5', range_label: '4,001–5,000', range_start: 4001, range_end: 5000, total_sentences: 1000 },
        { id: 6, key: 'user6', label: 'User 6', username: 'user6', range_label: '5,001–6,000', range_start: 5001, range_end: 6000, total_sentences: 1000 },
        { id: 7, key: 'user7', label: 'User 7', username: 'user7', range_label: '6,001–7,000', range_start: 6001, range_end: 7000, total_sentences: 1000 }
      ];
    }
    const response = await apiClient.get('/dataset/workspaces');
    return response.data;
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
    const response = await apiClient.get('/dataset/stats', {
      params: workspace ? { workspace } : {}
    });
    return response.data;
  },

  getNextSentence: async (workspace) => {
    if (useMock) {
      await new Promise((r) => setTimeout(r, 100));
      const pending = MOCK_DATA.sentences.find(s => s.status !== 'verified') || MOCK_DATA.sentences[0];
      return JSON.parse(JSON.stringify(pending));
    }
    const response = await apiClient.get('/dataset/sentences/next', {
      params: workspace ? { workspace } : {}
    });
    return response.data;
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
  saveDraft: async (annotationId, { tokens, note }) => {
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
    const response = await apiClient.put(`/annotations/${annotationId}/draft`, { tokens, note });
    return response.data;
  },

  verifySentence: async (annotationId, { tokens, note }) => {
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
    const response = await apiClient.post(`/annotations/${annotationId}/verify`, { tokens, note });
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

