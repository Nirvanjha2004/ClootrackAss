# Requirements Document

## Introduction

A full-stack Support Ticket System that allows users to submit, browse, filter, and view metrics for support tickets. The system integrates with an LLM API to automatically categorize tickets and suggest priority levels based on ticket descriptions. The entire application is containerized with Docker for easy deployment.

## Glossary

- **Ticket**: A support request submitted by a user containing a title, description, category, priority, and status
- **LLM**: Large Language Model - an AI service that analyzes ticket descriptions to suggest categories and priorities
- **Backend**: Django REST Framework API that manages ticket data and LLM integration
- **Frontend**: React application that provides the user interface
- **Classification**: The process of analyzing a ticket description to suggest category and priority
- **Stats_Endpoint**: API endpoint that returns aggregated ticket metrics
- **Docker_Compose**: Tool that orchestrates multiple Docker containers to run the complete application

## Requirements

### Requirement 1: Ticket Data Management

**User Story:** As a user, I want to create and store support tickets with structured data, so that my issues are properly tracked and organized.

#### Acceptance Criteria

1. THE Backend SHALL store tickets with a title field of maximum 200 characters
2. THE Backend SHALL store tickets with a required description field containing the full problem description
3. THE Backend SHALL store tickets with a category field limited to choices: billing, technical, account, general
4. THE Backend SHALL store tickets with a priority field limited to choices: low, medium, high, critical
5. THE Backend SHALL store tickets with a status field limited to choices: open, in_progress, resolved, closed
6. THE Backend SHALL automatically set the status field to open when a ticket is created
7. THE Backend SHALL automatically record the creation timestamp for each ticket
8. THE Backend SHALL enforce all field constraints at the database level

### Requirement 2: Ticket Creation API

**User Story:** As a frontend application, I want to create new tickets via API, so that users can submit their support requests.

#### Acceptance Criteria

1. WHEN a POST request is sent to /api/tickets/ with valid ticket data, THE Backend SHALL create a new ticket and return HTTP status 201
2. WHEN a POST request is sent to /api/tickets/ with invalid data, THE Backend SHALL return an appropriate error response
3. WHEN a ticket is created, THE Backend SHALL persist it to the PostgreSQL database immediately

### Requirement 3: Ticket Listing and Filtering API

**User Story:** As a frontend application, I want to retrieve and filter tickets, so that users can browse and search their support requests.

#### Acceptance Criteria

1. WHEN a GET request is sent to /api/tickets/, THE Backend SHALL return all tickets ordered by newest first
2. WHEN a GET request includes ?category= parameter, THE Backend SHALL filter tickets by the specified category
3. WHEN a GET request includes ?priority= parameter, THE Backend SHALL filter tickets by the specified priority
4. WHEN a GET request includes ?status= parameter, THE Backend SHALL filter tickets by the specified status
5. WHEN a GET request includes ?search= parameter, THE Backend SHALL filter tickets where the search term appears in title or description
6. WHEN multiple filter parameters are provided, THE Backend SHALL apply all filters in combination

### Requirement 4: Ticket Update API

**User Story:** As a frontend application, I want to update ticket properties, so that users can modify status, category, or priority.

#### Acceptance Criteria

1. WHEN a PATCH request is sent to /api/tickets/<id>/ with valid data, THE Backend SHALL update the specified ticket fields
2. WHEN a PATCH request is sent to /api/tickets/<id>/ with invalid data, THE Backend SHALL return an appropriate error response
3. WHEN a ticket is updated, THE Backend SHALL persist changes to the database immediately

### Requirement 5: Ticket Statistics API

**User Story:** As a frontend application, I want to retrieve aggregated ticket statistics, so that users can view metrics about their support tickets.

#### Acceptance Criteria

1. WHEN a GET request is sent to /api/tickets/stats/, THE Backend SHALL return the total count of all tickets
2. WHEN a GET request is sent to /api/tickets/stats/, THE Backend SHALL return the count of tickets with status open
3. WHEN a GET request is sent to /api/tickets/stats/, THE Backend SHALL return the average number of tickets created per day
4. WHEN a GET request is sent to /api/tickets/stats/, THE Backend SHALL return a breakdown of ticket counts by priority
5. WHEN a GET request is sent to /api/tickets/stats/, THE Backend SHALL return a breakdown of ticket counts by category
6. THE Backend SHALL compute all statistics using database-level aggregation operations
7. THE Backend SHALL NOT use Python-level loops to compute statistics

### Requirement 6: LLM Classification API

**User Story:** As a frontend application, I want to get AI-suggested categories and priorities for ticket descriptions, so that users receive intelligent recommendations.

#### Acceptance Criteria

1. WHEN a POST request is sent to /api/tickets/classify/ with a description field, THE Backend SHALL call an LLM API with the description
2. WHEN the LLM API responds successfully, THE Backend SHALL return suggested_category and suggested_priority fields
3. WHEN the LLM API is unreachable, THE Backend SHALL handle the error gracefully and return an appropriate response
4. WHEN the LLM API returns invalid data, THE Backend SHALL handle the error gracefully and return an appropriate response
5. THE Backend SHALL accept the LLM API key as an environment variable
6. THE Backend SHALL NOT hardcode the LLM API key in source code

### Requirement 7: Ticket Submission Form

**User Story:** As a user, I want to submit support tickets through a web form, so that I can report my issues.

#### Acceptance Criteria

1. WHEN the ticket form is displayed, THE Frontend SHALL show a title input field with 200 character maximum
2. WHEN the ticket form is displayed, THE Frontend SHALL show a required description textarea
3. WHEN the ticket form is displayed, THE Frontend SHALL show category and priority dropdown fields
4. WHEN a user enters a description, THE Frontend SHALL call the classify endpoint to get LLM suggestions
5. WHEN LLM suggestions are received, THE Frontend SHALL pre-fill the category and priority dropdowns
6. WHEN LLM classification is in progress, THE Frontend SHALL display a loading state
7. WHEN a user submits the form, THE Frontend SHALL send a POST request to /api/tickets/
8. WHEN a ticket is successfully created, THE Frontend SHALL clear the form without a full page reload
9. WHEN a ticket is successfully created, THE Frontend SHALL display the new ticket in the list immediately
10. THE Frontend SHALL allow users to override LLM-suggested category and priority values

### Requirement 8: Ticket List Display

**User Story:** As a user, I want to view and filter my support tickets, so that I can track and manage my requests.

#### Acceptance Criteria

1. WHEN the ticket list is displayed, THE Frontend SHALL show all tickets ordered by newest first
2. WHEN displaying a ticket, THE Frontend SHALL show title, truncated description, category, priority, status, and timestamp
3. WHEN a user selects category filter, THE Frontend SHALL display only tickets matching that category
4. WHEN a user selects priority filter, THE Frontend SHALL display only tickets matching that priority
5. WHEN a user selects status filter, THE Frontend SHALL display only tickets matching that status
6. WHEN a user enters a search term, THE Frontend SHALL display only tickets where the term appears in title or description
7. WHEN a user clicks a ticket, THE Frontend SHALL allow changing the ticket status
8. WHEN a ticket status is changed, THE Frontend SHALL send a PATCH request to update the ticket

### Requirement 9: Statistics Dashboard

**User Story:** As a user, I want to view aggregated ticket metrics, so that I can understand ticket trends and distribution.

#### Acceptance Criteria

1. WHEN the stats dashboard is displayed, THE Frontend SHALL fetch data from /api/tickets/stats/
2. WHEN stats data is received, THE Frontend SHALL display total ticket count
3. WHEN stats data is received, THE Frontend SHALL display open ticket count
4. WHEN stats data is received, THE Frontend SHALL display average tickets per day
5. WHEN stats data is received, THE Frontend SHALL display priority breakdown
6. WHEN stats data is received, THE Frontend SHALL display category breakdown
7. WHEN a new ticket is submitted, THE Frontend SHALL refresh the stats display automatically

### Requirement 10: Docker Containerization

**User Story:** As a developer, I want to run the entire application with a single command, so that deployment is simple and consistent.

#### Acceptance Criteria

1. WHEN docker-compose up --build is executed, THE Docker_Compose SHALL start a PostgreSQL database service
2. WHEN docker-compose up --build is executed, THE Docker_Compose SHALL start the Django backend service
3. WHEN docker-compose up --build is executed, THE Docker_Compose SHALL start the React frontend service
4. WHEN the backend service starts, THE Backend SHALL run database migrations automatically
5. WHEN services start, THE Docker_Compose SHALL ensure proper dependency order
6. THE Docker_Compose SHALL pass the LLM API key as an environment variable to the backend service
7. WHEN all services are running, THE application SHALL be fully functional without manual setup steps
