# Django Communication Platform

A CRM-like communication platform built with Django REST Framework, featuring contact management, multi-channel communications, marketing campaigns, sales pipelines, and workflow automation.

## Features

- **Contact Management**: Store and organize contacts with custom fields
- **Multi-Channel Communications**: Email, SMS, WhatsApp integrations
- **Campaign Management**: Create and track marketing campaigns
- **Sales Pipelines**: Manage deals through customizable pipeline stages
- **Workflow Automation**: Trigger-based automation for repetitive tasks
- **REST API**: Full-featured API with JWT authentication
- **Task Queue**: Celery for background jobs and scheduled tasks
- **Admin Panel**: Django admin for platform management

## Tech Stack

- **Backend**: Django 5.1.5, Django REST Framework 3.15.2
- **Database**: PostgreSQL 16+
- **Cache/Queue**: Redis
- **Task Queue**: Celery with Redis broker
- **Authentication**: JWT (Simple JWT)
- **API Documentation**: Django REST Framework browsable API

## Project Structure

```
django-communication-platform/
├── config/                  # Project configuration
│   ├── settings/           # Environment-specific settings
│   │   ├── base.py        # Base settings
│   │   ├── dev.py         # Development settings
│   │   └── prod.py        # Production settings
│   ├── urls.py            # Main URL routing
│   ├── celery.py          # Celery configuration
│   ├── wsgi.py            # WSGI entry point
│   └── asgi.py            # ASGI entry point
├── apps/                   # Django applications
│   ├── accounts/          # User management
│   ├── contacts/          # Contact and organization management
│   ├── communications/    # Email, SMS, WhatsApp
│   ├── campaigns/         # Marketing campaigns
│   ├── pipelines/         # Sales pipeline
│   └── automations/       # Workflow automation
├── requirements/          # Python dependencies
│   ├── base.txt          # Base requirements
│   ├── dev.txt           # Development requirements
│   └── prod.txt          # Production requirements
└── manage.py             # Django management script
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Redis 7+

### 1. Clone and Setup Virtual Environment

```bash
cd /Users/sobral/Documents/AIOS/projetos/django-communication-platform
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements/dev.txt
```

### 3. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Database Setup

```bash
# Create PostgreSQL database
createdb communication_platform

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
# Terminal 1: Django development server
python manage.py runserver

# Terminal 2: Celery worker
celery -A config worker --loglevel=info

# Terminal 3: Celery beat (scheduler)
celery -A config beat --loglevel=info
```

### 7. Access the Platform

- **API**: http://localhost:8000/api/v1/
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/v1/ (browsable API)

## API Endpoints

### Authentication
- `POST /api/v1/auth/token/` - Obtain JWT token
- `POST /api/v1/auth/token/refresh/` - Refresh JWT token
- `POST /api/v1/auth/token/verify/` - Verify JWT token

### Contacts
- `GET /api/v1/contacts/` - List contacts
- `POST /api/v1/contacts/` - Create contact
- `GET /api/v1/contacts/{id}/` - Retrieve contact
- `PUT /api/v1/contacts/{id}/` - Update contact
- `DELETE /api/v1/contacts/{id}/` - Delete contact

### Communications
- `GET /api/v1/communications/` - List communications
- `POST /api/v1/communications/send-email/` - Send email
- `POST /api/v1/communications/send-sms/` - Send SMS
- `POST /api/v1/communications/send-whatsapp/` - Send WhatsApp

### Campaigns
- `GET /api/v1/campaigns/` - List campaigns
- `POST /api/v1/campaigns/` - Create campaign
- `POST /api/v1/campaigns/{id}/send/` - Send campaign

### Pipelines
- `GET /api/v1/pipelines/` - List pipelines
- `GET /api/v1/pipelines/{id}/deals/` - List deals in pipeline

### Automations
- `GET /api/v1/automations/` - List automations
- `POST /api/v1/automations/` - Create automation

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest apps/contacts/tests/test_models.py
```

## Code Quality

```bash
# Format code with black
black .

# Sort imports
isort .

# Lint with flake8
flake8 .

# Type checking
mypy apps/
```

## Deployment

### Production Checklist

1. Set `DJANGO_SETTINGS_MODULE=config.settings.prod`
2. Generate secure `SECRET_KEY`
3. Set `DEBUG=False`
4. Configure `ALLOWED_HOSTS`
5. Setup PostgreSQL database
6. Configure Redis for cache and Celery
7. Setup email backend (SMTP)
8. Configure cloud storage (AWS S3) for media files
9. Setup Sentry for error tracking
10. Run `python manage.py collectstatic`
11. Run migrations
12. Setup Gunicorn/uWSGI with Nginx

### Deploy with Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## Celery Tasks

The platform includes several scheduled tasks:

- **cleanup-old-sessions**: Daily at 2 AM
- **process-scheduled-campaigns**: Every 5 minutes
- **check-automation-triggers**: Every minute
- **update-campaign-analytics**: Every 15 minutes

## License

Proprietary - DYNEX Platform

## Support

For support and questions, contact: noreply@example.com
