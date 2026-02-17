# Support Ticket System

A full-stack web application for managing support tickets with AI-powered classification. The system automatically suggests ticket categories and priorities using OpenAI's GPT-4, helping users organize their support requests efficiently.

## Features

- **Ticket Management**: Create, view, update, and filter support tickets
- **AI Classification**: Automatic category and priority suggestions using GPT-4
- **Real-time Statistics**: Dashboard showing ticket metrics and breakdowns
- **Advanced Filtering**: Filter tickets by category, priority, status, and search terms
- **Responsive UI**: Modern React interface with real-time updates
- **Containerized Deployment**: Full Docker setup for easy deployment

## Architecture Overview

The system consists of three main components:

```
┌─────────────────┐
│  React Frontend │
│   (Port 3000)   │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐      ┌──────────────┐
│ Django Backend  │◄────►│  PostgreSQL  │
│   (Port 8000)   │      │  (Port 5432) │
└────────┬────────┘      └──────────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│   OpenAI API    │
│    (GPT-4)      │
└─────────────────┘
```

### Technology Stack

- **Backend**: Django 4.x, Django REST Framework, PostgreSQL
- **Frontend**: React 18.x, Axios
- **Database**: PostgreSQL 15.x
- **AI/LLM**: OpenAI GPT-4 API
- **Containerization**: Docker, Docker Compose

### Design Decisions

1. **LLM Integration**: We chose OpenAI's GPT-4 for ticket classification because:
   - High accuracy in understanding natural language descriptions
   - Reliable JSON response format for structured data
   - Strong context understanding for nuanced support issues
   - Well-documented API with good error handling

2. **Graceful Degradation**: The system works without an OpenAI API key by providing sensible defaults (category: "general", priority: "medium"), ensuring the application remains functional even if the LLM service is unavailable.

3. **Database-Level Aggregation**: Statistics are computed using PostgreSQL aggregation functions rather than Python loops, ensuring optimal performance even with large datasets.

4. **Docker Compose**: All services are containerized for consistent deployment across environments, with automatic database migrations on startup.

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- (Optional) OpenAI API key for AI-powered classification

### Running the Application

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd support-ticket-system
   ```

2. **Set up environment variables** (Optional but recommended):
   
   Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```
   
   **Note**: If you don't have an OpenAI API key, the system will still work but will use default values for ticket classification.

3. **Start all services**:
   ```bash
   docker-compose up --build
   ```
   
   This command will:
   - Build the Docker images for backend and frontend
   - Start PostgreSQL database
   - Run database migrations automatically
   - Start the Django backend on port 8000
   - Start the React frontend on port 3000

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/tickets/

5. **Stop the application**:
   ```bash
   docker-compose down
   ```

## Environment Variables

### Root `.env` File

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 classification | No | Falls back to defaults |

### Backend Environment Variables

The backend service uses these environment variables (configured in `docker-compose.yml`):

| Variable | Description | Default (Docker) |
|----------|-------------|------------------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@db:5432/ticketdb` |
| `OPENAI_API_KEY` | OpenAI API key | Inherited from root `.env` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost,127.0.0.1,backend` |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | `http://localhost:3000,http://127.0.0.1:3000` |
| `SECRET_KEY` | Django secret key | Auto-generated (change in production) |
| `DEBUG` | Django debug mode | `True` (set to `False` in production) |

### Frontend Environment Variables

| Variable | Description | Default (Docker) |
|----------|-------------|------------------|
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:8000` |

### Getting an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key and add it to your `.env` file
5. Restart the Docker containers: `docker-compose restart backend`

**Important**: Keep your API key secure and never commit it to version control.

## API Documentation

### Base URL

```
http://localhost:8000/api
```

### Endpoints

#### 1. Create Ticket

Create a new support ticket.

**Endpoint**: `POST /api/tickets/`

**Request Body**:
```json
{
  "title": "Cannot access my account",
  "description": "I've been trying to log in but keep getting an error message",
  "category": "account",
  "priority": "high"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "title": "Cannot access my account",
  "description": "I've been trying to log in but keep getting an error message",
  "category": "account",
  "priority": "high",
  "status": "open",
  "created_at": "2026-02-17T10:30:00Z"
}
```

**Field Constraints**:
- `title`: Required, max 200 characters
- `description`: Required, text field
- `category`: Required, choices: `billing`, `technical`, `account`, `general`
- `priority`: Required, choices: `low`, `medium`, `high`, `critical`
- `status`: Optional, choices: `open`, `in_progress`, `resolved`, `closed` (defaults to `open`)

---

#### 2. List Tickets

Retrieve all tickets with optional filtering.

**Endpoint**: `GET /api/tickets/`

**Query Parameters**:
- `category` (optional): Filter by category
- `priority` (optional): Filter by priority
- `status` (optional): Filter by status
- `search` (optional): Search in title and description (case-insensitive)

**Examples**:
```bash
# Get all tickets
GET /api/tickets/

# Filter by category
GET /api/tickets/?category=technical

# Filter by multiple criteria
GET /api/tickets/?category=technical&priority=high&status=open

# Search tickets
GET /api/tickets/?search=login

# Combine filters and search
GET /api/tickets/?category=account&search=password
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Cannot access my account",
    "description": "I've been trying to log in but keep getting an error message",
    "category": "account",
    "priority": "high",
    "status": "open",
    "created_at": "2026-02-17T10:30:00Z"
  },
  {
    "id": 2,
    "title": "Billing question",
    "description": "I was charged twice for my subscription",
    "category": "billing",
    "priority": "medium",
    "status": "open",
    "created_at": "2026-02-17T09:15:00Z"
  }
]
```

**Note**: Tickets are always returned ordered by `created_at` descending (newest first).

---

#### 3. Update Ticket

Update specific fields of a ticket (partial update).

**Endpoint**: `PATCH /api/tickets/{id}/`

**Request Body** (all fields optional):
```json
{
  "status": "in_progress",
  "priority": "critical"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Cannot access my account",
  "description": "I've been trying to log in but keep getting an error message",
  "category": "account",
  "priority": "critical",
  "status": "in_progress",
  "created_at": "2026-02-17T10:30:00Z"
}
```

---

#### 4. Get Ticket Statistics

Retrieve aggregated statistics about all tickets.

**Endpoint**: `GET /api/tickets/stats/`

**Response** (200 OK):
```json
{
  "total_tickets": 124,
  "open_tickets": 67,
  "avg_tickets_per_day": 8.3,
  "priority_breakdown": {
    "low": 30,
    "medium": 52,
    "high": 31,
    "critical": 11
  },
  "category_breakdown": {
    "billing": 28,
    "technical": 55,
    "account": 22,
    "general": 19
  }
}
```

**Fields**:
- `total_tickets`: Total count of all tickets
- `open_tickets`: Count of tickets with status "open"
- `avg_tickets_per_day`: Average tickets created per day since the first ticket
- `priority_breakdown`: Count of tickets grouped by priority
- `category_breakdown`: Count of tickets grouped by category

---

#### 5. Classify Ticket (AI-Powered)

Get AI-suggested category and priority for a ticket description.

**Endpoint**: `POST /api/tickets/classify/`

**Request Body**:
```json
{
  "description": "I was charged twice for my subscription this month"
}
```

**Response** (200 OK) - With OpenAI API key:
```json
{
  "suggested_category": "billing",
  "suggested_priority": "high"
}
```

**Response** (200 OK) - Without OpenAI API key (fallback):
```json
{
  "suggested_category": "general",
  "suggested_priority": "medium",
  "note": "Using default values (LLM unavailable)"
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "Description is required"
}
```

**Note**: This endpoint uses OpenAI's GPT-4 to analyze the description and suggest appropriate category and priority. If the API key is not configured or the service is unavailable, it returns sensible defaults.

---

### Error Responses

All endpoints return appropriate HTTP status codes and error messages:

**400 Bad Request** - Invalid input data:
```json
{
  "title": ["This field is required."],
  "category": ["\"invalid\" is not a valid choice."]
}
```

**404 Not Found** - Resource not found:
```json
{
  "detail": "Not found."
}
```

**500 Internal Server Error** - Server error:
```json
{
  "error": "An unexpected error occurred"
}
```

## Development

### Running Without Docker

#### Backend

1. Install Python 3.11+
2. Create virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables (copy from `.env.example`)
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Start server:
   ```bash
   python manage.py runserver
   ```

#### Frontend

1. Install Node.js 18+
2. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
3. Set up environment variables (copy from `.env.example`)
4. Start development server:
   ```bash
   npm start
   ```

### Running Tests

#### Backend Tests
```bash
docker-compose exec backend python manage.py test
```

#### Frontend Tests
```bash
docker-compose exec frontend npm test
```

## Project Structure

```
support-ticket-system/
├── backend/
│   ├── config/              # Django project settings
│   ├── tickets/             # Main application
│   │   ├── models.py        # Ticket data model
│   │   ├── serializers.py   # API serializers
│   │   ├── views.py         # API endpoints
│   │   ├── llm_service.py   # OpenAI integration
│   │   └── tests.py         # Unit tests
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile
│   └── entrypoint.sh
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── TicketForm.js
│   │   │   ├── TicketList.js
│   │   │   ├── TicketCard.js
│   │   │   └── StatsPanel.js
│   │   ├── api/             # API client
│   │   └── App.js           # Main app component
│   ├── package.json         # Node dependencies
│   └── Dockerfile
├── docker-compose.yml       # Docker orchestration
├── .env.example             # Environment template
└── README.md
```

## Troubleshooting

### Database Connection Issues

If you see database connection errors:
```bash
# Ensure PostgreSQL is running
docker-compose ps

# Check database logs
docker-compose logs db

# Restart services
docker-compose restart
```

### Frontend Can't Reach Backend

If the frontend shows connection errors:
1. Verify backend is running: http://localhost:8000/api/tickets/
2. Check CORS settings in `backend/config/settings.py`
3. Ensure `REACT_APP_API_URL` is set correctly

### LLM Classification Not Working

If ticket classification returns default values:
1. Verify `OPENAI_API_KEY` is set in `.env`
2. Check API key is valid at https://platform.openai.com/api-keys
3. Restart backend: `docker-compose restart backend`
4. Check backend logs: `docker-compose logs backend`

### Port Already in Use

If ports 3000, 8000, or 5432 are already in use:
```bash
# Stop conflicting services or modify ports in docker-compose.yml
# Then restart
docker-compose down
docker-compose up --build
```

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]
