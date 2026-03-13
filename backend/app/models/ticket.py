"""Ticket model for storing support tickets and their classifications."""
import uuid
from datetime import datetime
from app import db


class Ticket(db.Model):
    """Ticket model representing a support ticket with classification data."""
    
    __tablename__ = 'tickets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Serialize ticket to dictionary with ISO 8601 formatted timestamps.
        
        Returns:
            dict: Dictionary containing all ticket fields with timestamps in ISO 8601 format.
        """
        return {
            'id': self.id,
            'text': self.text,
            'category': self.category,
            'confidence': self.confidence,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
