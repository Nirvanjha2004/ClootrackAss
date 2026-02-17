# Design Document: Support Ticket System

## Overview

The Support Ticket System is a full-stack web application that enables users to submit, manage, and analyze support tickets. The system consists of three main components:

1. **Django REST Framework Backend**: Provides RESTful APIs for ticket CRUD operations, filtering, statistics, and LLM-based classification
2. **React Frontend**: Delivers an interactive user interface for ticket management with real-time LLM suggestions
3. **PostgreSQL Database**: Stores ticket data with enforced constraints

The key differentiator is the LLM integration that automatically suggests ticket categories and priorities based on natural language descriptions, improving data quality and user experience.

## Architecture

### System Components

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
│   LLM API       │
│ (OpenAI/etc)    │
└─────────────────┘
```

### Technology Stack

- **Backend**: Django 4.x, Django REST Framework, psycopg2
- **Frontend**: React 18.x, Axios for HTTP requests
- **Database**: PostgreSQL 15.x
- **LLM**: OpenAI GPT-4 API (configurable via environment variable)
- **Containerization**: Docker, Docker Compose

### Communication Flow

1. User enters ticket description in React form
2. Frontend calls `/api/tickets/classify/` with description
3. Backend sends description to LLM API with classification prompt
4. LLM returns suggested category and priority
5. Frontend pre-fills form fields with suggestions
6. User reviews/modifies and submits ticket
7. Backend validates and stores ticket in PostgreSQL
8. Frontend refreshes ticket list and stats

## Components and Interfaces

### Backend Components

#### 1. Ticket Model (`tickets/models.py`)

```python
class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ('billing', 'Billing'),
        ('technical', 'Technical'),
        ('account', 'Account'),
        ('general', 'General'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 2. Ticket Serializer (`tickets/serializers.py`)

```python
class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'title', 'description', 'category', 'priority', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']
```

#### 3. Ticket ViewSet (`tickets/views.py`)

Provides CRUD operations and filtering:
- `list()`: GET /api/tickets/ with query params for filtering
- `create()`: POST /api/tickets/
- `partial_update()`: PATCH /api/tickets/<id>/

Query parameter handling:
- `category`, `priority`, `status`: Exact match filters
- `search`: Case-insensitive search in title and description using Q objects

#### 4. Stats View (`tickets/views.py`)

```python
@api_view(['GET'])
def ticket_stats(request):
    # Use Django ORM aggregation
    total_tickets = Ticket.objects.count()
    open_tickets = Ticket.objects.filter(status='open').count()
    
    # Calculate avg tickets per day
    earliest = Ticket.objects.aggregate(Min('created_at'))['created_at__min']
    if earliest:
        days = (timezone.now() - earliest).days + 1
        avg_per_day = total_tickets / days
    else:
        avg_per_day = 0
    
    # Priority breakdown using aggregation
    priority_breakdown = dict(
        Ticket.objects.values('priority')
        .annotate(count=Count('id'))
        .values_list('priority', 'count')
    )
    
    # Category breakdown using aggregation
    category_breakdown = dict(
        Ticket.objects.values('category')
        .annotate(count=Count('id'))
        .values_list('category', 'count')
    )
    
    return Response({
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'avg_tickets_per_day': round(avg_per_day, 1),
        'priority_breakdown': priority_breakdown,
        'category_breakdown': category_breakdown,
    })
```

#### 5. LLM Classification Service (`tickets/llm_service.py`)

```python
import openai
import os

class LLMClassifier:
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
    
    def classify_ticket(self, description):
        if not self.api_key:
            return None
        
        prompt = """Analyze this support ticket description and suggest:
1. Category (billing, technical, account, or general)
2. Priority (low, medium, high, or critical)

Description: {description}

Respond in JSON format:
{{"category": "...", "priority": "..."}}"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a support ticket classifier."},
                    {"role": "user", "content": prompt.format(description=description)}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'suggested_category': result['category'],
                'suggested_priority': result['priority']
            }
        except Exception as e:
            # Log error but don't fail
            print(f"LLM classification error: {e}")
            return None
```

#### 6. Classification View (`tickets/views.py`)

```python
@api_view(['POST'])
def classify_ticket(request):
    description = request.data.get('description', '')
    
    if not description:
        return Response(
            {'error': 'Description is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    classifier = LLMClassifier()
    result = classifier.classify_ticket(description)
    
    if result:
        return Response(result)
    else:
        # Graceful fallback
        return Response(
            {
                'suggested_category': 'general',
                'suggested_priority': 'medium',
                'note': 'Using default values (LLM unavailable)'
            }
        )
```

### Frontend Components

#### 1. TicketForm Component

Responsibilities:
- Render title input, description textarea, category/priority dropdowns
- Call classify API when description changes (debounced)
- Show loading state during classification
- Pre-fill dropdowns with LLM suggestions
- Submit ticket to backend
- Clear form on success

State:
- `title`, `description`, `category`, `priority`
- `isClassifying`: boolean for loading state
- `suggestions`: LLM response

#### 2. TicketList Component

Responsibilities:
- Fetch and display tickets from backend
- Render filter controls (category, priority, status, search)
- Apply filters via query parameters
- Show ticket cards with truncated descriptions
- Handle ticket status updates

State:
- `tickets`: array of ticket objects
- `filters`: object with category, priority, status, search

#### 3. TicketCard Component

Responsibilities:
- Display individual ticket information
- Provide status change dropdown
- Send PATCH request on status change

Props:
- `ticket`: ticket object
- `onUpdate`: callback for refresh

#### 4. StatsPanel Component

Responsibilities:
- Fetch stats from `/api/tickets/stats/`
- Display metrics in organized layout
- Auto-refresh when new ticket is created

State:
- `stats`: stats object from API

#### 5. App Component

Responsibilities:
- Compose all components
- Manage global state (if needed)
- Handle ticket creation callback to refresh list and stats

## Data Models

### Ticket Entity

| Field | Type | Constraints | Default |
|-------|------|-------------|---------|
| id | Integer | Primary Key, Auto-increment | - |
| title | String | Max 200 chars, Required | - |
| description | Text | Required | - |
| category | String | Choices: billing, technical, account, general | - |
| priority | String | Choices: low, medium, high, critical | - |
| status | String | Choices: open, in_progress, resolved, closed | 'open' |
| created_at | DateTime | Auto-set on creation | now() |

### Database Indexes

- Primary key on `id`
- Index on `created_at` for sorting and date calculations
- Index on `status` for filtering open tickets
- Composite index on `(category, priority, status)` for multi-filter queries

### API Request/Response Formats

#### POST /api/tickets/
Request:
```json
{
  "title": "Cannot access my account",
  "description": "I've been trying to log in but keep getting an error",
  "category": "account",
  "priority": "high"
}
```

Response (201):
```json
{
  "id": 123,
  "title": "Cannot access my account",
  "description": "I've been trying to log in but keep getting an error",
  "category": "account",
  "priority": "high",
  "status": "open",
  "created_at": "2026-02-17T10:30:00Z"
}
```

#### GET /api/tickets/?category=technical&search=error
Response (200):
```json
[
  {
    "id": 123,
    "title": "Cannot access my account",
    "description": "I've been trying to log in but keep getting an error",
    "category": "technical",
    "priority": "high",
    "status": "open",
    "created_at": "2026-02-17T10:30:00Z"
  }
]
```

#### POST /api/tickets/classify/
Request:
```json
{
  "description": "I was charged twice for my subscription"
}
```

Response (200):
```json
{
  "suggested_category": "billing",
  "suggested_priority": "high"
}
```

#### GET /api/tickets/stats/
Response (200):
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


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Backend Properties

**Property 1: Field constraint validation**
*For any* ticket data submitted to the API, if the title exceeds 200 characters OR the description is empty OR the category/priority/status is not in the valid choices, then the API should reject the request with an error response.
**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**

**Property 2: Default status assignment**
*For any* ticket created without an explicit status value, the ticket should have status='open' after creation.
**Validates: Requirements 1.6**

**Property 3: Automatic timestamp assignment**
*For any* ticket created, the created_at field should be set to a timestamp within a few seconds of the current time.
**Validates: Requirements 1.7**

**Property 4: Ticket creation round-trip**
*For any* valid ticket data submitted via POST /api/tickets/, querying the database immediately after should return a ticket with the same title, description, category, and priority values.
**Validates: Requirements 2.1, 2.3**

**Property 5: Invalid ticket rejection**
*For any* invalid ticket data (missing required fields, invalid enum values, title too long), the POST /api/tickets/ endpoint should return an error status code (4xx) and not create a ticket in the database.
**Validates: Requirements 2.2**

**Property 6: Ticket ordering**
*For any* set of tickets in the database, the GET /api/tickets/ endpoint should return them ordered by created_at descending (newest first).
**Validates: Requirements 3.1**

**Property 7: Single filter correctness**
*For any* filter parameter (category, priority, or status) and any value, all tickets returned by GET /api/tickets/ should have that field matching the filter value.
**Validates: Requirements 3.2, 3.3, 3.4**

**Property 8: Search filter correctness**
*For any* search term provided via ?search= parameter, all tickets returned should contain that term (case-insensitive) in either the title or description field.
**Validates: Requirements 3.5**

**Property 9: Combined filter correctness**
*For any* combination of filter parameters (category, priority, status, search), all tickets returned should satisfy all filter conditions simultaneously.
**Validates: Requirements 3.6**

**Property 10: Ticket update round-trip**
*For any* valid update data sent via PATCH /api/tickets/<id>/, querying the ticket immediately after should return the updated field values.
**Validates: Requirements 4.1, 4.3**

**Property 11: Invalid update rejection**
*For any* invalid update data (invalid enum values, title too long), the PATCH endpoint should return an error status code and the ticket should remain unchanged in the database.
**Validates: Requirements 4.2**

**Property 12: Total ticket count accuracy**
*For any* state of the database, the total_tickets value from GET /api/tickets/stats/ should equal the actual count of all tickets in the database.
**Validates: Requirements 5.1**

**Property 13: Open ticket count accuracy**
*For any* state of the database, the open_tickets value from GET /api/tickets/stats/ should equal the count of tickets with status='open'.
**Validates: Requirements 5.2**

**Property 14: Average tickets per day calculation**
*For any* state of the database with at least one ticket, the avg_tickets_per_day value should equal the total ticket count divided by the number of days between the earliest ticket's created_at and now (inclusive).
**Validates: Requirements 5.3**

**Property 15: Breakdown aggregation accuracy**
*For any* state of the database, the sum of all values in priority_breakdown should equal total_tickets, and the sum of all values in category_breakdown should equal total_tickets.
**Validates: Requirements 5.4, 5.5**

**Property 16: LLM classification response format**
*For any* successful LLM API response, the POST /api/tickets/classify/ endpoint should return a JSON object containing suggested_category and suggested_priority fields with valid enum values.
**Validates: Requirements 6.2**

### Frontend Properties

Most frontend requirements are specific UI behaviors that are best tested through example-based tests rather than universal properties. The frontend testing strategy will focus on:

- Component rendering tests (forms, lists, stats display)
- User interaction tests (form submission, filtering, status updates)
- API integration tests (mocking backend responses)
- State management tests (form clearing, auto-refresh)

## Error Handling

### Backend Error Handling

1. **Database Errors**
   - Catch database connection failures and return 503 Service Unavailable
   - Log database errors for debugging
   - Use database transactions for data consistency

2. **Validation Errors**
   - Return 400 Bad Request with detailed error messages
   - Use Django REST Framework's built-in validation
   - Provide field-specific error messages

3. **LLM API Errors**
   - Catch network timeouts and connection errors
   - Catch JSON parsing errors from malformed responses
   - Return graceful fallback values (default category/priority)
   - Log LLM errors but don't fail ticket submission
   - Include a note in response when using fallback values

4. **Not Found Errors**
   - Return 404 Not Found for invalid ticket IDs
   - Provide clear error messages

### Frontend Error Handling

1. **API Request Failures**
   - Display user-friendly error messages
   - Show retry options for failed requests
   - Maintain form data on submission failure

2. **LLM Classification Failures**
   - Show a subtle message if classification fails
   - Allow form submission to proceed with manual selection
   - Don't block user workflow

3. **Network Errors**
   - Display connection error messages
   - Provide offline indicators
   - Cache data when possible

## Testing Strategy

### Backend Testing

The backend will use a dual testing approach combining unit tests and property-based tests:

**Unit Tests** (using Django's TestCase):
- Test specific examples of ticket creation, updates, filtering
- Test edge cases: empty database, single ticket, boundary values
- Test error conditions: invalid data, missing fields
- Test LLM integration with mocked API responses
- Test stats calculations with known data sets

**Property-Based Tests** (using Hypothesis):
- Minimum 100 iterations per property test
- Each test tagged with: **Feature: support-ticket-system, Property N: [property text]**
- Generate random ticket data to test validation properties
- Generate random filter combinations to test query properties
- Generate random database states to test stats properties

**Test Organization**:
```
backend/
  tickets/
    tests/
      test_models.py          # Model validation tests
      test_views.py           # API endpoint tests
      test_properties.py      # Property-based tests
      test_llm_service.py     # LLM integration tests
```

**Key Testing Focus**:
- Database-level constraint enforcement
- ORM aggregation correctness (no Python loops in stats)
- Filter combination logic
- LLM error handling and fallback behavior

### Frontend Testing

The frontend will use example-based tests with React Testing Library:

**Component Tests**:
- Render tests for all components
- User interaction tests (form input, button clicks, dropdown changes)
- API integration tests with mocked axios responses
- State management tests (form clearing, list updates)

**Integration Tests**:
- End-to-end ticket creation flow
- Filter and search functionality
- Stats refresh on ticket creation
- Status update workflow

**Test Organization**:
```
frontend/
  src/
    components/
      __tests__/
        TicketForm.test.js
        TicketList.test.js
        TicketCard.test.js
        StatsPanel.test.js
```

### Docker Testing

**Container Tests**:
- Verify all services start successfully
- Verify database migrations run automatically
- Verify environment variables are passed correctly
- Verify service dependencies and startup order
- Test with and without LLM API key

**Integration Tests**:
- Full application smoke test after docker-compose up
- Verify frontend can reach backend
- Verify backend can reach database
- Test complete ticket creation workflow

### Testing Commands

```bash
# Backend tests
docker-compose exec backend python manage.py test

# Backend property tests specifically
docker-compose exec backend python manage.py test tickets.tests.test_properties

# Frontend tests
docker-compose exec frontend npm test

# Full integration test
docker-compose up --build
# Then run smoke tests against running services
```

### Property-Based Testing Configuration

Each property test will:
1. Use Hypothesis library for Python backend tests
2. Run minimum 100 iterations with random data
3. Include a comment tag: `# Feature: support-ticket-system, Property N: [property text]`
4. Reference the specific requirements being validated
5. Use appropriate strategies for generating test data:
   - `text()` for descriptions
   - `integers()` for IDs
   - `sampled_from()` for enum choices
   - `datetimes()` for timestamps
   - `builds()` for complex objects

Example property test structure:
```python
from hypothesis import given, strategies as st
from hypothesis.extra.django import TestCase

class TicketPropertyTests(TestCase):
    @given(
        title=st.text(min_size=1, max_size=200),
        description=st.text(min_size=1),
        category=st.sampled_from(['billing', 'technical', 'account', 'general']),
        priority=st.sampled_from(['low', 'medium', 'high', 'critical'])
    )
    def test_property_4_ticket_creation_round_trip(self, title, description, category, priority):
        # Feature: support-ticket-system, Property 4: Ticket creation round-trip
        # Validates: Requirements 2.1, 2.3
        
        # Create ticket via API
        response = self.client.post('/api/tickets/', {
            'title': title,
            'description': description,
            'category': category,
            'priority': priority
        })
        
        # Query database
        ticket = Ticket.objects.get(id=response.data['id'])
        
        # Verify round-trip
        self.assertEqual(ticket.title, title)
        self.assertEqual(ticket.description, description)
        self.assertEqual(ticket.category, category)
        self.assertEqual(ticket.priority, priority)
```
