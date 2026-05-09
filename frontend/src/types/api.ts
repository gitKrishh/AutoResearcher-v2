export interface APIError {
  code: string;
  message: string;
}

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: APIError;
  meta?: Record<string, any>;
}
