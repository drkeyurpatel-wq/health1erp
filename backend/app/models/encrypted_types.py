"""
SQLAlchemy TypeDecorator that transparently encrypts on write and decrypts on
read using Fernet field-level encryption (HIPAA / PHI compliance).
"""

from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

from app.core.encryption import get_encryptor


class EncryptedString(TypeDecorator):
    """A string column whose value is Fernet-encrypted at rest.

    Usage::

        class Patient(Base):
            phone = Column(EncryptedString(length=500), nullable=False)

    The *length* should be large enough to hold the Fernet ciphertext, which
    is roughly ``len(plaintext) * 4 / 3 + 100`` bytes.
    """

    impl = String
    cache_ok = True

    def __init__(self, length: int = 1024, **kwargs):
        super().__init__(length=length, **kwargs)

    # Value going INTO the database
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        encryptor = get_encryptor()
        return encryptor.encrypt(str(value))

    # Value coming OUT of the database
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        encryptor = get_encryptor()
        return encryptor.decrypt(value)
