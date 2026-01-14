#!/bin/bash
# Test runner for session continuity service
# 🏆 Breaking Barriers UK 2026 compliant

# Set AWS region (required for hackathon)
export AWS_DEFAULT_REGION=us-west-2
export AWS_REGION=us-west-2

# Set dummy AWS credentials for testing (tests use mocks)
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test

# Run the tests
python3 -m pytest tests/test_session_continuity_service.py -v --tb=short
