/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../api/axios';

export const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user_type');
    setUser(null);
    window.location.href = '/login';
  }, []);

  // ─── Fetch current user on mount ────────────────────────────
  useEffect(() => {
    const getUser = async () => {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const response = await api.get('/auth/users/me/');
        setUser(response.data);
      } catch (error) {
        console.error('Failed to fetch user:', error);
        logout();
      } finally {
        setLoading(false);
      }
    };
    getUser();
  }, [logout]);

  // ─── Login ──────────────────────────────────────────────────
  const login = async (email, password) => {
    try {
      const { data } = await api.post('/auth/token/', { email, password });
      localStorage.setItem('accessToken', data.access);
      localStorage.setItem('refreshToken', data.refresh);
      if (data.user_type) {
        localStorage.setItem('user_type', data.user_type);
      }
      setUser(data.user);
      return data;
    } catch (error) {
      throw error.response?.data || { message: 'Login failed' };
    }
  };

  // ─── Register ───────────────────────────────────────────────
  const register = async (userData) => {
    try {
      // 🔥 FIX: Remove Content-Type so browser sets it for FormData
      const { data } = await api.post('/auth/register/', userData, {
        headers: {
          'Content-Type': undefined, // let browser set multipart/form-data with boundary
        },
      });
      if (data.access && data.refresh) {
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        if (data.user_type) {
          localStorage.setItem('user_type', data.user_type);
        }
        setUser(data.user || data);
      }
      return data;
    } catch (error) {
      throw error.response?.data || { message: 'Registration failed' };
    }
  };

  // ─── Update Profile ──────────────────────────────────────────
  const updateProfile = async (profileData) => {
    try {
      // If it's FormData, don't set Content-Type – let browser handle it
      const headers = profileData instanceof FormData
        ? { 'Content-Type': undefined } // browser sets it
        : { 'Content-Type': 'application/json' };

      const response = await api.patch('/auth/users/me/', profileData, { headers });
      setUser(response.data);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Profile update failed' };
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
};