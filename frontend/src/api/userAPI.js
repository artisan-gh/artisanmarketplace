// src/api/userAPI.js
import api from './api';

export const updateUser = (data) => api.patch('/auth/users/me/', data).then(res => res.data);
export const changePassword = (data) => api.post('/auth/users/change-password/', data).then(res => res.data);