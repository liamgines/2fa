import os

class Config:
    SECRET_KEY = os.environ.get("2FA_ATTACK_KEY")
