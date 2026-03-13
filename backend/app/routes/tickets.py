"""Tickets blueprint for ticket creation and retrieval."""
import logging
from flask import Blueprint, jsonify, request
from app import db
from app.models.ticket import Ticket

# Configure logging
logger = logging.getLogger(__name__)

bp = Blueprint('tickets', __name__)


@bp.route('/tickets', methods=['POST'])
def create_ticket():
    """
    Create a new ticket.
    
    Request Body:
        {
            "text": str  # Required, 1-5000 characters after trim
        }
    
    Returns:
        tuple: (response_dict, status_code)
        - 201: Ticket created successfully
        - 400: Validation error
        - 500: Server error
    """
    try:
        # Validate request has JSON body
        if not request.is_json:
            return jsonify({'data': None, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # Validate text field exists
        if 'text' not in data:
            return jsonify({'data': None, 'error': 'text field is required'}), 400
        
        text = data['text']
        
        # Validate text is a string
        if not isinstance(text, str):
            return jsonify({'data': None, 'error': 'text must be a string'}), 400
        
        # Trim whitespace and validate length
        text = text.strip()
        
        if len(text) == 0:
            return jsonify({'data': None, 'error': 'text cannot be empty'}), 400
        
        if len(text) > 5000:
            return jsonify({'data': None, 'error': 'text must be 5000 characters or less'}), 400
        
        # Create ticket with pending status
        ticket = Ticket(
            text=text,
            status='pending',
            category=None,
            confidence=None
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        logger.info(f'Created ticket {ticket.id} with status pending')
        
        return jsonify({'data': ticket.to_dict(), 'error': None}), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error creating ticket: {str(e)}', exc_info=True)
        return jsonify({'data': None, 'error': 'Failed to create ticket'}), 500


@bp.route('/tickets/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """
    Get a ticket by ID.
    
    Args:
        ticket_id: UUID string of the ticket
    
    Returns:
        tuple: (response_dict, status_code)
        - 200: Ticket found
        - 404: Ticket not found
        - 500: Server error
    """
    try:
        ticket = db.session.get(Ticket, ticket_id)
        
        if ticket is None:
            return jsonify({'data': None, 'error': f'Ticket {ticket_id} not found'}), 404
        
        return jsonify({'data': ticket.to_dict(), 'error': None}), 200
        
    except Exception as e:
        logger.error(f'Error retrieving ticket {ticket_id}: {str(e)}', exc_info=True)
        return jsonify({'data': None, 'error': 'Failed to retrieve ticket'}), 500


@bp.route('/tickets', methods=['GET'])
def list_tickets():
    """
    List all tickets with pagination.
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
    
    Returns:
        tuple: (response_dict, status_code)
        - 200: Success with paginated results
        - 400: Invalid pagination parameters
        - 500: Server error
    """
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Validate pagination parameters
        if page < 1:
            return jsonify({'data': None, 'error': 'page must be >= 1'}), 400
        
        if per_page < 1 or per_page > 100:
            return jsonify({'data': None, 'error': 'per_page must be between 1 and 100'}), 400
        
        # Query tickets ordered by created_at descending
        pagination = Ticket.query.order_by(Ticket.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Build response
        response_data = {
            'tickets': [ticket.to_dict() for ticket in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
        
        return jsonify({'data': response_data, 'error': None}), 200
        
    except Exception as e:
        logger.error(f'Error listing tickets: {str(e)}', exc_info=True)
        return jsonify({'data': None, 'error': 'Failed to list tickets'}), 500
