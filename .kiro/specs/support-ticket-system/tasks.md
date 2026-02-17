# Implementation Plan: Support Ticket System

## Overview

This implementation plan breaks down the Support Ticket System into discrete, incremental tasks. The approach follows a bottom-up strategy: set up infrastructure first, implement backend APIs with database models, then build the frontend, and finally integrate everything with Docker.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create backend directory with Django project structure
  - Create frontend directory with React app structure
  - Set up requirements.txt for Django (Django, djangorestframework, psycopg2-binary, django-cors-headers, python-dotenv, openai)
  - Set up package.json for React (react, react-dom, axios)
  - Create .gitignore files for both backend and frontend
  - _Requirements: 10.1, 10.2, 10.3_

- [x] 2. Implement Ticket model and database schema
  - [x] 2.1 Create Django app 'tickets'
    - Run django-admin startapp tickets
    - Add to INSTALLED_APPS in settings.py
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [x] 2.2 Define Ticket model with all fields and constraints
    - Create model with CharField for title (max_length=200)
    - Add TextField for description
    - Add CharField with choices for category, priority, status
    - Add DateTimeField with auto_now_add for created_at
    - Set default='open' for status field
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8_
  
  - [ ]* 2.3 Write property test for field validation
    - **Property 1: Field constraint validation**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
  
  - [ ]* 2.4 Write property test for default status
    - **Property 2: Default status assignment**
    - **Validates: Requirements 1.6**
  
  - [ ]* 2.5 Write property test for automatic timestamp
    - **Property 3: Automatic timestamp assignment**
    - **Validates: Requirements 1.7**

- [x] 3. Create ticket serializer and basic CRUD views
  - [x] 3.1 Implement TicketSerializer
    - Create serializer with all model fields
    - Set id and created_at as read-only
    - Add validation for required fields
    - _Requirements: 2.1, 2.2_
  
  - [x] 3.2 Implement TicketViewSet with list, create, partial_update
    - Create ViewSet with queryset and serializer
    - Implement list() method with ordering by -created_at
    - Implement create() method returning 201 on success
    - Implement partial_update() method for PATCH requests
    - _Requirements: 2.1, 2.2, 3.1, 4.1, 4.2_
  
  - [x] 3.3 Configure URL routing for ticket endpoints
    - Set up router for /api/tickets/
    - Register TicketViewSet with router
    - _Requirements: 2.1, 3.1, 4.1_
  
  - [ ]* 3.4 Write property test for ticket creation round-trip
    - **Property 4: Ticket creation round-trip**
    - **Validates: Requirements 2.1, 2.3**
  
  - [ ]* 3.5 Write property test for invalid ticket rejection
    - **Property 5: Invalid ticket rejection**
    - **Validates: Requirements 2.2**
  
  - [ ]* 3.6 Write property test for ticket update round-trip
    - **Property 10: Ticket update round-trip**
    - **Validates: Requirements 4.1, 4.3**
  
  - [ ]* 3.7 Write property test for invalid update rejection
    - **Property 11: Invalid update rejection**
    - **Validates: Requirements 4.2**

- [-] 4. Implement filtering and search functionality
  - [x] 4.1 Add filter backends to TicketViewSet
    - Override get_queryset() to handle query parameters
    - Implement category, priority, status exact filters
    - Implement search filter using Q objects for title and description
    - Handle multiple filters in combination
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6_
  
  - [ ]* 4.2 Write property test for ticket ordering
    - **Property 6: Ticket ordering**
    - **Validates: Requirements 3.1**
  
  - [ ]* 4.3 Write property test for single filter correctness
    - **Property 7: Single filter correctness**
    - **Validates: Requirements 3.2, 3.3, 3.4**
  
  - [ ]* 4.4 Write property test for search filter correctness
    - **Property 8: Search filter correctness**
    - **Validates: Requirements 3.5**
  
  - [ ]* 4.5 Write property test for combined filter correctness
    - **Property 9: Combined filter correctness**
    - **Validates: Requirements 3.6**

- [x] 5. Implement statistics endpoint with database aggregation
  - [x] 5.1 Create ticket_stats view function
    - Use Ticket.objects.count() for total_tickets
    - Use filter(status='open').count() for open_tickets
    - Calculate avg_tickets_per_day using aggregate(Min('created_at'))
    - Use values('priority').annotate(count=Count('id')) for priority_breakdown
    - Use values('category').annotate(count=Count('id')) for category_breakdown
    - Return JSON response with all stats
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_
  
  - [x] 5.2 Configure URL routing for stats endpoint
    - Add route for GET /api/tickets/stats/
    - _Requirements: 5.1_
  
  - [ ]* 5.3 Write property test for total ticket count accuracy
    - **Property 12: Total ticket count accuracy**
    - **Validates: Requirements 5.1**
  
  - [ ]* 5.4 Write property test for open ticket count accuracy
    - **Property 13: Open ticket count accuracy**
    - **Validates: Requirements 5.2**
  
  - [ ]* 5.5 Write property test for average tickets per day calculation
    - **Property 14: Average tickets per day calculation**
    - **Validates: Requirements 5.3**
  
  - [ ]* 5.6 Write property test for breakdown aggregation accuracy
    - **Property 15: Breakdown aggregation accuracy**
    - **Validates: Requirements 5.4, 5.5**

- [x] 6. Implement LLM classification service
  - [x] 6.1 Create LLMClassifier class in llm_service.py
    - Initialize with API key from environment variable OPENAI_API_KEY
    - Implement classify_ticket() method
    - Create prompt asking for category and priority in JSON format
    - Call OpenAI API with gpt-4 model
    - Parse JSON response and return suggested_category and suggested_priority
    - Handle exceptions gracefully (network errors, JSON parsing errors)
    - Return None on any error
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x] 6.2 Create classify_ticket view function
    - Accept POST request with description field
    - Validate description is not empty
    - Call LLMClassifier.classify_ticket()
    - Return suggestions if successful
    - Return graceful fallback (general/medium) if LLM fails
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [x] 6.3 Configure URL routing for classify endpoint
    - Add route for POST /api/tickets/classify/
    - _Requirements: 6.1_
  
  - [ ]* 6.4 Write unit tests for LLM service with mocked API
    - Test successful classification
    - Test network error handling
    - Test invalid JSON response handling
    - Test missing API key handling
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ]* 6.5 Write property test for LLM classification response format
    - **Property 16: LLM classification response format**
    - **Validates: Requirements 6.2**

- [x] 7. Configure Django settings and CORS
  - [x] 7.1 Update settings.py for production readiness
    - Configure DATABASES to use PostgreSQL with environment variables
    - Add 'rest_framework' and 'corsheaders' to INSTALLED_APPS
    - Configure CORS_ALLOWED_ORIGINS for frontend
    - Add corsheaders middleware
    - Set ALLOWED_HOSTS from environment variable
    - Configure static files
    - _Requirements: 10.1, 10.2_
  
  - [x] 7.2 Create environment variable template
    - Document required variables: DATABASE_URL, OPENAI_API_KEY, ALLOWED_HOSTS
    - _Requirements: 6.5, 10.6_

- [x] 8. Checkpoint - Ensure backend tests pass
  - Run python manage.py test
  - Verify all API endpoints work correctly
  - Ensure database migrations are created and applied
  - Test with and without OPENAI_API_KEY set

- [x] 9. Implement React TicketForm component
  - [x] 9.1 Create TicketForm component with form fields
    - Add title input with maxLength={200} and required
    - Add description textarea with required
    - Add category dropdown with all valid choices
    - Add priority dropdown with all valid choices
    - Add submit button
    - Manage form state with useState
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [x] 9.2 Implement LLM classification integration
    - Add useEffect to call /api/tickets/classify/ when description changes (debounced)
    - Set isClassifying state during API call
    - Display loading indicator when isClassifying is true
    - Pre-fill category and priority dropdowns with suggestions
    - Allow user to override suggestions
    - _Requirements: 7.4, 7.5, 7.6, 7.10_
  
  - [x] 9.3 Implement form submission
    - Handle form submit event
    - POST data to /api/tickets/
    - Clear form on success
    - Call onTicketCreated callback to refresh list
    - Display error messages on failure
    - _Requirements: 7.7, 7.8, 7.9_
  
  - [ ]* 9.4 Write component tests for TicketForm
    - Test form rendering with all fields
    - Test LLM classification call on description change
    - Test form submission
    - Test form clearing on success
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10_

- [x] 10. Implement React TicketList and TicketCard components
  - [x] 10.1 Create TicketCard component
    - Display ticket title, truncated description, category, priority, status, timestamp
    - Add status dropdown for changing ticket status
    - Handle status change with PATCH request to /api/tickets/<id>/
    - Call onUpdate callback after successful update
    - _Requirements: 8.2, 8.7, 8.8_
  
  - [x] 10.2 Create TicketList component
    - Fetch tickets from /api/tickets/ on mount
    - Display tickets using TicketCard components
    - Add filter controls for category, priority, status
    - Add search input
    - Update API call with query parameters when filters change
    - Handle ticket updates by refreshing list
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_
  
  - [ ]* 10.3 Write component tests for TicketList and TicketCard
    - Test ticket list rendering
    - Test filter functionality
    - Test search functionality
    - Test status update
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

- [x] 11. Implement React StatsPanel component
  - [x] 11.1 Create StatsPanel component
    - Fetch stats from /api/tickets/stats/ on mount
    - Display total_tickets, open_tickets, avg_tickets_per_day
    - Display priority_breakdown as a list or chart
    - Display category_breakdown as a list or chart
    - Accept refreshTrigger prop to re-fetch stats
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_
  
  - [ ]* 11.2 Write component tests for StatsPanel
    - Test stats fetching and display
    - Test refresh on prop change
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [x] 12. Implement React App component and integrate all components
  - [x] 12.1 Create App component
    - Compose TicketForm, TicketList, and StatsPanel
    - Manage refreshTrigger state for stats
    - Pass onTicketCreated callback to TicketForm to refresh list and stats
    - Add basic styling for layout
    - _Requirements: 7.9, 9.7_
  
  - [x] 12.2 Configure axios base URL
    - Set axios.defaults.baseURL to backend URL (environment variable)
    - _Requirements: 2.1, 3.1, 4.1, 5.1, 6.1_

- [x] 13. Checkpoint - Ensure frontend builds and runs
  - Run npm start to verify frontend compiles
  - Test all components render correctly
  - Verify API integration with mock backend

- [x] 14. Create Docker configuration for backend
  - [x] 14.1 Create backend Dockerfile
    - Use python:3.11 base image
    - Set working directory to /app
    - Copy requirements.txt and install dependencies
    - Copy all backend code
    - Expose port 8000
    - Create entrypoint script to run migrations and start server
    - _Requirements: 10.2, 10.4_
  
  - [x] 14.2 Create backend entrypoint script
    - Wait for database to be ready
    - Run python manage.py migrate
    - Run python manage.py runserver 0.0.0.0:8000
    - _Requirements: 10.4, 10.5_

- [x] 15. Create Docker configuration for frontend
  - [x] 15.1 Create frontend Dockerfile
    - Use node:18 base image
    - Set working directory to /app
    - Copy package.json and install dependencies
    - Copy all frontend code
    - Expose port 3000
    - Set CMD to npm start
    - _Requirements: 10.3_
  
  - [x] 15.2 Configure environment variables for API URL
    - Use REACT_APP_API_URL environment variable
    - _Requirements: 10.3_

- [x] 16. Create docker-compose.yml
  - [x] 16.1 Define all services
    - Add postgres service with PostgreSQL 15 image
    - Add backend service with build context and depends_on postgres
    - Add frontend service with build context and depends_on backend
    - Configure environment variables for all services
    - Set up volumes for database persistence
    - Map ports: 5432 for postgres, 8000 for backend, 3000 for frontend
    - _Requirements: 10.1, 10.2, 10.3, 10.5, 10.6, 10.7_
  
  - [x] 16.2 Add environment variable configuration
    - Pass DATABASE_URL to backend
    - Pass OPENAI_API_KEY to backend (from .env file)
    - Pass REACT_APP_API_URL to frontend
    - _Requirements: 6.5, 10.6_
  
  - [ ]* 16.3 Write integration tests for Docker setup
    - Test docker-compose up --build starts all services
    - Test database migrations run automatically
    - Test frontend can reach backend
    - Test backend can reach database
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.7_

- [ ] 17. Create README.md with setup instructions
  - [ ] 17.1 Document setup and running instructions
    - Explain docker-compose up --build command
    - Document environment variables needed
    - Explain how to set OPENAI_API_KEY
    - Document which LLM is used (OpenAI GPT-4) and why
    - Include design decisions and architecture overview
    - _Requirements: 10.7_
  
  - [ ] 17.2 Document API endpoints
    - List all endpoints with examples
    - Document request/response formats
    - _Requirements: 2.1, 3.1, 4.1, 5.1, 6.1_

- [ ] 18. Final integration testing and polish
  - [ ] 18.1 Test complete workflow
    - Run docker-compose up --build
    - Create tickets through frontend
    - Verify LLM suggestions work (with API key)
    - Test filtering and search
    - Verify stats update correctly
    - Test status updates
    - _Requirements: 10.7_
  
  - [ ] 18.2 Test without LLM API key
    - Verify application works with fallback values
    - Ensure graceful degradation
    - _Requirements: 6.3, 6.4_
  
  - [ ] 18.3 Code cleanup
    - Remove debug prints and console.logs
    - Ensure consistent code formatting
    - Add comments where needed
    - _Requirements: All_

- [ ] 19. Final checkpoint - Complete system verification
  - Ensure docker-compose up --build works from clean state
  - Verify all requirements are met
  - Test with fresh database
  - Verify commit history is incremental and meaningful

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Focus on getting core functionality working first, then add tests
- LLM integration should degrade gracefully when API key is not provided
