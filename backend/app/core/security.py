"""
Security utilities for authentication, authorization, and data protection.
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from cryptography.fernet import Fernet
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption for sensitive data (API tokens, etc.)
def get_encryption_key() -> bytes:
    """Get or generate encryption key for sensitive data."""
    key_file = "encryption.key"
    
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        return key

encryption_key = get_encryption_key()
cipher_suite = Fernet(encryption_key)

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return subject."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data like API tokens."""
    try:
        encrypted_data = cipher_suite.encrypt(data.encode())
        return encrypted_data.decode()
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encrypt sensitive data"
        )

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data."""
    try:
        decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decrypt sensitive data"
        )

def generate_secure_token() -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)

def validate_api_key(api_key: str) -> bool:
    """Validate API key format and strength."""
    if not api_key or len(api_key) < 32:
        return False
    
    # Additional validation logic can be added here
    return True

def sanitize_input(data: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not data:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", "'", '"', "&", ";", "(", ")", "script"]
    sanitized = data
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")
    
    return sanitized.strip()

def mask_sensitive_info(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive information for logging."""
    if not data or len(data) <= visible_chars:
        return mask_char * 8
    
    return data[:visible_chars] + mask_char * (len(data) - visible_chars)

class SecurityAudit:
    """Security audit logging utilities."""
    
    @staticmethod
    def log_authentication_attempt(username: str, success: bool, ip_address: str = None):
        """Log authentication attempts."""
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"AUTH_ATTEMPT: User={username}, Status={status}, IP={ip_address}")
    
    @staticmethod
    def log_api_access(endpoint: str, user: str, method: str, ip_address: str = None):
        """Log API access for sensitive endpoints."""
        logger.info(f"API_ACCESS: Endpoint={endpoint}, User={user}, Method={method}, IP={ip_address}")
    
    @staticmethod
    def log_data_access(resource: str, user: str, action: str, resource_id: str = None):
        """Log data access for audit trails."""
        logger.info(f"DATA_ACCESS: Resource={resource}, User={user}, Action={action}, ID={resource_id}")
    
    @staticmethod
    def log_security_event(event_type: str, details: str, user: str = None):
        """Log security-related events."""
        logger.warning(f"SECURITY_EVENT: Type={event_type}, Details={details}, User={user}")

# Rate limiting utilities
class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, identifier: str, max_requests: int = 100, window_minutes: int = 60) -> bool:
        """Check if request is allowed based on rate limits."""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Clean old entries
        self.requests = {
            key: value for key, value in self.requests.items() 
            if value['timestamp'] > window_start
        }
        
        # Check current requests
        if identifier not in self.requests:
            self.requests[identifier] = {'count': 0, 'timestamp': now}
        
        if self.requests[identifier]['count'] >= max_requests:
            return False
        
        self.requests[identifier]['count'] += 1
        self.requests[identifier]['timestamp'] = now
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()

# Security headers middleware data
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

def validate_file_upload(filename: str, content_type: str, max_size_mb: int = 10) -> bool:
    """Validate file uploads for security."""
    # Check file extension
    allowed_extensions = {'.txt', '.csv', '.json', '.md', '.pdf', '.png', '.jpg', '.jpeg'}
    file_ext = os.path.splitext(filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return False
    
    # Check content type
    allowed_content_types = {
        'text/plain', 'text/csv', 'application/json', 
        'text/markdown', 'application/pdf',
        'image/png', 'image/jpeg'
    }
    
    if content_type not in allowed_content_types:
        return False
    
    return True

def check_password_strength(password: str) -> dict:
    """Check password strength and return feedback."""
    feedback = {
        "is_strong": False,
        "score": 0,
        "suggestions": []
    }
    
    if len(password) < 8:
        feedback["suggestions"].append("Use at least 8 characters")
    else:
        feedback["score"] += 1
    
    if not any(c.isupper() for c in password):
        feedback["suggestions"].append("Include uppercase letters")
    else:
        feedback["score"] += 1
    
    if not any(c.islower() for c in password):
        feedback["suggestions"].append("Include lowercase letters")
    else:
        feedback["score"] += 1
    
    if not any(c.isdigit() for c in password):
        feedback["suggestions"].append("Include numbers")
    else:
        feedback["score"] += 1
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        feedback["suggestions"].append("Include special characters")
    else:
        feedback["score"] += 1
    
    feedback["is_strong"] = feedback["score"] >= 4
    return feedback