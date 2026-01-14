"""
Local Development Server for AI Therapy Platform
Wraps Lambda handlers in FastAPI for local testing
🏆 Breaking Barriers UK 2026 compliant
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from fastapi import FastAPI, Request, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import uvicorn

# Import Lambda handlers
from src.lambda_functions.auth_handlers import lambda_handler as auth_lambda_handler
from src.lambda_functions.session_handlers import lambda_handler as session_lambda_handler

# Set environment variables for local development
os.environ.setdefault('AWS_DEFAULT_REGION', 'us-west-2')
os.environ.setdefault('ENVIRONMENT', 'local')
os.environ.setdefault('USER_POOL_ID', 'local-user-pool')
os.environ.setdefault('CLIENT_ID', 'local-client-id')
os.environ.setdefault('USERS_TABLE_NAME', 'ai-therapy-platform-local-users')
os.environ.setdefault('SESSIONS_TABLE_NAME', 'ai-therapy-platform-local-sessions')
os.environ.setdefault('RED_FLAGS_TABLE_NAME', 'ai-therapy-platform-local-red-flags')
os.environ.setdefault('NOTIFICATIONS_TABLE_NAME', 'ai-therapy-platform-local-notifications')
os.environ.setdefault('CONNECTIONS_TABLE_NAME', 'ai-therapy-platform-local-connections')

app = FastAPI(
    title="AI Therapy Platform - Local Dev Server",
    description="Local development server for testing Lambda handlers",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_lambda_event(request: Request, path: str, method: str, 
                       path_params: dict = None, query_params: dict = None,
                       body: dict = None) -> dict:
    """Create Lambda event structure from FastAPI request"""
    headers = dict(request.headers)
    
    event = {
        'httpMethod': method,
        'path': path,
        'headers': headers,
        'pathParameters': path_params or {},
        'queryStringParameters': query_params,
        'body': body,
        'requestContext': {
            'requestId': 'local-request-id',
            'identity': {
                'sourceIp': request.client.host if request.client else '127.0.0.1'
            }
        }
    }
    
    return event

def handle_lambda_response(lambda_response: dict) -> JSONResponse:
    """Convert Lambda response to FastAPI response"""
    status_code = lambda_response.get('statusCode', 200)
    body = lambda_response.get('body', '{}')
    headers = lambda_response.get('headers', {})
    
    # Parse body if it's a string
    import json
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except:
            pass
    
    return JSONResponse(
        status_code=status_code,
        content=body,
        headers=headers
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Therapy Platform Local Dev Server",
        "environment": "local"
    }

# Authentication endpoints
@app.post("/auth/register")
async def register(request: Request):
    """Register a new user"""
    body = await request.json()
    event = create_lambda_event(request, '/auth/register', 'POST', body=body)
    response = auth_lambda_handler(event, None)
    return handle_lambda_response(response)

@app.post("/auth/login")
async def login(request: Request):
    """User login"""
    body = await request.json()
    event = create_lambda_event(request, '/auth/login', 'POST', body=body)
    response = auth_lambda_handler(event, None)
    return handle_lambda_response(response)

@app.post("/auth/logout")
async def logout(request: Request, authorization: Optional[str] = Header(None)):
    """User logout"""
    event = create_lambda_event(request, '/auth/logout', 'POST')
    response = auth_lambda_handler(event, None)
    return handle_lambda_response(response)

@app.post("/auth/refresh")
async def refresh_token(request: Request):
    """Refresh authentication token"""
    body = await request.json()
    event = create_lambda_event(request, '/auth/refresh', 'POST', body=body)
    response = auth_lambda_handler(event, None)
    return handle_lambda_response(response)

@app.post("/auth/reset-password")
async def reset_password(request: Request):
    """Request password reset"""
    body = await request.json()
    event = create_lambda_event(request, '/auth/reset-password', 'POST', body=body)
    response = auth_lambda_handler(event, None)
    return handle_lambda_response(response)

@app.get("/auth/profile")
async def get_profile(request: Request, authorization: Optional[str] = Header(None)):
    """Get user profile"""
    event = create_lambda_event(request, '/auth/profile', 'GET')
    response = auth_lambda_handler(event, None)
    return handle_lambda_response(response)

@app.put("/auth/profile")
async def update_profile(request: Request, authorization: Optional[str] = Header(None)):
    """Update user profile"""
    body = await request.json()
    event = create_lambda_event(request, '/auth/profile', 'PUT', body=body)
    response = auth_lambda_handler(event, None)
    return handle_lambda_response(response)

@app.post("/auth/enable-mfa")
async def enable_mfa(request: Request, authorization: Optional[str] = Header(None)):
    """Enable MFA for user"""
    event = create_lambda_event(request, '/auth/enable-mfa', 'POST')
    response = auth_lambda_handler(event, None)
    return handle_lambda_response(response)

# Session endpoints
@app.post("/sessions")
async def create_session(request: Request, authorization: Optional[str] = Header(None)):
    """Create a new therapy session"""
    body = await request.json()
    event = create_lambda_event(request, '/sessions', 'POST', body=body)
    response = session_lambda_handler(event, None)
    return handle_lambda_response(response)

@app.put("/sessions/{session_id}/state")
async def update_session_state(
    request: Request,
    session_id: str,
    timestamp: str = Query(...),
    authorization: Optional[str] = Header(None)
):
    """Update session state and metadata"""
    body = await request.json()
    event = create_lambda_event(
        request,
        f'/sessions/{session_id}/state',
        'PUT',
        path_params={'session_id': session_id},
        query_params={'timestamp': timestamp},
        body=body
    )
    response = session_lambda_handler(event, None)
    return handle_lambda_response(response)

@app.post("/sessions/{session_id}/complete")
async def complete_session(
    request: Request,
    session_id: str,
    timestamp: str = Query(...),
    authorization: Optional[str] = Header(None)
):
    """Complete a therapy session"""
    event = create_lambda_event(
        request,
        f'/sessions/{session_id}/complete',
        'POST',
        path_params={'session_id': session_id},
        query_params={'timestamp': timestamp}
    )
    response = session_lambda_handler(event, None)
    return handle_lambda_response(response)

@app.post("/sessions/{session_id}/terminate")
async def terminate_session(
    request: Request,
    session_id: str,
    timestamp: str = Query(...),
    authorization: Optional[str] = Header(None)
):
    """Terminate a therapy session"""
    body = await request.json() if await request.body() else {}
    event = create_lambda_event(
        request,
        f'/sessions/{session_id}/terminate',
        'POST',
        path_params={'session_id': session_id},
        query_params={'timestamp': timestamp},
        body=body
    )
    response = session_lambda_handler(event, None)
    return handle_lambda_response(response)

@app.get("/clients/{client_id}/sessions")
async def get_client_sessions(
    request: Request,
    client_id: str,
    limit: Optional[int] = Query(50),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    exclusive_start_key: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
):
    """Get sessions for a client"""
    query_params = {
        'limit': str(limit),
        'start_date': start_date,
        'end_date': end_date,
        'exclusive_start_key': exclusive_start_key
    }
    query_params = {k: v for k, v in query_params.items() if v is not None}
    
    event = create_lambda_event(
        request,
        f'/clients/{client_id}/sessions',
        'GET',
        path_params={'client_id': client_id},
        query_params=query_params
    )
    response = session_lambda_handler(event, None)
    return handle_lambda_response(response)

@app.get("/sessions/active")
async def get_active_sessions(
    request: Request,
    limit: Optional[int] = Query(100),
    authorization: Optional[str] = Header(None)
):
    """Get all active sessions (therapists and admins only)"""
    query_params = {'limit': str(limit)} if limit else {}
    event = create_lambda_event(
        request,
        '/sessions/active',
        'GET',
        query_params=query_params
    )
    response = session_lambda_handler(event, None)
    return handle_lambda_response(response)

@app.get("/sessions/{session_id}")
async def get_session(
    request: Request,
    session_id: str,
    timestamp: str = Query(...),
    authorization: Optional[str] = Header(None)
):
    """Get session details"""
    event = create_lambda_event(
        request,
        f'/sessions/{session_id}',
        'GET',
        path_params={'session_id': session_id},
        query_params={'timestamp': timestamp}
    )
    response = session_lambda_handler(event, None)
    return handle_lambda_response(response)

if __name__ == "__main__":
    print("🚀 Starting AI Therapy Platform Local Development Server")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("\n⚠️  Note: This is a local development server using mock AWS services")
    print("   For production deployment, use Terraform to deploy to AWS\n")
    
    uvicorn.run(
        "local_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
