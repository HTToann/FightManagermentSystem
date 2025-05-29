# FightManagermentSystem

A web-based fight event management system built with Python, Flask, and SQLAlchemy. This system helps organizers manage fight events, fighters, bookings, and related payment/integration workflows.

## Features

- Fight event scheduling and booking
- Fighter and match management
- Admin dashboard (Flask-Admin)
- User authentication (Flask-Login)
- Payment integration (VNPay)
- Media upload (Cloudinary)
- Modular API design for extensibility
- Alembic for database migrations

## Tech Stack

- Python 3.8+
- Flask
- Flask-Admin, Flask-Login, Flask-SQLAlchemy
- SQLAlchemy ORM
- PyMySQL (MySQL support)
- WTForms (forms handling)
- Cloudinary (media)
- VNPay API integration

## Project Structure

```
FightManagermentSystem/
├── fightBooking/
│   ├── admin.py           # Admin panel logic
│   ├── apis.py            # API endpoints
│   ├── configs.py         # Configuration
│   ├── dao.py             # Data access layer
│   ├── extensions.py      # Flask extensions
│   ├── index.py           # App entrypoint
│   ├── models.py          # Database models
│   ├── run.py             # Run server
│   ├── vnpay.py           # VNPay integration
│   ├── alembic.ini        # Alembic config
│   ├── alembic/           # Alembic migrations
│   ├── static/            # Static files
│   ├── templates/         # Jinja2 templates
│   └── vnpay_python/      # VNPay Python SDK or helpers
├── requirements.txt       # Python dependencies
├── .gitignore
└── README.md
```

[View all files in the fightBooking module →](https://github.com/HTToann/FightManagermentSystem/tree/main/fightBooking)

## Getting Started

### Prerequisites

- Python 3.8 or newer
- MySQL server
- Cloudinary account (for media)
- VNPay credentials (for payment integration)

### Setup Instructions

1. **Clone the repository**
   ```sh
   git clone https://github.com/HTToann/FightManagermentSystem.git
   cd FightManagermentSystem
   ```

2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure environment**
   - Set your database, Cloudinary, and VNPay credentials in `fightBooking/configs.py` or via environment variables as applicable.

4. **Database migrations**
   ```sh
   # Initialize Alembic if needed
   alembic upgrade head
   ```

5. **Run the application**
   ```sh
   python fightBooking/run.py
   ```

6. **Access**
   - Visit `http://localhost:5000` in your browser.

## Main Dependencies

See `requirements.txt` for the complete list. Key packages include:
- Flask, Flask-Admin, Flask-Login, Flask-SQLAlchemy
- SQLAlchemy
- WTForms
- Cloudinary
- VNPay API

## Contribution

Contributions are welcome! Please fork the repository and open a pull request.

## License

This project is provided for academic or demonstration purposes.
