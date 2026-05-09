import axios from 'axios';
import { APIResponse } from '@/types/api';
import { FinalReport, ResearchRequest } from '@/types/research';

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
  }
};
