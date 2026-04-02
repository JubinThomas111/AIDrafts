import hashlib
import secrets
import datetime
# testing logic to get an optimized output based on the prompts.
class SecurityManager:
    """Handles user authentication and secure token generation."""

    def __init__(self):
        self.user_db = {}  # Mock database: {username: hashed_password}
        self.active_tokens = {} # {token: expiry_timestamp}

    def hash_password(self, password):
        """Creates a secure SHA-256 hash of a password with a salt."""
        salt = "BR0ADC0M_2026_SALT"
        db_string = password + salt
        return hashlib.sha256(db_string.encode()).hexdigest()

    def register_user(self, username, password):
        """Hashes the password and saves the user to the mock DB."""
        hashed_pw = self.hash_password(password)
        self.user_db[username] = hashed_pw
        return f"User {username} registered successfully."

    def login(self, username, password):
        """Verifies password and generates a 32-character session token."""
        input_hash = self.hash_password(password)
        
        if self.user_db.get(username) == input_hash:
            token = secrets.token_hex(16)
            # Token valid for 1 hour
            expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
            self.active_tokens[token] = expiry
            return {"status": "success", "token": token}
        
        return {"status": "fail", "message": "Invalid credentials"}

    def validate_session(self, token):
        """Checks if a session token exists and has not expired."""
        if token in self.active_tokens:
            if datetime.datetime.now() < self.active_tokens[token]:
                return True
            else:
                del self.active_tokens[token] # Clean up expired
        return False
