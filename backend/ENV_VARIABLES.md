# Environment Variables Documentation

This document describes all environment variables used by the Support Ticket System backend.

## Required Variables

### DATABASE_URL
**Required for production deployment**

PostgreSQL database connection string.

- **Format**: `postgresql://username:password@host:port/database_name`
- **Example**: `postgresql://ticketuser:secretpass@localhost:5432/ticketdb`
- **Default**: Falls back to SQLite (`db.sqlite3`) if not set
- **Requirements**: 10.1, 10.2

**Docker Compose Example**:
```yaml
DATABASE_URL=postgresql://postgres:postgres@db:5432/ticketdb
```

### OPENAI_API_KEY
**Required for LLM classification feature**

OpenAI API key for GPT-4 based ticket classification.

- **Format**: String (starts with `sk-`)
- **Example**: `sk-proj-abc123...`
- **Default**: System works without it, but uses fallback values (category: general, priority: medium)
- **Get Key**: https://platform.openai.com/api-keys
- **Requirements**: 6.5, 10.6

**Note**: The application gracefully degrades when this key is not provided. Ticket submission still works, but automatic classification suggestions will use default values.

### ALLOWED_HOSTS
**Required for production deployment**

Comma-separated list of host/domain names that Django can serve.

- **Format**: Comma-separated string
- **Example**: `localhost,127.0.0.1,api.example.com,www.example.com`
- **Default**: `localhost,127.0.0.1,testserver`
- **Requirements**: 10.1, 10.2

**Security Note**: In production, set this to your actual domain names only.

## Optional Variables

### CORS_ALLOWED_ORIGINS
**Optional - defaults to localhost**

Comma-separated list of origins allowed to make cross-origin requests.

- **Format**: Comma-separated URLs
- **Example**: `http://localhost:3000,https://app.example.com`
- **Default**: `http://localhost:3000,http://127.0.0.1:3000`
- **Requirements**: 10.2

**Note**: Must include the protocol (http:// or https://)

### SECRET_KEY
**Required for production - has default for development**

Django secret key used for cryptographic signing.

- **Format**: String (50+ random characters)
- **Default**: Development key (insecure, do not use in production)
- **Generate**: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`

**Security Warning**: Never commit the production secret key to version control!

### DEBUG
**Optional - defaults to True**

Enable/disable Django debug mode.

- **Format**: Boolean (`True` or `False`)
- **Default**: `True`
- **Production**: Must be set to `False`

**Security Warning**: Never run with DEBUG=True in production!

## Setup Instructions

### Development Setup

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set your values:
   - Leave `DATABASE_URL` commented out to use SQLite
   - Add your `OPENAI_API_KEY` if you want LLM classification
   - Keep default values for other variables

3. Load environment variables (if using python-dotenv):
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

### Docker Compose Setup

Environment variables are configured in `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/ticketdb
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ALLOWED_HOSTS=localhost,127.0.0.1,backend
      - CORS_ALLOWED_ORIGINS=http://localhost:3000
```

Create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_actual_key_here
```

### Production Deployment

1. Set all required environment variables in your hosting platform
2. Generate a new `SECRET_KEY`
3. Set `DEBUG=False`
4. Set `ALLOWED_HOSTS` to your actual domain(s)
5. Set `CORS_ALLOWED_ORIGINS` to your frontend URL(s)
6. Use a secure PostgreSQL database with strong credentials
7. Never commit `.env` files to version control

## Validation

To verify your environment variables are loaded correctly:

```bash
python manage.py shell
```

```python
from django.conf import settings
print(f"Database: {settings.DATABASES['default']['ENGINE']}")
print(f"Allowed Hosts: {settings.ALLOWED_HOSTS}")
print(f"CORS Origins: {settings.CORS_ALLOWED_ORIGINS}")
```

## Troubleshooting

### Database Connection Issues
- Verify `DATABASE_URL` format is correct
- Ensure PostgreSQL is running and accessible
- Check username, password, host, and port
- Verify database exists

### LLM Classification Not Working
- Verify `OPENAI_API_KEY` is set correctly
- Check API key is valid and has credits
- Review backend logs for error messages
- System will use fallback values if LLM fails

### CORS Errors
- Verify frontend URL is in `CORS_ALLOWED_ORIGINS`
- Include the protocol (http:// or https://)
- Restart backend after changing CORS settings
- Check browser console for specific CORS error messages
