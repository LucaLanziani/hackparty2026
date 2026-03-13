"""
Property-based and unit tests for ClassificationService.

Tests verify that the classification service correctly validates
confidence values and handles various API responses.
"""

import pytest
import requests
from unittest.mock import Mock, patch, call
from hypothesis import given, strategies as st
from app.services.classification_service import (
    ClassificationService,
    ClassificationResult,
    ClassificationAPIError
)


class TestClassificationServiceProperties:
    """Property-based tests for ClassificationService."""
    
    @given(
        confidence=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        category=st.text(min_size=1, max_size=100)
    )
    def test_property_classification_confidence_range(self, confidence, category):
        """
        **Validates: Requirements 3.4**
        
        Property 2: Classification Confidence Range
        
        All successful classifications return confidence between 0 and 1.
        This test verifies that when the external API returns a valid response
        with any confidence value in the range [0, 1], the classification service
        correctly accepts and returns that confidence value.
        """
        # Create service instance
        service = ClassificationService(
            api_url="https://api.example.com/classify",
            api_key="test-api-key"
        )
        
        # Mock the requests.post to return a successful response
        with patch('app.services.classification_service.requests.post') as mock_post:
            # Create a mock response with the generated confidence value
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'category': category,
                'confidence': confidence
            }
            mock_post.return_value = mock_response
            
            # Call classify_text
            result = service.classify_text("test text")
            
            # Verify the result has confidence in valid range
            assert isinstance(result, ClassificationResult)
            assert 0.0 <= result.confidence <= 1.0
            assert result.confidence == confidence
            assert result.category == category
    
    @given(
        confidence=st.one_of(
            st.floats(min_value=-1000.0, max_value=-0.001),
            st.floats(min_value=1.001, max_value=1000.0)
        )
    )
    def test_property_invalid_confidence_rejected(self, confidence):
        """
        **Validates: Requirements 3.4**
        
        Property: Invalid Confidence Rejection
        
        The classification service must reject confidence values outside [0, 1].
        This test verifies that when the external API returns an invalid confidence
        value (< 0 or > 1), the service raises a ValueError.
        """
        # Create service instance
        service = ClassificationService(
            api_url="https://api.example.com/classify",
            api_key="test-api-key"
        )
        
        # Mock the requests.post to return an invalid confidence
        with patch('app.services.classification_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'category': 'test_category',
                'confidence': confidence
            }
            mock_post.return_value = mock_response
            
            # Verify that invalid confidence raises ValueError
            with pytest.raises(ValueError) as exc_info:
                service.classify_text("test text")
            
            assert "Confidence must be between 0 and 1" in str(exc_info.value)
            assert str(confidence) in str(exc_info.value)


class TestClassificationServiceUnit:
    """Unit tests for ClassificationService."""
    
    def test_successful_classification_with_mocked_api(self):
        """
        **Validates: Requirements 3.1**
        
        Test successful classification with mocked API.
        Verifies that the service correctly processes a successful API response
        and returns a ClassificationResult with the expected category and confidence.
        """
        service = ClassificationService(
            api_url="https://api.example.com/classify",
            api_key="test-api-key"
        )
        
        with patch('app.services.classification_service.requests.post') as mock_post:
            # Mock successful API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'category': 'technical_support',
                'confidence': 0.92
            }
            mock_post.return_value = mock_response
            
            # Call classify_text
            result = service.classify_text("My computer won't start")
            
            # Verify the request was made correctly
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args.kwargs['json'] == {'text': "My computer won't start"}
            assert call_args.kwargs['headers']['Authorization'] == 'Bearer test-api-key'
            assert call_args.kwargs['headers']['Content-Type'] == 'application/json'
            assert call_args.kwargs['timeout'] == 10
            
            # Verify the result
            assert isinstance(result, ClassificationResult)
            assert result.category == 'technical_support'
            assert result.confidence == 0.92
    
    def test_retry_logic_with_network_failures(self):
        """
        **Validates: Requirements 4.1, 4.4**
        
        Test retry logic with network failures.
        Verifies that the service retries up to 3 times with exponential backoff
        when network errors occur, and raises ClassificationAPIError after exhausting retries.
        """
        service = ClassificationService(
            api_url="https://api.example.com/classify",
            api_key="test-api-key"
        )
        
        with patch('app.services.classification_service.requests.post') as mock_post, \
             patch('app.services.classification_service.time.sleep') as mock_sleep:
            # Mock network failure on all attempts
            mock_post.side_effect = requests.exceptions.ConnectionError("Network unreachable")
            
            # Verify that ClassificationAPIError is raised
            with pytest.raises(ClassificationAPIError) as exc_info:
                service.classify_text("Test text")
            
            # Verify retry attempts
            assert mock_post.call_count == 3
            assert "Failed after 3 retries" in str(exc_info.value)
            
            # Verify exponential backoff (1s, 2s for first two retries)
            assert mock_sleep.call_count == 2
            sleep_calls = [call_args[0][0] for call_args in mock_sleep.call_args_list]
            assert sleep_calls == [1, 2]
    
    def test_retry_success_on_second_attempt(self):
        """
        **Validates: Requirements 4.1**
        
        Test that retry logic succeeds when API becomes available.
        Verifies that the service successfully returns a result when the API
        fails initially but succeeds on a retry attempt.
        """
        service = ClassificationService(
            api_url="https://api.example.com/classify",
            api_key="test-api-key"
        )
        
        with patch('app.services.classification_service.requests.post') as mock_post, \
             patch('app.services.classification_service.time.sleep') as mock_sleep:
            # First attempt fails, second succeeds
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'category': 'billing',
                'confidence': 0.88
            }
            
            mock_post.side_effect = [
                requests.exceptions.ConnectionError("Network error"),
                mock_response
            ]
            
            # Call should succeed on second attempt
            result = service.classify_text("Test text")
            
            # Verify result
            assert result.category == 'billing'
            assert result.confidence == 0.88
            
            # Verify retry occurred
            assert mock_post.call_count == 2
            assert mock_sleep.call_count == 1
            assert mock_sleep.call_args[0][0] == 1  # 2^0 = 1 second backoff
    
    def test_timeout_handling(self):
        """
        **Validates: Requirements 4.4**
        
        Test timeout handling.
        Verifies that network timeouts are treated as retriable errors
        and the service retries up to 3 times before failing.
        """
        service = ClassificationService(
            api_url="https://api.example.com/classify",
            api_key="test-api-key"
        )
        
        with patch('app.services.classification_service.requests.post') as mock_post, \
             patch('app.services.classification_service.time.sleep') as mock_sleep:
            # Mock timeout on all attempts
            mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
            
            # Verify that ClassificationAPIError is raised
            with pytest.raises(ClassificationAPIError) as exc_info:
                service.classify_text("Test text")
            
            # Verify retry attempts
            assert mock_post.call_count == 3
            assert "Failed after 3 retries" in str(exc_info.value)
            
            # Verify exponential backoff occurred
            assert mock_sleep.call_count == 2
    
    def test_malformed_api_response_missing_category(self):
        """
        **Validates: Requirements 3.5**
        
        Test malformed API response handling - missing category field.
        Verifies that the service raises ValueError when the API response
        is missing the required 'category' field.
        """
        service = ClassificationService(
            api_url="https://api.example.com/classify",
            api_key="test-api-key"
        )
        
        with patch('app.services.classification_service.requests.post') as mock_post:
            # Mock response missing 'category' field
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'confidence': 0.85
                # 'category' is missing
            }
            mock_post.return_value = mock_response
            
            # Verify that ValueError is raised
            with pytest.raises(ValueError) as exc_info:
                service.classify_text("Test text")
            
            assert "Invalid API response format: missing required fields" in str(exc_info.value)
            assert "confidence" in str(exc_info.value)
    
    def test_malformed_api_response_missing_confidence(self):
        """
        **Validates: Requirements 3.5**
        
        Test malformed API response handling - missing confidence field.
        Verifies that the service raises ValueError when the API response
        is missing the required 'confidence' field.
        """
        service = ClassificationService(
            api_url="https://api.example.com/classify",
            api_key="test-api-key"
        )
        
        with patch('app.services.classification_service.requests.post') as mock_post:
            # Mock response missing 'confidence' field
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'category': 'technical_support'
                # 'confidence' is missing
            }
            mock_post.return_value = mock_response
            
            # Verify that ValueError is raised
            with pytest.raises(ValueError) as exc_info:
                service.classify_text("Test text")
            
            assert "Invalid API response format: missing required fields" in str(exc_info.value)
            assert "category" in str(exc_info.value)
    
    def test_malformed_api_response_missing_both_fields(self):
        """
        **Validates: Requirements 3.5**
        
        Test malformed API response handling - missing both required fields.
        Verifies that the service raises ValueError when the API response
        is missing both 'category' and 'confidence' fields.
        """
        service = ClassificationService(
            api_url="https://api.example.com/classify",
            api_key="test-api-key"
        )
        
        with patch('app.services.classification_service.requests.post') as mock_post:
            # Mock response with empty object
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_post.return_value = mock_response
            
            # Verify that ValueError is raised
            with pytest.raises(ValueError) as exc_info:
                service.classify_text("Test text")
            
            assert "Invalid API response format: missing required fields" in str(exc_info.value)
    
    def test_non_200_status_code_triggers_retry(self):
        """
        **Validates: Requirements 4.1**
        
        Test that non-200 status codes trigger retry logic.
        Verifies that the service retries when the API returns error status codes.
        """
        service = ClassificationService(
            api_url="https://api.example.com/classify",
            api_key="test-api-key"
        )
        
        with patch('app.services.classification_service.requests.post') as mock_post, \
             patch('app.services.classification_service.time.sleep') as mock_sleep:
            # Mock 500 error on all attempts
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response
            
            # Verify that ClassificationAPIError is raised
            with pytest.raises(ClassificationAPIError) as exc_info:
                service.classify_text("Test text")
            
            # Verify retry attempts
            assert mock_post.call_count == 3
            assert "Failed after 3 retries" in str(exc_info.value)
            assert mock_sleep.call_count == 2
    
    def test_empty_text_raises_value_error(self):
        """
        Test that empty text input raises ValueError.
        Verifies input validation before making API calls.
        """
        service = ClassificationService(
            api_url="https://api.example.com/classify",
            api_key="test-api-key"
        )
        
        with pytest.raises(ValueError) as exc_info:
            service.classify_text("")
        
        assert "Text cannot be empty" in str(exc_info.value)
    
    def test_whitespace_only_text_raises_value_error(self):
        """
        Test that whitespace-only text raises ValueError.
        Verifies input validation trims whitespace before checking.
        """
        service = ClassificationService(
            api_url="https://api.example.com/classify",
            api_key="test-api-key"
        )
        
        with pytest.raises(ValueError) as exc_info:
            service.classify_text("   \n\t  ")
        
        assert "Text cannot be empty" in str(exc_info.value)
