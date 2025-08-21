"""
Security and authentication endpoints.
"""
from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token, verify_password, get_password_hash,
    verify_token, SecurityAudit, rate_limiter, check_password_strength,
    mask_sensitive_info
)
from app.core.config import settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/security/token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

class UserInDB(BaseModel):
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class PasswordStrengthCheck(BaseModel):
    password: str

# Mock user database (in production, use real database)
fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@scrum-master.ai",
        "hashed_password": get_password_hash("admin123"),
        "is_active": True,
        "is_superuser": True,
    },
    "scrum_master": {
        "username": "scrum_master",
        "email": "scrum@scrum-master.ai", 
        "hashed_password": get_password_hash("scrum123"),
        "is_active": True,
        "is_superuser": False,
    }
}

def get_user(username: str) -> UserInDB:
    """Get user from database."""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(username: str, password: str) -> UserInDB:
    """Authenticate user credentials."""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = verify_token(token)
    if username is None:
        raise credentials_exception
    
    user = get_user(username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login endpoint to get access token.
    """
    client_ip = request.client.host
    
    # Rate limiting
    if not rate_limiter.is_allowed(f"login_{client_ip}", max_requests=5, window_minutes=15):
        SecurityAudit.log_security_event(
            "RATE_LIMIT_EXCEEDED", 
            f"Too many login attempts from {client_ip}",
            form_data.username
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Authenticate user
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        SecurityAudit.log_authentication_attempt(form_data.username, False, client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    
    SecurityAudit.log_authentication_attempt(form_data.username, True, client_ip)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    """
    Get current user information.
    """
    return {
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser
    }

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: UserInDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Check new password strength
    strength_check = check_password_strength(password_data.new_password)
    if not strength_check["is_strong"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password not strong enough. Suggestions: {', '.join(strength_check['suggestions'])}"
        )
    
    # Update password (in production, update in database)
    new_hashed_password = get_password_hash(password_data.new_password)
    fake_users_db[current_user.username]["hashed_password"] = new_hashed_password
    
    SecurityAudit.log_security_event(
        "PASSWORD_CHANGED",
        f"Password changed for user {current_user.username}",
        current_user.username
    )
    
    return {"message": "Password changed successfully"}

@router.post("/check-password-strength")
async def check_password_strength_endpoint(
    password_data: PasswordStrengthCheck,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Check password strength without changing it.
    """
    strength_check = check_password_strength(password_data.password)
    
    return {
        "is_strong": strength_check["is_strong"],
        "score": strength_check["score"],
        "max_score": 5,
        "suggestions": strength_check["suggestions"]
    }

@router.get("/audit-logs")
async def get_audit_logs(
    current_user: UserInDB = Depends(get_current_active_user),
    limit: int = 50
):
    """
    Get security audit logs (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # In production, fetch from actual logs/database
    # This is a mock response
    mock_logs = [
        {
            "timestamp": "2025-01-02T01:45:00Z",
            "event_type": "AUTH_ATTEMPT",
            "user": "admin",
            "status": "SUCCESS",
            "ip_address": "127.0.0.1"
        },
        {
            "timestamp": "2025-01-02T01:40:00Z", 
            "event_type": "API_ACCESS",
            "user": "scrum_master",
            "endpoint": "/api/v1/sprints",
            "method": "GET"
        }
    ]
    
    SecurityAudit.log_data_access(
        "audit_logs", 
        current_user.username, 
        "READ",
        f"limit={limit}"
    )
    
    return {
        "logs": mock_logs[:limit],
        "total": len(mock_logs),
        "note": "This is mock data. In production, implement real audit log storage."
    }

@router.get("/security-status")
async def get_security_status(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get security status and recommendations.
    """
    # Check various security aspects
    security_status = {
        "authentication": {
            "status": "enabled",
            "method": "JWT Bearer Token",
            "token_expiry": f"{settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes"
        },
        "encryption": {
            "status": "enabled",
            "method": "Fernet (AES 128)",
            "note": "Sensitive data encrypted at rest"
        },
        "rate_limiting": {
            "status": "enabled",
            "login_limit": "5 attempts per 15 minutes",
            "api_limit": "100 requests per hour"
        },
        "audit_logging": {
            "status": "enabled",
            "events": ["authentication", "api_access", "data_changes", "security_events"]
        },
        "recommendations": []
    }
    
    # Add recommendations based on current state
    if settings.SECRET_KEY == "your-secret-key-change-in-production":
        security_status["recommendations"].append(
            "⚠️ Change the SECRET_KEY in production environment"
        )
    
    if not settings.OPENAI_API_KEY.startswith("sk-"):
        security_status["recommendations"].append(
            "⚠️ Configure proper OpenAI API key"
        )
    
    if len(security_status["recommendations"]) == 0:
        security_status["recommendations"].append("✅ Security configuration looks good")
    
    return security_status

@router.post("/validate-api-integration")
async def validate_api_integrations(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Validate and test API integrations security.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Test integrations (mock implementation)
    integration_status = {
        "slack": {
            "configured": bool(settings.SLACK_BOT_TOKEN),
            "token_masked": mask_sensitive_info(settings.SLACK_BOT_TOKEN or ""),
            "status": "connected" if settings.SLACK_BOT_TOKEN else "not_configured"
        },
        "jira": {
            "configured": bool(settings.JIRA_API_TOKEN),
            "token_masked": mask_sensitive_info(settings.JIRA_API_TOKEN or ""),
            "status": "connected" if settings.JIRA_API_TOKEN else "not_configured"
        },
        "openai": {
            "configured": bool(settings.OPENAI_API_KEY),
            "token_masked": mask_sensitive_info(settings.OPENAI_API_KEY or ""),
            "status": "connected" if settings.OPENAI_API_KEY else "not_configured"
        }
    }
    
    SecurityAudit.log_security_event(
        "INTEGRATION_VALIDATION",
        "API integrations validated",
        current_user.username
    )
    
    return {
        "integrations": integration_status,
        "security_note": "API tokens are encrypted in storage and masked in responses"
    }