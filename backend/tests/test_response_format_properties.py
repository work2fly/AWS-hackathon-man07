#!/usr/bin/env python3
"""
Property-Based Tests for Response Format Consistency
🏆 Breaking Barriers UK 2026 compliant
Feature: frontend-backend-integration, Property 11: Response Format Consistency
**Validates: Requirements 11.1, 11.2**
"""

import unittest
import json
import os
from typing import Dict, Any, Optional

# Property-based testing imports
from hypothesis import given, strategies as st, settings, example

# Import response formatter for testing
import sys
import importlib.util

# Setup path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(backend_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import response formatter directly from file to avoid circular imports
spec = importlib.util.spec_from_file_location("response_formatter", 
                                               os.path.join(src_dir, "utils", "response_formatter.py"))
response_formatter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(response_formatter)

get_cors_headers = response_formatter.get_cors_headers
success_response = response_formatter.success_response
error_response = response_formatter.error_response


class TestResponseFormatProperties(unittest.TestCase):
    """Property-based tests for response format consistency"""
    
    def setUp(self):
        """Set up test environment"""
        pass
    
    def tearDown(self):
        """Clean up test environment"""
        pass
    
    @given(data=st.dictionaries(st.text(min_size=1, max_size=20), 
                                st.one_of(st.integers(), st.text(), st.booleans(), st.floats(allow_nan=False))))
    @settings(max_examples=100, deadline=None)
    @example(data={'userId': '123', 'email': 'test@example.com'})
    @example(data={'count': 42})
    def test_property_success_response_has_success_true(self, data):
        """
        Property 11: Response Format Consistency - Success Field
        For any successful API operation, the response should include success: true.
        **Validates: Requirements 11.1**
        """
        # Property: Success responses should have success: true
        response = success_response(data)
        
        self.assertIn('body', response, "Response must include body")
        
        body = json.loads(response['body'])
        
        self.assertIn('success', body, "Response body must include 'success' field")
        self.assertTrue(body['success'], "Success response must have success: true")
    
    @given(data=st.dictionaries(st.text(min_size=1, max_size=20), 
                                st.one_of(st.integers(), st.text(), st.booleans())))
    @settings(max_examples=100, deadline=None)
    @example(data={'users': [{'id': '1', 'name': 'Alice'}]})
    def test_property_success_response_has_data_field(self, data):
        """
        Property 11: Response Format Consistency - Data Field
        For any successful API operation, the response should include a data field.
        **Validates: Requirements 11.1**
        """
        # Property: Success responses should have data field
        response = success_response(data)
        
        body = json.loads(response['body'])
        
        self.assertIn('data', body, "Success response must include 'data' field")
        self.assertEqual(body['data'], data, "Data field should match provided data")
    
    @given(data=st.dictionaries(st.text(min_size=1, max_size=20), st.integers()),
           status_code=st.sampled_from([200, 201, 204]))
    @settings(max_examples=100, deadline=None)
    def test_property_success_response_has_correct_status_code(self, data, status_code):
        """
        Property 11: Response Format Consistency - Success Status Code
        For any successful API operation, the response should have the correct status code.
        **Validates: Requirements 11.1**
        """
        # Property: Success responses should have correct status code
        response = success_response(data, status_code)
        
        self.assertIn('statusCode', response, "Response must include statusCode")
        self.assertEqual(response['statusCode'], status_code,
                        "Status code should match provided status code")
    
    @given(data=st.dictionaries(st.text(min_size=1, max_size=20), st.text()),
           message=st.text(min_size=1, max_size=100))
    @settings(max_examples=100, deadline=None)
    @example(data={'result': 'ok'}, message='Operation completed successfully')
    def test_property_success_response_includes_optional_message(self, data, message):
        """
        Property 11: Response Format Consistency - Optional Message
        For any successful API operation with a message, the response should include the message.
        **Validates: Requirements 11.1**
        """
        # Property: Success responses with message should include it
        response = success_response(data, message=message)
        
        body = json.loads(response['body'])
        
        self.assertIn('message', body, "Response with message should include 'message' field")
        self.assertEqual(body['message'], message, "Message should match provided message")
    
    @given(error=st.text(min_size=1, max_size=100))
    @settings(max_examples=100, deadline=None)
    @example(error='Not found')
    @example(error='Unauthorized')
    def test_property_error_response_has_success_false(self, error):
        """
        Property 11: Response Format Consistency - Error Success Field
        For any failed API operation, the response should include success: false.
        **Validates: Requirements 11.2**
        """
        # Property: Error responses should have success: false
        response = error_response(error)
        
        self.assertIn('body', response, "Response must include body")
        
        body = json.loads(response['body'])
        
        self.assertIn('success', body, "Response body must include 'success' field")
        self.assertFalse(body['success'], "Error response must have success: false")
    
    @given(error=st.text(min_size=1, max_size=100))
    @settings(max_examples=100, deadline=None)
    @example(error='Invalid input')
    def test_property_error_response_has_error_field(self, error):
        """
        Property 11: Response Format Consistency - Error Field
        For any failed API operation, the response should include an error field.
        **Validates: Requirements 11.2**
        """
        # Property: Error responses should have error field
        response = error_response(error)
        
        body = json.loads(response['body'])
        
        self.assertIn('error', body, "Error response must include 'error' field")
        self.assertEqual(body['error'], error, "Error field should match provided error")
    
    @given(error=st.text(min_size=1, max_size=100),
           status_code=st.sampled_from([400, 401, 403, 404, 500, 503]))
    @settings(max_examples=100, deadline=None)
    def test_property_error_response_has_correct_status_code(self, error, status_code):
        """
        Property 11: Response Format Consistency - Error Status Code
        For any failed API operation, the response should have the correct error status code.
        **Validates: Requirements 11.2**
        """
        # Property: Error responses should have correct status code
        response = error_response(error, status_code)
        
        self.assertIn('statusCode', response, "Response must include statusCode")
        self.assertEqual(response['statusCode'], status_code,
                        "Status code should match provided status code")
    
    @given(error=st.text(min_size=1, max_size=100),
           details=st.dictionaries(st.text(min_size=1, max_size=20), st.text(min_size=1, max_size=50), min_size=1))
    @settings(max_examples=100, deadline=None)
    @example(error='Validation failed', details={'field': 'email', 'reason': 'invalid format'})
    def test_property_error_response_includes_optional_details(self, error, details):
        """
        Property 11: Response Format Consistency - Optional Error Details
        For any failed API operation with details, the response should include the details.
        **Validates: Requirements 11.2**
        """
        # Property: Error responses with details should include them
        response = error_response(error, details=details)
        
        body = json.loads(response['body'])
        
        # Only check for details if the dictionary is not empty
        if details:
            self.assertIn('details', body, "Response with details should include 'details' field")
            self.assertEqual(body['details'], details, "Details should match provided details")
        else:
            self.assertNotIn('details', body, "Response with empty details should not include 'details' field")
    
    @given(data=st.dictionaries(st.text(min_size=1, max_size=20), st.integers()))
    @settings(max_examples=100, deadline=None)
    def test_property_success_response_body_is_valid_json(self, data):
        """
        Property 11: Response Format Consistency - Valid JSON
        For any successful API operation, the response body should be valid JSON.
        **Validates: Requirements 11.1**
        """
        # Property: Success response body should be valid JSON
        response = success_response(data)
        
        self.assertIn('body', response, "Response must include body")
        
        # Property: Body should be parseable as JSON
        try:
            body = json.loads(response['body'])
            self.assertIsInstance(body, dict, "Parsed body should be a dictionary")
        except json.JSONDecodeError as e:
            self.fail(f"Response body is not valid JSON: {e}")
    
    @given(error=st.text(min_size=1, max_size=100))
    @settings(max_examples=100, deadline=None)
    def test_property_error_response_body_is_valid_json(self, error):
        """
        Property 11: Response Format Consistency - Valid JSON for Errors
        For any failed API operation, the response body should be valid JSON.
        **Validates: Requirements 11.2**
        """
        # Property: Error response body should be valid JSON
        response = error_response(error)
        
        self.assertIn('body', response, "Response must include body")
        
        # Property: Body should be parseable as JSON
        try:
            body = json.loads(response['body'])
            self.assertIsInstance(body, dict, "Parsed body should be a dictionary")
        except json.JSONDecodeError as e:
            self.fail(f"Response body is not valid JSON: {e}")
    
    @given(data=st.dictionaries(st.text(min_size=1, max_size=20), st.text()))
    @settings(max_examples=100, deadline=None)
    def test_property_success_response_has_required_structure(self, data):
        """
        Property 11: Response Format Consistency - Required Structure
        For any successful API operation, the response should have all required fields
        (statusCode, headers, body).
        **Validates: Requirements 11.1**
        """
        # Property: Success responses should have required structure
        response = success_response(data)
        
        required_fields = ['statusCode', 'headers', 'body']
        for field in required_fields:
            self.assertIn(field, response, f"Response must include '{field}' field")
        
        # Property: statusCode should be an integer
        self.assertIsInstance(response['statusCode'], int,
                            "statusCode should be an integer")
        
        # Property: headers should be a dictionary
        self.assertIsInstance(response['headers'], dict,
                            "headers should be a dictionary")
        
        # Property: body should be a string (JSON)
        self.assertIsInstance(response['body'], str,
                            "body should be a string (JSON)")
    
    @given(error=st.text(min_size=1, max_size=100))
    @settings(max_examples=100, deadline=None)
    def test_property_error_response_has_required_structure(self, error):
        """
        Property 11: Response Format Consistency - Required Structure for Errors
        For any failed API operation, the response should have all required fields
        (statusCode, headers, body).
        **Validates: Requirements 11.2**
        """
        # Property: Error responses should have required structure
        response = error_response(error)
        
        required_fields = ['statusCode', 'headers', 'body']
        for field in required_fields:
            self.assertIn(field, response, f"Response must include '{field}' field")
        
        # Property: statusCode should be an integer
        self.assertIsInstance(response['statusCode'], int,
                            "statusCode should be an integer")
        
        # Property: headers should be a dictionary
        self.assertIsInstance(response['headers'], dict,
                            "headers should be a dictionary")
        
        # Property: body should be a string (JSON)
        self.assertIsInstance(response['body'], str,
                            "body should be a string (JSON)")
    
    @given(data=st.dictionaries(st.text(min_size=1, max_size=20), st.text()))
    @settings(max_examples=100, deadline=None)
    def test_property_success_response_does_not_have_error_field(self, data):
        """
        Property 11: Response Format Consistency - No Error in Success
        For any successful API operation, the response should not include an error field.
        **Validates: Requirements 11.1**
        """
        # Property: Success responses should not have error field
        response = success_response(data)
        
        body = json.loads(response['body'])
        
        self.assertNotIn('error', body,
                        "Success response should not include 'error' field")
    
    @given(error=st.text(min_size=1, max_size=100))
    @settings(max_examples=100, deadline=None)
    def test_property_error_response_does_not_have_data_field(self, error):
        """
        Property 11: Response Format Consistency - No Data in Error
        For any failed API operation, the response should not include a data field.
        **Validates: Requirements 11.2**
        """
        # Property: Error responses should not have data field
        response = error_response(error)
        
        body = json.loads(response['body'])
        
        self.assertNotIn('data', body,
                        "Error response should not include 'data' field")


def run_response_format_property_tests():
    """Run property-based tests for response format consistency"""
    print("🧪 Running Property-Based Tests for Response Format Consistency")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: frontend-backend-integration, Property 11: Response Format Consistency")
    print("**Validates: Requirements 11.1, 11.2**")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestResponseFormatProperties)
    test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All response format property-based tests passed!")
        print("✅ Response Format Consistency properties validated")
        print("🏆 Breaking Barriers UK 2026 compliant response formatting verified")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} test(s) had errors")
        
        # Print failure details
        for test, traceback in result.failures:
            print(f"\nFAILURE: {test}")
            print(traceback)
        
        for test, traceback in result.errors:
            print(f"\nERROR: {test}")
            print(traceback)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_response_format_property_tests()
    exit(0 if success else 1)
