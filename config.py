import os

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'git_webhook_secret_key'
    MONGO_URI = "mongodb+srv://a9756549615:dvPXhoiKNnSQ2q21@webhook.bjswhy4.mongodb.net/webhook-mongo?retryWrites=true&w=majority"
    WEBHOOK_TIMEOUT = 30  
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max payload size: 16 MB
    UI_UPDATE_INTERVAL = 15  # seconds
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'

