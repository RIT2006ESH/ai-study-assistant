// src/services/authService.js
import { authAPI } from './api';

const authService = {
  /**
   * Login user
   */
  async login(email, password) {
    try {
      const result = await authAPI.login(email, password);
      
      if (result.access_token || result.token) {
        // Store token in localStorage
        const token = result.access_token || result.token;
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(result.user || result));
        
        return {
          success: true,
          user: result.user || result,
          token: token
        };
      }
      
      return {
        success: false,
        error: 'Invalid credentials'
      };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: error.message || 'Login failed'
      };
    }
  },

  /**
   * Register new user
   */
  async register(email, password, name) {
    try {
      const result = await authAPI.register(email, password, name);
      
      if (result.access_token || result.token) {
        // Store token in localStorage
        const token = result.access_token || result.token;
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(result.user || result));
        
        return {
          success: true,
          user: result.user || result,
          token: token
        };
      }
      
      return {
        success: false,
        error: 'Registration failed'
      };
    } catch (error) {
      console.error('Registration error:', error);
      return {
        success: false,
        error: error.message || 'Registration failed'
      };
    }
  },

  /**
   * Logout user
   */
  logout() {
    try {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      return {
        success: true
      };
    } catch (error) {
      console.error('Logout error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Get current user from localStorage
   */
  getCurrentUser() {
    try {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        return JSON.parse(userStr);
      }
      return null;
    } catch (error) {
      console.error('Get current user error:', error);
      return null;
    }
  },

  /**
   * Get current token
   */
  getToken() {
    return localStorage.getItem('token');
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    const token = this.getToken();
    return !!token;
  },

  /**
   * Get user ID
   */
  getUserId() {
    const user = this.getCurrentUser();
    return user?.id || user?.user_id || null;
  },

  /**
   * Update user profile in localStorage
   */
  updateUserProfile(userData) {
    try {
      const currentUser = this.getCurrentUser();
      const updatedUser = { ...currentUser, ...userData };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      
      return {
        success: true,
        user: updatedUser
      };
    } catch (error) {
      console.error('Update profile error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
};

export default authService;