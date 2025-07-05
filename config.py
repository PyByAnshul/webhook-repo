import os

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'git_webhook_secret_key'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/git_webhook_db'
    WEBHOOK_TIMEOUT = 30  
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max payload size: 16 MB
    UI_UPDATE_INTERVAL = 15  # seconds
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'

