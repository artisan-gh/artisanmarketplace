
import axios from 'axios';

const BASE = import.meta?.env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';
const authClient = axios.create({ baseURL: BASE });

export const sendOtp = (phone) => authClient.post('/auth/otp/send/', { phone }).then(r => r.data);
export const resendOtp = (phone) => authClient.post('/auth/otp/resend/', { phone }).then(r => r.data);
export const verifyOtp = (phone, code) => authClient.post('/auth/otp/verify/', { phone, code }).then(r => r.data);
export default authClient;
