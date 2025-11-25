"""
Unit tests for utils/auth.py password hashing and verification.
"""

from utils.auth import hash_password, verify_password


class TestPasswordHashing:
    """Test password hashing and verification functions."""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_different_hashes(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "TestPassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Different hashes due to different salts
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test that verify_password returns True for correct password."""
        password = "CorrectPassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test that verify_password returns False for incorrect password."""
        password = "CorrectPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "Password123!"
        hashed = hash_password(password)

        assert verify_password("password123!", hashed) is False
        assert verify_password("PASSWORD123!", hashed) is False

    def test_hash_password_with_special_characters(self):
        """Test hashing password with special characters."""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_hash_password_unicode(self):
        """Test hashing password with unicode characters."""
        password = "Pässwörd123!🔒"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
        assert verify_password("Password123!🔒", hashed) is False

    def test_verify_password_empty_string(self):
        """Test that empty password doesn't match hashed password."""
        password = "RealPassword123!"
        hashed = hash_password(password)

        assert verify_password("", hashed) is False

    def test_hash_empty_password(self):
        """Test that empty password can be hashed (though not recommended)."""
        hashed = hash_password("")

        assert isinstance(hashed, str)
        assert verify_password("", hashed) is True
        assert verify_password("anything", hashed) is False
