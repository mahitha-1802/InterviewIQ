import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-interview-iq-9938")
    DATABASE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "interviewiq.db")
    ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "b'h7gR4k8j9H3sD2n8f1G0e7W5v8C3x2Z1a4Q5w6E7r8='")
