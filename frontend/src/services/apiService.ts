import axios from 'axios';
import type { APIResponse } from '@/types/api';
import type { FinalReport, ResearchRequest } from '@/types/research';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  conductResearch: async (request: ResearchRequest): Promise<APIResponse<FinalReport>> => {
    const response = await api.post<APIResponse<FinalReport>>('/research', request);
    return response.data;
  },
  
  getHealth: async (): Promise<APIResponse<{status: string}>> => {
    const response = await api.get<APIResponse<{status: string}>>('/health');
    return response.data;
  },

  chat: async (query: string, top_k: number = 5): Promise<APIResponse<{answer: string}>> => {
    const response = await api.post<APIResponse<{answer: string}>>('/chat', { query, top_k });
    return response.data;
  }
};
