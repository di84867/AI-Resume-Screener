"""
auth.py
-------
Simple local authentication system for AI Resume Intelligence.
Stores user credentials in data/users.json with hashed passwords.
"""

import json
import os
import hashlib
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
import requests

USERS_FILE = "data/users.json"
ADMIN_PASSWORD = "admin123" # Default admin password

# OIDC Configuration (Dynamic)
def get_oidc_config(provider: str = "google"):
    redirect_uri = os.environ.get("OAUTH_REDIRECT_URI", "http://localhost:8501")
    if provider == "google":
        return {
            "discovery_url": "https://accounts.google.com/.well-known/openid-configuration",
            "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
            "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
            "redirect_uri": redirect_uri
        }
    elif provider == "github":
        return {
            "auth_endpoint": "https://github.com/login/oauth/authorize",
            "token_endpoint": "https://github.com/login/oauth/access_token",
            "userinfo_endpoint": "https://api.github.com/user",
            "client_id": os.environ.get("GITHUB_CLIENT_ID", ""),
            "client_secret": os.environ.get("GITHUB_CLIENT_SECRET", ""),
            "redirect_uri": redirect_uri
        }
    return None

def _hash_password(password: str) -> str:
    """SHA-256 hash a password with a static salt."""
    salt = "resume_iq_2026"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def _load_users() -> Dict[str, Any]:
    """Load all users from JSON file."""
    if not os.path.exists(USERS_FILE):
        # Create default admin if file doesn't exist
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        admin_user = {
            "name": "Main Admin",
            "email": "admin",
            "phone": "0000000000",
            "password_hash": _hash_password("admin123"),
            "role": "admin",
            "is_main_admin": True,
            "created_at": datetime.now().isoformat(),
        }
        _save_users({"admin": admin_user})
        return {"admin": admin_user}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_users(users: Dict[str, Any]):
    """Save users dict to JSON file."""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def validate_email(email: str) -> bool:
    """Basic email validation."""
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email))


def validate_phone(phone: str) -> bool:
    """Basic phone validation (at least 10 digits)."""
    digits = re.sub(r"\D", "", phone)
    return len(digits) >= 10


def sign_up(name: str, email: str, phone: str, password: str, role: str = "user") -> Dict[str, Any]:
    """
    Register a new user.
    Returns: {"success": bool, "message": str, "user": dict|None}
    """
    email = email.strip().lower()
    name = name.strip()
    phone = phone.strip()

    if not name:
        return {"success": False, "message": "Name is required.", "user": None}
    if not validate_email(email):
        return {"success": False, "message": "Invalid email address.", "user": None}
    if not validate_phone(phone):
        return {"success": False, "message": "Phone must have at least 10 digits.", "user": None}
    if len(password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters.", "user": None}

    users = _load_users()

    if email in users:
        return {"success": False, "message": "An account with this email already exists.", "user": None}

    user_profile = {
        "name": name,
        "email": email,
        "phone": phone,
        "password_hash": _hash_password(password),
        "role": role,
        "created_at": datetime.now().isoformat(),
    }
    users[email] = user_profile
    _save_users(users)

    # Return profile without password hash
    safe_profile = {k: v for k, v in user_profile.items() if k != "password_hash"}
    return {"success": True, "message": "Account created successfully!", "user": safe_profile}


def sign_in(email: str, password: str) -> Dict[str, Any]:
    """
    Authenticate a user.
    Returns: {"success": bool, "message": str, "user": dict|None}
    """
    email = email.strip().lower()
    users = _load_users()

    if email not in users:
        return {"success": False, "message": "No account found with this email.", "user": None}

    stored = users[email]
    if stored["password_hash"] != _hash_password(password):
        return {"success": False, "message": "Incorrect password.", "user": None}

    safe_profile = {k: v for k, v in stored.items() if k != "password_hash"}
    return {"success": True, "message": "Welcome back!", "user": safe_profile}


def get_user_display(profile: Optional[Dict[str, Any]]) -> str:
    """Get a display string for the signed-in user."""
    if not profile:
        return "Guest"
    name = profile.get("name", "")
    email = profile.get("email", "")
    role_suffix = " (Admin)" if profile.get("role") == "admin" else ""
    return f"{name or email}{role_suffix}"


def reset_password(email: str, new_password: str) -> bool:
    """Reset a user's password (Admin only action recommended to prefix this)."""
    users = _load_users()
    if email in users:
        users[email]["password_hash"] = _hash_password(new_password)
        _save_users(users)
        return True
    return False


def delete_user(email: str) -> bool:
    """Delete a user account."""
    users = _load_users()
    if email in users and not users[email].get("is_main_admin"):
        del users[email]
        _save_users(users)
        return True
    return False

def update_user_role(email: str, new_role: str) -> bool:
    """Update a user's role."""
    users = _load_users()
    if email in users and not users[email].get("is_main_admin"):
        users[email]["role"] = new_role
        _save_users(users)
        return True
    return False

def get_all_users() -> List[Dict[str, Any]]:
    """Return list of all users (safe profiles)."""
    users = _load_users()
    return [{k: v for k, v in u_p.items() if k != "password_hash"} for u_p in users.values()]


# --- OIDC HELPERS ---

def get_oidc_auth_url(provider: str = "google", state: str = "secure_state") -> str:
    """Generate the authorization URL for the OIDC provider."""
    config = get_oidc_config(provider)
    if not config or not config["client_id"]: return ""
    
    try:
        if provider == "github":
            auth_endpoint = config["auth_endpoint"]
            params = {
                "client_id": config["client_id"],
                "redirect_uri": config["redirect_uri"],
                "scope": "read:user user:email",
                "state": state,
            }
        else:
            discovery = requests.get(config["discovery_url"]).json()
            auth_endpoint = discovery["authorization_endpoint"]
            params = {
                "client_id": config["client_id"],
                "response_type": "code",
                "scope": "openid email profile",
                "redirect_uri": config["redirect_uri"],
                "state": state,
                "access_type": "offline",
                "prompt": "select_account"
            }
        query = "&".join([f"{k}={requests.utils.quote(v)}" for k, v in params.items()])
        return f"{auth_endpoint}?{query}"
    except Exception as e:
        print(f"OIDC Discovery Error: {e}")
        return ""

def process_oidc_callback(code: str, provider: str = "google") -> Dict[str, Any]:
    """Exchange OIDC code for user info."""
    config = get_oidc_config(provider)
    if not config or not config["client_id"]: return {"success": False, "message": "Invalid provider or missing client credentials."}
    
    try:
        if provider == "github":
            token_endpoint = config["token_endpoint"]
            userinfo_endpoint = config["userinfo_endpoint"]
            
            data = {
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "code": code,
                "redirect_uri": config["redirect_uri"]
            }
            # Exchange for token
            headers = {"Accept": "application/json"}
            token_res = requests.post(token_endpoint, data=data, headers=headers).json()
            access_token = token_res.get("access_token")
            if not access_token:
                return {"success": False, "message": "Failed to retrieve access token from GitHub."}
            
            # Fetch user info
            user_res = requests.get(userinfo_endpoint, headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"}).json()
            email = user_res.get("email")
            
            # GitHub sometimes keeps email private, fetch from /emails endpoint
            if not email:
                emails_res = requests.get(f"{userinfo_endpoint}/emails", headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"}).json()
                for em in emails_res:
                    if em.get("primary") and em.get("verified"):
                        email = em.get("email")
                        break
                        
            name = user_res.get("name") or user_res.get("login") or email
            
        else:
            # Standard OIDC (Google)
            discovery = requests.get(config["discovery_url"]).json()
            token_endpoint = discovery["token_endpoint"]
            userinfo_endpoint = discovery["userinfo_endpoint"]
            
            data = {
                "code": code,
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "redirect_uri": config["redirect_uri"],
                "grant_type": "authorization_code"
            }
            token_res = requests.post(token_endpoint, data=data).json()
            access_token = token_res.get("access_token")
            if not access_token:
                return {"success": False, "message": "Failed to retrieve access token."}
                
            user_res = requests.get(userinfo_endpoint, headers={"Authorization": f"Bearer {access_token}"}).json()
            email = user_res.get("email")
            name = user_res.get("name", email)
        
        if not email:
            return {"success": False, "message": "OAuth provider did not return an email."}
            
        # 3. Sync with local database (Hybrid Model)
        users = _load_users()
        if email not in users:
            user_profile = {
                "name": name,
                "email": email,
                "phone": "N/A (OIDC)",
                "password_hash": f"OIDC_EXTERNAL_ACCOUNT_{provider.upper()}",
                "role": "user",
                "provider": provider,
                "created_at": datetime.now().isoformat(),
            }
            users[email] = user_profile
            _save_users(users)
        
        stored = users[email]
        safe_profile = {k: v for k, v in stored.items() if k != "password_hash"}
        return {"success": True, "message": "OAuth login successful!", "user": safe_profile}
        
    except Exception as e:
        return {"success": False, "message": f"OAuth Error: {str(e)}"}

