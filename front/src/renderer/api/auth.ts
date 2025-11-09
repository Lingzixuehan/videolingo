import { api } from './http';

export interface TokenResp { access_token: string; token_type: string }
export interface LoginReq { email: string; password: string }
export interface RegisterReq { email: string; password: string }
export interface ResetReq { email: string }

export const login = (data: LoginReq) => api.post<TokenResp>('/api/auth/login', data);
export const register = (data: RegisterReq) => api.post<void>('/api/auth/register', data);
export const resetPassword = (data: ResetReq) => api.post<void>('/api/auth/password-reset', data);