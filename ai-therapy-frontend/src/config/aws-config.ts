// AWS Configuration for AI Therapy Platform
// 🏆 Breaking Barriers UK 2026 compliant - us-west-2 region only

export const awsConfig = {
  // AWS Region - Breaking Barriers constraint: us-west-2 only
  region: 'us-west-2',
  
  // API Gateway endpoints from terraform state
  apiGateway: {
    restApi: 'https://xi8ekw0fj6.execute-api.us-west-2.amazonaws.com/dev',
    websocketApi: 'wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev'
  },
  
  // Cognito configuration - Frontend Public Client (no secret)
  // Created by: backend/scripts/create_public_cognito_client.py
  cognito: {
    userPoolId: 'us-west-2_ASOPUuOOV',
    userPoolWebClientId: '50bh1stem2eqiatfi4cg382rj8', // ✅ Frontend public client (no secret)
    region: 'us-west-2',
    // Note: This is a public client without secret - safe for frontend use
    // Uses SRP authentication for secure password exchange
  },
  
  // Bedrock model configuration
  bedrock: {
    model: 'anthropic.claude-3-5-sonnet-20241022-v2:0', // From terraform state
    region: 'us-west-2'
  },
  
  // Demo mode configuration
  demo: {
    enabled: false, // ✅ Disabled - using real backend
    mockDelay: 1000, // Simulate network delay
  }
};

// Environment-specific configuration
export const getApiUrl = (endpoint: string) => {
  return `${awsConfig.apiGateway.restApi}${endpoint}`;
};

export const getWebSocketUrl = () => {
  return awsConfig.apiGateway.websocketApi;
};

// Check if we're in demo mode (no backend available)
export const isDemoMode = () => {
  return awsConfig.demo.enabled || process.env.NODE_ENV === 'development';
};