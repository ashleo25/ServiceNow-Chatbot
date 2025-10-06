import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const chatAPI = {
  // Send a chat message
  sendMessage: async (message, agentType, context = {}) => {
    try {
      const response = await api.post('/chat', {
        message,
        agent_type: agentType,
        context
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to send message');
    }
  },

  // Search knowledge base or ServiceNow
  search: async (query, searchType = 'knowledge') => {
    try {
      const response = await api.post('/search', {
        query,
        search_type: searchType
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Search failed');
    }
  },

  // Get article content
  getArticle: async (articleId) => {
    try {
      const response = await api.get(`/article/${articleId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get article');
    }
  },

  // Create a ticket
  createTicket: async (ticketData) => {
    try {
      const response = await api.post('/ticket/create', ticketData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create ticket');
    }
  },

  // Check ticket status
  getTicketStatus: async (ticketNumber) => {
    try {
      const response = await api.get(`/ticket/status/${ticketNumber}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get ticket status');
    }
  },

  // Update ticket
  updateTicket: async (ticketNumber, workNotes) => {
    try {
      const response = await api.post('/ticket/update', {
        ticket_number: ticketNumber,
        work_notes: workNotes
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update ticket');
    }
  },

  // Test ticket agent
  testTicketAgent: async () => {
    try {
      const response = await api.get('/test/ticket-agent');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to test ticket agent');
    }
  },

  // Enhanced chat with intent detection and structured data collection
  sendEnhancedMessage: async (message, sessionData = null) => {
    try {
      const response = await api.post('/chat/enhanced', {
        message,
        session_data: sessionData
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to send enhanced message');
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      throw new Error('Backend connection failed');
    }
  },

  // Handle duplicate ticket decision
  handleDuplicateDecision: async (decision, sessionData) => {
    try {
      const response = await api.post('/ticket/duplicate-decision', {
        decision,
        session_data: sessionData
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to handle duplicate decision');
    }
  },

  // Get ticket creation agent status
  getTicketCreationStatus: async () => {
    try {
      const response = await api.get('/ticket/creation/status');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get ticket creation status');
    }
  },

  // Analytics API methods
  processAnalyticsQuery: async (query, userContext = {}) => {
    try {
      const response = await api.post('/analytics/query', {
        query,
        user_context: userContext
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to process analytics query');
    }
  },

  getAvailableAnalyticsQueries: async () => {
    try {
      const response = await api.get('/analytics/queries');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get available queries');
    }
  },

  getAnalyticsData: async (area, kpi) => {
    try {
      const response = await api.get(`/analytics/data/${area}/${kpi}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get analytics data');
    }
  }
};

export default api;
