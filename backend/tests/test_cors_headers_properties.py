#!/usr/bin/env python3
"""
Property-Based Tests for CORS Headers Consistency
🏆 Breaking Barriers UK 2026 compliant
Feature: frontend-backend-integration, Property 10: CORS Headers Consistency
**Validates: Requirements 10.1-10.6**
"""

import unittest
import json
import os
from typing import Dict, Any, Optional
from unittest.mock import patch

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


class TestCORSHeadersProperties(unittest.TestCase):
    """Property-based tests for CORS headers consistency"""
    
    def setUp(self):
        """Set up test environment"""
        # Clear environment variables
        if 'ENVIRONMENT' in os.environ:
            del os.environ['ENVIRONMENT']
        if 'ALLOWED_ORIGIN' in os.environ:
            del os.environ['ALLOWED_ORIGIN']
    
    def tearDown(self):
        """Clean up test environment"""
        # Clear environment variables
        if 'ENVIRONMENT' in os.environ:
            del os.environ['ENVIRONMENT']
        if 'ALLOWED_ORIGIN' in os.environ:
            del os.environ['ALLOWED_ORIGIN']
    
    @given(origin=st.sampled_from(['*', 'http://localhost:3000', 'https://example.com', 'https://therapy.app']))
    @settings(max_examples=100, deadline=None)
    @example(origin='*')
    @example(origin='http://localhost:3000')
    def test_property_cors_headers_include_origin(self, origin):
        """
        Property 10: CORS Headers Consistency - Origin Header
        For any API response, the response should include Access-Control-Allow-Origin header.
        **Validates: Requirements 10.1**
        """
        # Property: CORS headers should always include Access-Control-Allow-Origin
        headers = get_cors_headers(origin)
        
        self.assertIn('Access-Control-Allow-Origin', headers,
                     "CORS headers must include Access-Control-Allow-Origin")
        self.assertIsInstance(headers['Access-Control-Allow-Origin'], str,
                            "Access-Control-Allow-Origin must be a string")
        self.assertTrue(len(headers['Access-Control-Allow-Origin']) > 0,
                       "Access-Control-Allow-Origin must not be empty")
    
    @given(origin=st.sampled_from(['*', 'http://localhost:3000', 'https://example.com']))
    @settings(max_examples=100, deadline=None)
    def test_property_cors_headers_include_methods(self, origin):
        """
        Property 10: CORS Headers Consistency - Methods Header
        For any API response, the response should include Access-Control-Allow-Methods header
        with allowed HTTP methods.
        **Validates: Requirements 10.2**
        """
        # Property: CORS headers should always include Access-Control-Allow-Methods
        headers = get_cors_headers(origin)
        
        self.assertIn('Access-Control-Allow-Methods', headers,
                     "CORS headers must include Access-Control-Allow-Methods")
        
        methods = headers['Access-Control-Allow-Methods']
        self.assertIsInstance(methods, str, "Access-Control-Allow-Methods must be a string")
        
        # Property: Methods should include standard HTTP methods
        required_methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        for method in required_methods:
            self.assertIn(method, methods,
                         f"Access-Control-Allow-Methods must include {method}")
    
    @given(origin=st.sampled_from(['*', 'http://localhost:3000', 'https://example.com']))
    @settings(max_examples=100, deadline=None)
    def test_property_cors_headers_include_allowed_headers(self, origin):
        """
        Property 10: CORS Headers Consistency - Allowed Headers
        For any API response, the response should include Access-Control-Allow-Headers header
        with allowed request headers.
        **Validates: Requirements 10.3**
        """
        # Property: CORS headers should always include Access-Control-Allow-Headers
        headers = get_cors_headers(origin)
        
        self.assertIn('Access-Control-Allow-Headers', headers,
                     "CORS headers must include Access-Control-Allow-Headers")
        
        allowed_headers = headers['Access-Control-Allow-Headers']
        self.assertIsInstance(allowed_headers, str,
                            "Access-Control-Allow-Headers must be a string")
        
        # Property: Should include common headers
        required_headers = ['Content-Type', 'Authorization']
        for header in required_headers:
            self.assertIn(header, allowed_headers,
                         f"Access-Control-Allow-Headers must include {header}")
    
    @given(data=st.dictionaries(st.text(min_size=1, max_size=20), st.integers()))
    @settings(max_examples=100, deadline=None)
    @example(data={'count': 42})
    def test_property_success_response_includes_cors_headers(self, data):
        """
        Property 10: CORS Headers Consistency - Success Response
        For any successful API response, the response should include all required CORS headers.
        **Validates: Requirements 10.1, 10.2, 10.3**
        """
        # Property: Success responses should include CORS headers
        response = success_response(data)
        
        self.assertIn('headers', response, "Response must include headers")
        headers = response['headers']
        
        # Property: All required CORS headers should be present
        required_cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers'
        ]
        
        for cors_header in required_cors_headers:
            self.assertIn(cors_header, headers,
                         f"Success response must include {cors_header}")
    
    @given(error=st.text(min_size=1, max_size=100),
           status_code=st.sampled_from([400, 401, 403, 404, 500]))
    @settings(max_examples=100, deadline=None)
    @example(error='Not found', status_code=404)
    @example(error='Unauthorized', status_code=401)
    def test_property_error_response_includes_cors_headers(self, error, status_code):
        """
        Property 10: CORS Headers Consistency - Error Response
        For any error API response, the response should include all required CORS headers.
        **Validates: Requirements 10.1, 10.2, 10.3**
        """
        # Property: Error responses should include CORS headers
        response = error_response(error, status_code)
        
        self.assertIn('headers', response, "Response must include headers")
        headers = response['headers']
        
        # Property: All required CORS headers should be present
        required_cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers'
        ]
        
        for cors_header in required_cors_headers:
            self.assertIn(cors_header, headers,
                         f"Error response must include {cors_header}")
    
    @given(origin=st.sampled_from(['*', 'http://localhost:3000', 'https://example.com']))
    @settings(max_examples=100, deadline=None)
    def test_property_cors_headers_include_content_type(self, origin):
        """
        Property 10: CORS Headers Consistency - Content-Type Header
        For any API response, the response should include Content-Type header.
        **Validates: Requirements 10.1-10.6**
        """
        # Property: CORS headers should include Content-Type
        headers = get_cors_headers(origin)
        
        self.assertIn('Content-Type', headers,
                     "Headers must include Content-Type")
        self.assertEqual(headers['Content-Type'], 'application/json',
                        "Content-Type must be application/json")
    
    def test_property_development_environment_allows_wildcard(self):
        """
        Property 10: CORS Headers Consistency - Development Environment
        In development environment, the system should allow wildcard origins.
        **Validates: Requirements 10.5**
        """
        # Set development environment
        os.environ['ENVIRONMENT'] = 'development'
        
        # Property: Development should allow wildcard
        headers = get_cors_headers('*')
        
        self.assertEqual(headers['Access-Control-Allow-Origin'], '*',
                        "Development environment should allow wildcard origin")
    
    @given(allowed_origin=st.sampled_from(['https://production.com', 'https://app.therapy.com']))
    @settings(max_examples=100, deadline=None)
    @example(allowed_origin='https://production.com')
    def test_property_production_environment_uses_configured_origin(self, allowed_origin):
        """
        Property 10: CORS Headers Consistency - Production Environment
        In production environment, the system should use configured production origins.
        **Validates: Requirements 10.6**
        """
        # Set production environment
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['ALLOWED_ORIGIN'] = allowed_origin
        
        # Property: Production should use configured origin
        headers = get_cors_headers()
        
        self.assertEqual(headers['Access-Control-Allow-Origin'], allowed_origin,
                        "Production environment should use configured origin")
    
    @given(data=st.dictionaries(st.text(min_size=1, max_size=20), st.text(min_size=1, max_size=50)),
           status_code=st.sampled_from([200, 201, 204]))
    @settings(max_examples=100, deadline=None)
    def test_property_all_success_responses_have_consistent_cors(self, data, status_code):
        """
        Property 10: CORS Headers Consistency - Consistency Across Success Responses
        For any successful API response with any status code,
        the CORS headers should be consistent.
        **Validates: Requirements 10.1-10.6**
        """
        # Property: All success responses should have identical CORS headers
        response = success_response(data, status_code)
        
        headers = response['headers']
        
        # Get reference CORS headers
        reference_cors = get_cors_headers()
        
        # Property: CORS headers should match reference
        for key in ['Access-Control-Allow-Origin', 'Access-Control-Allow-Methods',
                   'Access-Control-Allow-Headers']:
            self.assertEqual(headers[key], reference_cors[key],
                           f"CORS header {key} should be consistent across all responses")
    
    @given(error=st.text(min_size=1, max_size=100),
           status_code=st.sampled_from([400, 401, 403, 404, 500, 503]))
    @settings(max_examples=100, deadline=None)
    def test_property_all_error_responses_have_consistent_cors(self, error, status_code):
        """
        Property 10: CORS Headers Consistency - Consistency Across Error Responses
        For any error API response with any status code,
        the CORS headers should be consistent.
        **Validates: Requirements 10.1-10.6**
        """
        # Property: All error responses should have identical CORS headers
        response = error_response(error, status_code)
        
        headers = response['headers']
        
        # Get reference CORS headers
        reference_cors = get_cors_headers()
        
        # Property: CORS headers should match reference
        for key in ['Access-Control-Allow-Origin', 'Access-Control-Allow-Methods',
                   'Access-Control-Allow-Headers']:
            self.assertEqual(headers[key], reference_cors[key],
                           f"CORS header {key} should be consistent across all responses")
    
    @given(origin=st.sampled_from(['*', 'http://localhost:3000', 'https://example.com']))
    @settings(max_examples=100, deadline=None)
    def test_property_cors_headers_allow_credentials(self, origin):
        """
        Property 10: CORS Headers Consistency - Credentials Support
        For any API response, the response should include Access-Control-Allow-Credentials
        to support authenticated requests.
        **Validates: Requirements 10.1-10.6**
        """
        # Property: CORS headers should allow credentials
        headers = get_cors_headers(origin)
        
        self.assertIn('Access-Control-Allow-Credentials', headers,
                     "CORS headers should include Access-Control-Allow-Credentials")
        self.assertEqual(headers['Access-Control-Allow-Credentials'], 'true',
                        "Access-Control-Allow-Credentials should be 'true'")


def run_cors_headers_property_tests():
    """Run property-based tests for CORS headers consistency"""
    print("🧪 Running Property-Based Tests for CORS Headers Consistency")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: frontend-backend-integration, Property 10: CORS Headers Consistency")
    print("**Validates: Requirements 10.1-10.6**")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestCORSHeadersProperties)
    test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All CORS headers property-based tests passed!")
        print("✅ CORS Headers Consistency properties validated")
        print("🏆 Breaking Barriers UK 2026 compliant CORS configuration verified")
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
    success = run_cors_headers_property_tests()
    exit(0 if success else 1)
