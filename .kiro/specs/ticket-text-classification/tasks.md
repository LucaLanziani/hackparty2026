# Implementation Plan: Ticket Text Classification

## Overview

This implementation plan breaks down the ticket text classification feature into discrete coding tasks. The feature consists of a React frontend form component, a Flask backend API with database persistence, and integration with an external classification service. Tasks are organized to build incrementally, with testing sub-tasks marked as optional for faster MVP delivery.

## Tasks

- [x] 1. Set up backend database model and migrations
  - Create SQLAlchemy Ticket model in `backend/app/models/ticket.py`
  - Add fields: id (UUID primary key), text (Text, max 5000), category (String 100), confidence (Float 0-1), status (String 20), created_at, updated_at
  - Add to_dict() serialization method
  - Generate and apply database migration with `flask db migrate` and `flask db upgrade`
  - _Requirements: 2.1, 2.2, 2.3, 12.1, 12.2, 12.3, 12.4, 15.1, 15.2, 15.3, 15.4_

- [x] 2. Implement classification service module
  - [x] 2.1 Create ClassificationService class in `backend/app/services/classification_service.py`
    - Implement __init__ with api_url and api_key parameters
    - Implement classify_text(text: str) method with HTTP POST to external API
    - Add retry logic with exponential backoff (max 3 retries)
    - Handle timeouts (10 second timeout per request)
    - Validate API response format (category and confidence fields)
    - Raise ClassificationAPIError on failures
    - _Requirements: 3.1, 3.2, 3.4, 4.1, 4.4, 14.1, 14.2_
  
  - [x] 2.2 Write property test for classification service
    - **Property 2: Classification Confidence Range** - All successful classifications return confidence between 0 and 1
    - **Validates: Requirements 3.4**
  
  - [x] 2.3 Write unit tests for classification service
    - Test successful classification with mocked API
    - Test retry logic with network failures
    - Test timeout handling
    - Test malformed API response handling
    - _Requirements: 3.1, 3.5, 4.1, 4.4_

- [-] 3. Create tickets blueprint and API endpoints
  - [-] 3.1 Create tickets blueprint in `backend/app/routes/tickets.py`
    - Register blueprint with '/api' prefix
    - Implement POST /api/tickets endpoint for ticket creation
    - Implement GET /api/tickets/<ticket_id> endpoint for retrieval
    - Implement GET /api/tickets endpoint for listing with pagination
    - Add input validation for text field (1-5000 chars after trim)
    - Add error handling and logging
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.4, 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 7.1, 7.2, 7.3, 7.4, 7.5, 10.2, 10.3, 13.1, 13.2, 13.3_
  
  - [~] 3.2 Integrate classification service into ticket creation flow
    - Initialize ClassificationService with environment variables
    - Call classify_text after ticket creation
    - Update ticket with classification results on success
    - Set status to 'failed' on classification errors
    - Ensure ticket is saved even if classification fails
    - _Requirements: 3.1, 3.2, 3.3, 4.2, 4.3, 4.5, 14.3, 14.4_
  
  - [ ]* 3.3 Write property tests for ticket API
    - **Property 1: Input Validation** - All accepted tickets have text length between 1-5000 characters
    - **Validates: Requirements 1.1**
    - **Property 3: Status Consistency** - All tickets have status in ['pending', 'classified', 'failed']
    - **Validates: Requirements 12.3**
    - **Property 4: Classification Completeness** - Classified tickets always have category and confidence
    - **Validates: Requirements 3.3**
  
  - [ ]* 3.4 Write unit tests for tickets blueprint
    - Test POST /api/tickets with valid input
    - Test POST /api/tickets with empty text (400 error)
    - Test POST /api/tickets with text > 5000 chars (400 error)
    - Test GET /api/tickets/<id> with existing ticket
    - Test GET /api/tickets/<id> with non-existent ticket (404 error)
    - Test GET /api/tickets with pagination
    - Test classification failure handling
    - _Requirements: 1.2, 1.3, 2.5, 4.2, 4.3, 5.2, 5.3, 5.4, 6.2, 6.3, 7.1, 7.4_

- [~] 4. Configure Flask app with CORS, rate limiting, and environment variables
  - Update `backend/app/__init__.py` to register tickets blueprint
  - Configure Flask-CORS for frontend origin (http://localhost:5173)
  - Add Flask-Limiter for rate limiting (10 requests per minute)
  - Load classification API URL and key from environment variables
  - Add structured logging configuration
  - Create `.env.example` with required environment variables
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 13.4, 13.5, 14.2, 14.3_

- [~] 5. Checkpoint - Backend API complete
  - Run `flask db upgrade` to ensure migrations are applied
  - Start Flask dev server and verify endpoints respond
  - Test POST /api/tickets manually with curl or Postman
  - Ensure all tests pass (if implemented)
  - Ask the user if questions arise

- [~] 6. Create frontend TypeScript types and API client
  - [ ] 6.1 Define TypeScript interfaces in `frontend/src/types/ticket.ts`
    - Define ClassifiedTicket interface with all fields
    - Define CreateTicketRequest and CreateTicketResponse interfaces
    - Define API error response types
    - _Requirements: 5.1, 5.2, 5.5, 15.3_
  
  - [ ] 6.2 Create API client in `frontend/src/lib/api/tickets.ts`
    - Implement createTicket(text: string) function
    - Implement getTicket(id: string) function
    - Implement listTickets(page, perPage) function
    - Use fetch with proper headers and error handling
    - Parse and validate API responses
    - _Requirements: 1.4, 5.1, 5.2, 5.3, 5.4, 6.1, 7.1_
  
  - [ ]* 6.3 Write unit tests for API client
    - Test createTicket with mocked fetch
    - Test error handling for network failures
    - Test response parsing
    - _Requirements: 1.4, 5.3, 5.4_

- [ ] 7. Implement TicketClassificationForm component
  - [ ] 7.1 Create form component in `frontend/src/components/TicketClassificationForm.tsx`
    - Create form with textarea for ticket text input
    - Add character counter showing remaining characters (5000 max)
    - Implement client-side validation (1-5000 chars after trim)
    - Add submit button with loading state
    - Display validation errors below input field
    - Use ShadCN UI components (Textarea, Button, Label, Alert)
    - Style with Tailwind CSS
    - _Requirements: 1.1, 1.2, 1.3, 8.1, 8.2, 8.4, 10.1, 10.4_
  
  - [ ] 7.2 Add form submission logic and loading states
    - Handle form submit event
    - Call createTicket API function
    - Show loading indicator within 100ms of submission
    - Disable submit button during submission
    - Clear form on successful submission
    - _Requirements: 1.4, 8.1, 8.2, 8.3_
  
  - [ ] 7.3 Add classification result display
    - Display ticket ID, category, and confidence on success
    - Format confidence as percentage with one decimal place
    - Show appropriate message for 'failed' status tickets
    - Display error messages for API failures
    - Add props for onSubmitSuccess and onSubmitError callbacks
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [ ]* 7.4 Write component tests for TicketClassificationForm
    - Test form renders with all elements
    - Test validation prevents empty submission
    - Test validation prevents > 5000 char submission
    - Test loading state appears on submit
    - Test success result display
    - Test error message display
    - Use React Testing Library and Vitest
    - _Requirements: 1.2, 1.3, 8.1, 8.2, 9.1, 9.2_

- [ ] 8. Create tickets page and integrate form component
  - Create page component in `frontend/src/pages/TicketsPage.tsx`
  - Import and render TicketClassificationForm
  - Add page title and layout
  - Handle success callback to show toast notification
  - Handle error callback to show error toast
  - Add route in React Router configuration
  - _Requirements: 1.1, 9.1, 9.2_

- [ ] 9. Checkpoint - Frontend form complete
  - Run `pnpm typecheck` to verify TypeScript compilation
  - Start frontend dev server and test form manually
  - Submit valid ticket and verify classification result displays
  - Test validation errors for empty and long text
  - Ensure all tests pass (if implemented)
  - Ask the user if questions arise

- [ ] 10. Create ticket list view component (optional enhancement)
  - Create TicketList component in `frontend/src/components/TicketList.tsx`
  - Display paginated list of tickets with category and confidence
  - Add pagination controls
  - Show ticket status with visual indicators
  - Link to individual ticket detail view
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 11. Write integration tests for end-to-end flow
  - Set up Playwright test suite
  - Test complete user flow: enter text → submit → view result
  - Test error scenarios with network failures
  - Test with various text lengths
  - Test concurrent submissions
  - _Requirements: 1.1, 1.4, 8.1, 9.1_

- [ ] 12. Final checkpoint - Feature complete
  - Verify both frontend and backend are running
  - Test complete flow from UI to database
  - Check database contains ticket records with classifications
  - Review error handling for all failure scenarios
  - Ensure all required tests pass
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The classification API URL and key must be configured in environment variables before testing
- Database migrations must be applied before running the backend
- Frontend and backend should be developed and tested independently, then integrated
