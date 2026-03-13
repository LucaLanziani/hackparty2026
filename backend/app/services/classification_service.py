"""
Classification service for ticket text categorization.

This module provides integration with an external classification API
to categorize support ticket text and return confidence scores.
"""

import requests
import time
from typing import Dict, Any


class ClassificationAPIError(Exception):
    """Raised when the classification API call fails."""
    pass


class ClassificationResult:
    """Result from text classification."""
    
    def __init__(self, category: str, confidence: float):
        self.category = category
        self.confidence = confidence


class ClassificationService:
    """
    Service for classifying ticket text using an external API.
    
    Implements retry logic with exponential backoff and validates
    API responses to ensure data integrity.
    """
    
    def __init__(self, api_url: str, api_key: str):
        """
        Initialize the classification service.
        
        Args:
            api_url: Base URL of the classification API endpoint
            api_key: API key for authentication
        """
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = 10  # seconds
        self.max_retries = 3
    
    def classify_text(self, text: str) -> ClassificationResult:
        """
        Classify text using the external API with retry logic.
        
        Args:
            text: The text to classify
            
        Returns:
            ClassificationResult with category and confidence
            
        Raises:
            ClassificationAPIError: If API call fails after all retries
            ValueError: If API response format is invalid
        """
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        payload = {'text': text}
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response format
                    if 'category' not in data or 'confidence' not in data:
                        raise ValueError(
                            f"Invalid API response format: missing required fields. "
                            f"Got: {list(data.keys())}"
                        )
                    
                    # Validate confidence range
                    confidence = float(data['confidence'])
                    if not (0.0 <= confidence <= 1.0):
                        raise ValueError(
                            f"Confidence must be between 0 and 1, got: {confidence}"
                        )
                    
                    return ClassificationResult(
                        category=data['category'],
                        confidence=confidence
                    )
                else:
                    last_error = ClassificationAPIError(
                        f"API returned status {response.status_code}: {response.text}"
                    )
                    
            except (requests.exceptions.RequestException, 
                    requests.exceptions.Timeout) as e:
                last_error = ClassificationAPIError(
                    f"Network error on attempt {attempt + 1}: {str(e)}"
                )
            
            # Exponential backoff before retry (except on last attempt)
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                time.sleep(wait_time)
        
        # All retries exhausted
        raise ClassificationAPIError(
            f"Failed after {self.max_retries} retries. Last error: {last_error}"
        )
