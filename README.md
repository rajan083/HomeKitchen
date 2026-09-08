# HomeKitchen

A local food marketplace web app built with Flask. Vendors list homemade food items, consumers browse and order, and riders handle delivery — with UPI-based payments, wallet balances, and automatic commission splitting between vendor, rider, and platform.

## Features

- **Three user roles**: Consumer, Vendor, and Rider, each with their own registration/KYC flow and dashboard.
- **Vendor tools**: list items, manage stock, view orders, register business details with location.
- **Consumer flow**: browse/search items by region and category, place orders, pay via UPI QR code, track order history.
- **Rider flow**: KYC verification, view assigned deliveries, update delivery status.
- **Wallets**: every user has a wallet balance; money can be added or withdrawn via UPI, and completed orders automatically split payment between vendor, rider, and platform.
- **Admin panel**: verify pending vendor/rider KYC submissions.
- **Email notifications**: welcome emails, login alerts, order cancellations, delivery assignment, and profile update alerts (via Gmail SMTP).
- **Email verification**: token-based email confirmation before login is allowed.

## Tech Stack

- **Backend**: Flask, Flask-SQLAlchemy, Flask-Mail
- **Database**: PostgreSQL
- **Auth**: Werkzeug password hashing, Flask sessions
- **Payments**: UPI deep links + QR codes (`qrcode` library)
- **Config**: environment variables via `python-dotenv`

## Project Structure

```
HomeKitchen/
├── main.py              # Flask app, routes, business logic
├── models.py             # SQLAlchemy models (User, Order, Transaction, etc.)
├── config.py              # App configuration, loaded from environment variables
├── requirements.txt       # Python dependencies
├── .env                   # Local environment variables (not committed)
├── .gitignore
├── templates/              # Jinja2 HTML templates
└── static/
    ├── uploads/            # Item images
    ├── UserInfo/           # KYC documents, profile photos
    └── QrCode/             # Generated payment QR codes
```

## Prerequisites

- Python 3.10+
- PostgreSQL installed and running locally
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) generated (regular Gmail passwords won't work for SMTP)

## Setup

**1. Clone the repo and create a virtual environment**

```bash
git clone <your-repo-url>
cd HomeKitchen
python -m venv venv
```

Activate it:
- Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
- macOS/Linux: `source venv/bin/activate`

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Create the PostgreSQL database**

```sql
psql -U postgres -h localhost
CREATE DATABASE "HomeKitchen";
```

**4. Configure environment variables**

Create a `.env` file in the project root (see `.gitignore` — this file should never be committed):

```dotenv
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/HomeKitchen
SECRET_KEY=your-random-secret-key

MAIL_USERNAME=youraddress@gmail.com
MAIL_PASSWORD=your-16-char-gmail-app-password

ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-strong-admin-password

ADMIN_UPI_ID=yourupi@bank
```

**5. Run the app**

```bash
python main.py
```

On first run, `db.create_all()` builds all tables automatically. The app then starts on `http://127.0.0.1:5000` by default.

## Configuration Reference

| Variable | Purpose | Required |
|---|---|---|
| `DATABASE_URL` | Postgres connection string | Yes (falls back to a local default) |
| `SECRET_KEY` | Flask session signing key | Recommended for production |
| `MAIL_USERNAME` | Gmail address used to send notifications | Yes, for email features |
| `MAIL_PASSWORD` | Gmail App Password (not your regular password) | Yes, for email features |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Credentials for `/admin/login` | Yes, for admin panel |
| `ADMIN_UPI_ID` | Platform's UPI ID | Optional |

## Commission Structure

When a rider marks an order as delivered, the order amount is split automatically:
- **Vendor share**: remainder after rider + platform cuts
- **Rider commission**: configurable via `RIDER_COMMISSION_RATE` in `config.py` (default 10%)
- **Platform commission**: configurable via `PLATFORM_COMMISSION_RATE` in `config.py` (default 10%)

Each split is recorded as a `Transaction` and reflected in each party's wallet balance.

## Notes

- Uploaded KYC documents and profile photos are stored under `static/UserInfo/` and item images under `static/uploads/` — these are gitignored since they contain real user data.
- The in-memory `verification_tokens` dict resets on every server restart. For production use, move email verification tokens into the database.
- Debug mode is controlled by the `FLASK_DEBUG` environment variable (`True`/`False`); it's off by default.

## License

Add your license here.