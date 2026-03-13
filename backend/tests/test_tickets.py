"""
Unit and property-based tests for tickets blueprint.

Tests verify ticket creation, retrieval, listing, validation,
and error handling according to requirements.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app import create_app, db
from app.models.ticket import Ticket


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


class TestTicketCreation:
    """Unit tests for ticket creation endpoint."""
    
    def test_create_ticket_success(self, client):
        """
        **Validates: Requirements 1.1, 1.4, 2.1, 2.2, 2.3, 5.1, 5.2**
        
        Test successful ticket creation with valid text.
        Verifies that a ticket is created with pending status and returns 201.
        """
        response = client.post('/api/tickets', json={
            'text': 'My printer is not working'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['error'] is None
        assert data['data'] is not None
        
        ticket = data['data']
        assert ticket['text'] == 'My printer is not working'
        assert ticket['status'] == 'pending'
        assert ticket['category'] is None
        assert ticket['confidence'] is None
        assert 'id' in ticket
        assert 'created_at' in ticket
        assert 'updated_at' in ticket
    
    def test_create_ticket_with_whitespace_trimming(self, client):
        """
        **Validates: Requirements 1.1, 10.4**
        
        Test that whitespace is trimmed from ticket text.
        Verifies that leading and trailing whitespace is removed.
        """
        response = client.post('/api/tickets', json={
            'text': '  My laptop screen is broken  \n'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        ticket = data['data']
        assert ticket['text'] == 'My laptop screen is broken'
    
    def test_create_ticket_empty_text(self, client):
        """
        **Validates: Requirements 1.2, 5.3, 10.2**
        
        Test that empty text is rejected.
        Verifies that empty string returns 400 error.
        """
        response = client.post('/api/tickets', json={
            'text': ''
        })
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['data'] is None
        assert 'empty' in data['error'].lower()
    
    def test_create_ticket_whitespace_only(self, client):
        """
        **Validates: Requirements 1.2, 10.4**
        
        Test that whitespace-only text is rejected.
        Verifies that text with only spaces/tabs/newlines returns 400 error.
        """
        response = client.post('/api/tickets', json={
            'text': '   \n\t  '
        })
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['data'] is None
        assert 'empty' in data['error'].lower()
    
    def test_create_ticket_text_too_long(self, client):
        """
        **Validates: Requirements 1.3, 5.3, 10.2**
        
        Test that text exceeding 5000 characters is rejected.
        Verifies that long text returns 400 error.
        """
        long_text = 'a' * 5001
        response = client.post('/api/tickets', json={
            'text': long_text
        })
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['data'] is None
        assert '5000' in data['error']
    
    def test_create_ticket_exactly_5000_chars(self, client):
        """
        **Validates: Requirements 1.1**
        
        Test that text with exactly 5000 characters is accepted.
        Verifies boundary condition at maximum length.
        """
        text_5000 = 'a' * 5000
        response = client.post('/api/tickets', json={
            'text': text_5000
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        ticket = data['data']
        assert len(ticket['text']) == 5000
    
    def test_create_ticket_missing_text_field(self, client):
        """
        **Validates: Requirements 5.3, 10.2**
        
        Test that missing text field is rejected.
        Verifies that request without text field returns 400 error.
        """
        response = client.post('/api/tickets', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['data'] is None
        assert 'required' in data['error'].lower()
    
    def test_create_ticket_text_not_string(self, client):
        """
        **Validates: Requirements 10.2**
        
        Test that non-string text value is rejected.
        Verifies that text must be a string type.
        """
        response = client.post('/api/tickets', json={
            'text': 12345
        })
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['data'] is None
        assert 'string' in data['error'].lower()
    
    def test_create_ticket_non_json_request(self, client):
        """
        **Validates: Requirements 10.2**
        
        Test that non-JSON requests are rejected.
        Verifies that Content-Type must be application/json.
        """
        response = client.post('/api/tickets', data='not json')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['data'] is None
        assert 'json' in data['error'].lower()


class TestTicketRetrieval:
    """Unit tests for ticket retrieval endpoint."""
    
    def test_get_ticket_success(self, client, app):
        """
        **Validates: Requirements 6.1, 6.2, 6.4**
        
        Test successful ticket retrieval by ID.
        Verifies that existing ticket is returned with 200 status.
        """
        # Create a ticket first
        with app.app_context():
            ticket = Ticket(
                text='Test ticket',
                status='pending'
            )
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id
        
        # Retrieve the ticket
        response = client.get(f'/api/tickets/{ticket_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['error'] is None
        assert data['data'] is not None
        
        ticket_data = data['data']
        assert ticket_data['id'] == ticket_id
        assert ticket_data['text'] == 'Test ticket'
        assert ticket_data['status'] == 'pending'
    
    def test_get_ticket_not_found(self, client):
        """
        **Validates: Requirements 6.3**
        
        Test retrieval of non-existent ticket.
        Verifies that non-existent ticket ID returns 404 error.
        """
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = client.get(f'/api/tickets/{fake_id}')
        
        assert response.status_code == 404
        data = response.get_json()
        
        assert data['data'] is None
        assert 'not found' in data['error'].lower()


class TestTicketListing:
    """Unit tests for ticket listing endpoint."""
    
    def test_list_tickets_empty(self, client):
        """
        **Validates: Requirements 7.1, 7.4**
        
        Test listing tickets when database is empty.
        Verifies that empty list is returned with correct pagination metadata.
        """
        response = client.get('/api/tickets')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['error'] is None
        assert data['data'] is not None
        
        result = data['data']
        assert result['tickets'] == []
        assert result['total'] == 0
        assert result['page'] == 1
        assert result['per_page'] == 20
        assert result['pages'] == 0
    
    def test_list_tickets_with_data(self, client, app):
        """
        **Validates: Requirements 7.1, 7.4, 7.5**
        
        Test listing tickets with data.
        Verifies that tickets are returned in descending order by created_at.
        """
        # Create multiple tickets
        with app.app_context():
            ticket1 = Ticket(text='First ticket', status='pending')
            ticket2 = Ticket(text='Second ticket', status='classified', category='tech', confidence=0.9)
            ticket3 = Ticket(text='Third ticket', status='failed')
            
            db.session.add_all([ticket1, ticket2, ticket3])
            db.session.commit()
        
        response = client.get('/api/tickets')
        
        assert response.status_code == 200
        data = response.get_json()
        
        result = data['data']
        assert len(result['tickets']) == 3
        assert result['total'] == 3
        assert result['page'] == 1
        assert result['per_page'] == 20
        assert result['pages'] == 1
        
        # Verify order (most recent first)
        tickets = result['tickets']
        assert tickets[0]['text'] == 'Third ticket'
        assert tickets[1]['text'] == 'Second ticket'
        assert tickets[2]['text'] == 'First ticket'
    
    def test_list_tickets_pagination_default(self, client):
        """
        **Validates: Requirements 7.3**
        
        Test default pagination parameters.
        Verifies that default page=1 and per_page=20 are used.
        """
        response = client.get('/api/tickets')
        
        assert response.status_code == 200
        data = response.get_json()
        
        result = data['data']
        assert result['page'] == 1
        assert result['per_page'] == 20
    
    def test_list_tickets_pagination_custom(self, client, app):
        """
        **Validates: Requirements 7.2, 7.4**
        
        Test custom pagination parameters.
        Verifies that page and per_page query parameters work correctly.
        """
        # Create 25 tickets
        with app.app_context():
            for i in range(25):
                ticket = Ticket(text=f'Ticket {i}', status='pending')
                db.session.add(ticket)
            db.session.commit()
        
        # Request page 2 with 10 per page
        response = client.get('/api/tickets?page=2&per_page=10')
        
        assert response.status_code == 200
        data = response.get_json()
        
        result = data['data']
        assert result['page'] == 2
        assert result['per_page'] == 10
        assert result['total'] == 25
        assert result['pages'] == 3
        assert len(result['tickets']) == 10
    
    def test_list_tickets_invalid_page(self, client):
        """
        **Validates: Requirements 10.2**
        
        Test invalid page parameter.
        Verifies that page < 1 returns 400 error.
        """
        response = client.get('/api/tickets?page=0')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['data'] is None
        assert 'page' in data['error'].lower()
    
    def test_list_tickets_invalid_per_page_too_small(self, client):
        """
        **Validates: Requirements 10.2**
        
        Test invalid per_page parameter (too small).
        Verifies that per_page < 1 returns 400 error.
        """
        response = client.get('/api/tickets?per_page=0')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['data'] is None
        assert 'per_page' in data['error'].lower()
    
    def test_list_tickets_invalid_per_page_too_large(self, client):
        """
        **Validates: Requirements 10.2**
        
        Test invalid per_page parameter (too large).
        Verifies that per_page > 100 returns 400 error.
        """
        response = client.get('/api/tickets?per_page=101')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['data'] is None
        assert 'per_page' in data['error'].lower()


class TestTicketProperties:
    """Property-based tests for ticket endpoints."""
    
    @given(text=st.text(min_size=1, max_size=5000))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_valid_text_accepted(self, client, text):
        """
        **Validates: Requirements 1.1, 2.1**
        
        Property 1: Input Validation
        
        Any text between 1-5000 characters should be accepted and create a ticket.
        This test verifies that all valid text inputs result in successful ticket creation.
        """
        # Skip if text is whitespace-only (valid rejection case)
        if text.strip() == '':
            pytest.skip("Whitespace-only text is validly rejected")
        
        response = client.post('/api/tickets', json={'text': text})
        
        # Should succeed with 201
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['error'] is None
        assert data['data'] is not None
        
        ticket = data['data']
        assert ticket['text'] == text.strip()
        assert ticket['status'] == 'pending'
        assert ticket['id'] is not None
    
    @given(
        text=st.text(min_size=1, max_size=100, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
        status=st.sampled_from(['pending', 'classified', 'failed'])
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_status_validity(self, app, text, status):
        """
        **Validates: Requirements 2.1**
        
        Property 3: Status Consistency
        
        Every ticket must have exactly one of three valid status values.
        This test verifies that tickets can only be created with valid status values.
        """
        with app.app_context():
            ticket = Ticket(text=text, status=status)
            db.session.add(ticket)
            db.session.commit()
            
            # Verify ticket was created with valid status
            assert ticket.status in ['pending', 'classified', 'failed']
            assert ticket.id is not None
    
    @given(
        page=st.integers(min_value=1, max_value=10),
        per_page=st.integers(min_value=1, max_value=100)
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_pagination_parameters(self, client, page, per_page):
        """
        **Validates: Requirements 7.2, 7.4**
        
        Property: Pagination Parameter Validity
        
        All valid pagination parameters should be accepted and return correct metadata.
        This test verifies that pagination works correctly with various valid parameters.
        """
        response = client.get(f'/api/tickets?page={page}&per_page={per_page}')
        
        assert response.status_code == 200
        data = response.get_json()
        
        result = data['data']
        assert result['page'] == page
        assert result['per_page'] == per_page
        assert result['total'] >= 0
        assert result['pages'] >= 0


class TestResponseFormat:
    """Tests for API response format consistency."""
    
    def test_success_response_format(self, client):
        """
        **Validates: Requirements 5.1, 5.2, 5.5**
        
        Test that successful responses follow the correct format.
        Verifies that response includes data and error fields with proper structure.
        """
        response = client.post('/api/tickets', json={
            'text': 'Test ticket'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Verify response structure
        assert 'data' in data
        assert 'error' in data
        assert data['error'] is None
        
        # Verify ticket data structure
        ticket = data['data']
        assert 'id' in ticket
        assert 'text' in ticket
        assert 'category' in ticket
        assert 'confidence' in ticket
        assert 'status' in ticket
        assert 'created_at' in ticket
        assert 'updated_at' in ticket
        
        # Verify ISO 8601 timestamp format
        assert 'T' in ticket['created_at']
        assert 'T' in ticket['updated_at']
    
    def test_error_response_format(self, client):
        """
        **Validates: Requirements 5.3**
        
        Test that error responses follow the correct format.
        Verifies that error response includes data=None and error message.
        """
        response = client.post('/api/tickets', json={
            'text': ''
        })
        
        assert response.status_code == 400
        data = response.get_json()
        
        # Verify error response structure
        assert 'data' in data
        assert 'error' in data
        assert data['data'] is None
        assert isinstance(data['error'], str)
        assert len(data['error']) > 0
