import { chatAPI } from './api';

const chatService = {
  /**
   * Send a chat message with query validation
   */
  async sendMessage(query, context = null) {
    try {
      const result = await chatAPI.sendMessage(query, context);
      
      // DON'T wrap the result - return it as-is
      // chatAPI.sendMessage already returns proper format with validation
      return result;
      
    } catch (error) {
      console.error('Chat service error:', error);
      
      // Only return generic error for actual network/system failures
      return {
        success: false,
        error: true,
        message: 'Network error. Please check your connection and try again.',
        details: error.message,
        isRejected: false
      };
    }
  },

  /**
   * Validate a query before sending
   */
  async validateQuery(query) {
    try {
      return await chatAPI.validateQuery(query);
    } catch (error) {
      console.error('Query validation error:', error);
      return {
        valid: false,
        reason: 'Validation service unavailable',
        error: error.message
      };
    }
  },

  /**
   * Check chat service health
   */
  async checkHealth() {
    try {
      return await chatAPI.checkHealth();
    } catch (error) {
      console.error('Health check error:', error);
      return {
        status: 'unhealthy',
        error: error.message
      };
    }
  }
};

export default chatService;
