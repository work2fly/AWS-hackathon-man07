// AWS Configuration for AI Therapy Platform
// 🏆 Breaking Barriers UK 2026 compliant - us-west-2 region only

export const awsConfig = {
  // AWS Region - Breaking Barriers constraint: us-west-2 only
  region: 'us-west-2',
  
  // API Gateway endpoints from terraform state
  apiGateway: {
    restApi: 'https://xi8ekw0fj6.execute-api.us-west-2.amazonaws.com/dev',
    websocketApi: 'wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com'
  },
  
  // Cognito configuration from terraform state
  cognito: {
    userPoolId: 'us-west-2_ASOPUuOOV',
    userPoolWebClientId: 'krm7gidi0n5ikqvemtd79oql1',
    region: 'us-west-2',
    // Note: Client secret not available in frontend for security
    // Backend integration will handle secret hash generation
  },
  
  // Bedrock model configuration
  bedrock: {
    model: 'anthropic.claude-3-5-sonnet-20241022-v2:0', // From terraform state
    region: 'us-west-2'
  },
  
  // Demo mode configuration
  demo: {
    enabled: true, // Enable demo mode for testing without backend
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