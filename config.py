import os
from dotenv import load_dotenv

# Load variables from a local .env file (if present) into the process
# environment. In production (e.g. Render), real environment variables are
# set directly in the dashboard, and this call is a harmless no-op there.
load_dotenv()


class Config:
    """Application configuration, sourced from environment variables.

    On Render, set these under the Web Service's Environment tab.
    Locally, set them directly in your shell before running the app.
    """

    # ---- Core ----
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')

    # ---- Database ----
    _raw_db_url = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:root@localhost:5432/HomeKitchen'
    )
    if _raw_db_url.startswith('postgres://'):
        _raw_db_url = _raw_db_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = _raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---- Mail ----
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')

    # ---- Admin login ----
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

    # ---- Uploads ----
    UPLOAD_FOLDER_ITEM = 'static/uploads'
    UPLOAD_FOLDER = 'static/UserInfo'

    # ---- Commission rates ----
    RIDER_COMMISSION_RATE = 0.10
    PLATFORM_COMMISSION_RATE = 0.10
    ADMIN_UPI_ID = os.environ.get('ADMIN_UPI_ID', '6283060669@ptsbi')