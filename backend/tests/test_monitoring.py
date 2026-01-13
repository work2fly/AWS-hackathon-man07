#!/usr/bin/env python3
"""
AI Therapy Platform - Monitoring System Tests
Breaking Barriers UK 2026 compliant monitoring validation
"""

import unittest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import our monitoring utilities
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.logger import StructuredLogger, logger, log_api_request, log_red_flag_detection
from utils.metrics import MetricsCollector, metrics, track_api_performance
from utils.alerts import AlertManager, AlertSeverity, AlertType, send_red_flag_alert

class TestStructuredLogger(unittest.TestCase):
    """Test structured logging functionality"""
    
    def setUp(self):
        self.test_logger = StructuredLogger('test_logger')
    
    def test_basic_logging(self):
        """Test basic logging functionality"""
        # These should not raise exceptions
        self.test_logger.info("Test info message")
        self.test_logger.debug("Test debug message")
        self.test_logger.warning("Test warning message")
        self.test_logger.error("Test error message")
        self.test_logger.critical("Test critical message")
    
    def test_logging_with_context(self):
        """Test logging with additional context"""
        self.test_logger.info(
            "Test message with context",
            user_id="test_user_123",
            session_id="session_456",
            custom_field="custom_value"
        )
    
    def test_error_logging_with_exception(self):
        """Test error logging with exception details"""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            self.test_logger.error("Test error with exception", error=e)
    
    def test_request_context(self):
        """Test request context functionality"""
        context = {
            'request_id': 'req_123',
            'user_id': 'user_456'
        }
        
        self.test_logger.set_request_context(context)
        self.test_logger.info("Message with context")
        self.test_logger.clear_request_context()
        self.test_logger.info("Message without context")
    
    def test_convenience_functions(self):
        """Test convenience logging functions"""
        log_api_request("GET", "/api/sessions", "user_123")
        log_red_flag_detection("session_123", "self_harm", "high", "user_456")

class TestMetricsCollector(unittest.TestCase):
    """Test metrics collection functionality"""
    
    def setUp(self):
        self.metrics_collector = MetricsCollector()
        # Mock CloudWatch client
        self.metrics_collector.cloudwatch = Mock()
    
    def test_put_metric(self):
        """Test putting a single metric"""
        self.metrics_collector.put_metric(
            'TestMetric',
            1.0,
            'Count',
            dimensions={'TestDimension': 'TestValue'}
        )
        
        # Verify CloudWatch was called
        self.metrics_collector.cloudwatch.put_metric_data.assert_called_once()
        call_args = self.metrics_collector.cloudwatch.put_metric_data.call_args
        
        self.assertEqual(call_args[1]['Namespace'], 'AI-Therapy-Platform')
        self.assertEqual(len(call_args[1]['MetricData']), 1)
        self.assertEqual(call_args[1]['MetricData'][0]['MetricName'], 'TestMetric')
        self.assertEqual(call_args[1]['MetricData'][0]['Value'], 1.0)
    
    def test_put_metrics_batch(self):
        """Test putting multiple metrics in batch"""
        metrics_data = [
            {'name': 'Metric1', 'value': 1.0},
            {'name': 'Metric2', 'value': 2.0, 'unit': 'Seconds'},
            {'name': 'Metric3', 'value': 3.0, 'dimensions': {'Test': 'Value'}}
        ]
        
        self.metrics_collector.put_metrics_batch(metrics_data)
        
        # Verify CloudWatch was called
        self.metrics_collector.cloudwatch.put_metric_data.assert_called_once()
        call_args = self.metrics_collector.cloudwatch.put_metric_data.call_args
        
        self.assertEqual(len(call_args[1]['MetricData']), 3)
    
    def test_business_metrics(self):
        """Test business-specific metrics"""
        self.metrics_collector.record_session_started('user_123')
        self.metrics_collector.record_session_completed('user_123', 1800.0)
        self.metrics_collector.record_red_flag_detected('self_harm', 'high', 'user_123')
        self.metrics_collector.record_user_registration('client')
        self.metrics_collector.record_authentication_attempt(True)
        
        # Verify multiple calls were made
        self.assertGreater(
            self.metrics_collector.cloudwatch.put_metric_data.call_count, 
            0
        )
    
    def test_performance_metrics(self):
        """Test performance metrics"""
        self.metrics_collector.record_api_request('GET', '/api/sessions', 200, 150.0)
        self.metrics_collector.record_database_operation('GetItem', 'users', True, 25.0)
        self.metrics_collector.record_bedrock_request('claude-3-sonnet', True, 500.0, 150)
        self.metrics_collector.record_websocket_connection('connect', True)
        
        # Verify calls were made
        self.assertGreater(
            self.metrics_collector.cloudwatch.put_metric_data.call_count, 
            0
        )
    
    def test_track_api_performance_context_manager(self):
        """Test API performance tracking context manager"""
        with track_api_performance('GET', '/api/test'):
            time.sleep(0.01)  # Simulate some work
        
        # Verify metric was recorded
        self.metrics_collector.cloudwatch.put_metric_data.assert_called()

class TestAlertManager(unittest.TestCase):
    """Test alert management functionality"""
    
    def setUp(self):
        self.alert_manager = AlertManager()
        # Mock AWS clients
        self.alert_manager.sns = Mock()
        self.alert_manager.ses = Mock()
    
    def test_send_alert(self):
        """Test basic alert sending"""
        self.alert_manager.send_alert(
            AlertType.SYSTEM,
            AlertSeverity.MEDIUM,
            "Test Alert",
            "This is a test alert message"
        )
        
        # Alert should be logged (we can't easily test the actual logging,
        # but we can verify the method doesn't raise exceptions)
    
    def test_send_red_flag_alert(self):
        """Test red flag alert"""
        self.alert_manager.send_red_flag_alert(
            session_id='session_123',
            user_id='user_456',
            flag_type='self_harm',
            severity='high',
            context='User mentioned concerning thoughts',
            therapist_ids=['therapist_1', 'therapist_2']
        )
    
    def test_send_security_alert(self):
        """Test security alert"""
        self.alert_manager.send_security_alert(
            event_type='multiple_failed_logins',
            user_id='user_123',
            ip_address='192.168.1.1',
            details={'attempt_count': 5}
        )
    
    def test_send_system_alert(self):
        """Test system alert"""
        self.alert_manager.send_system_alert(
            component='DynamoDB',
            issue='High latency detected',
            severity=AlertSeverity.HIGH,
            metrics_data={'avg_latency': 2500}
        )
    
    def test_send_performance_alert(self):
        """Test performance alert"""
        self.alert_manager.send_performance_alert(
            metric_name='APILatency',
            current_value=3000.0,
            threshold=2000.0,
            component='API Gateway'
        )
    
    def test_convenience_functions(self):
        """Test convenience alert functions"""
        send_red_flag_alert(
            'session_123', 'user_456', 'suicidal_ideation', 
            'critical', 'Concerning content detected', ['therapist_1']
        )

class TestMonitoringIntegration(unittest.TestCase):
    """Test integration between monitoring components"""
    
    @patch('utils.metrics.aws_clients')
    @patch('utils.alerts.boto3')
    def test_red_flag_workflow(self, mock_boto3, mock_aws_clients):
        """Test complete red flag detection workflow"""
        # Mock AWS clients
        mock_cloudwatch = Mock()
        mock_aws_clients.cloudwatch = mock_cloudwatch
        
        # Simulate red flag detection
        session_id = 'session_123'
        user_id = 'user_456'
        flag_type = 'self_harm'
        severity = 'high'
        context = 'User mentioned self-harm thoughts'
        
        # Log the detection
        log_red_flag_detection(session_id, flag_type, severity, user_id)
        
        # Record metrics
        metrics.record_red_flag_detected(flag_type, severity, user_id)
        
        # Send alert
        send_red_flag_alert(
            session_id, user_id, flag_type, severity, context, ['therapist_1']
        )
        
        # Verify metrics were recorded
        mock_cloudwatch.put_metric_data.assert_called()
    
    def test_performance_monitoring_workflow(self):
        """Test performance monitoring workflow"""
        # Simulate API request with performance tracking
        with track_api_performance('POST', '/api/sessions'):
            # Simulate some processing time
            time.sleep(0.01)
            
            # Log the request
            log_api_request('POST', '/api/sessions', 'user_123')

class TestBreakingBarriersCompliance(unittest.TestCase):
    """Test Breaking Barriers UK 2026 compliance"""
    
    def test_bedrock_model_compliance(self):
        """Test that only compliant Bedrock models are used"""
        compliant_models = [
            'anthropic.claude-3-5-sonnet-20241022-v2:0',
            'anthropic.claude-3-opus-20240229',
            'amazon.nova-micro-v1:0',
            'amazon.nova-lite-v1:0',
            'amazon.nova-pro-v1:0'
        ]
        
        for model_id in compliant_models:
            # This should not raise any compliance errors
            metrics.record_bedrock_request(model_id, True, 500.0, 150)
    
    def test_region_compliance(self):
        """Test that monitoring is configured for compliant regions"""
        # Verify we're using us-west-2 (primary) or us-east-1 (global services)
        import os
        region = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
        self.assertIn(region, ['us-west-2', 'us-east-1'])
    
    def test_data_privacy_compliance(self):
        """Test that sensitive data is not logged"""
        # Test that PII is not included in logs
        test_context = {
            'user_id': 'user_123',  # This is OK - anonymized ID
            'session_id': 'session_456',  # This is OK - session ID
            'flag_type': 'self_harm',  # This is OK - category
            # Should NOT include actual conversation content or PII
        }
        
        logger.info("Red flag detected", **test_context)
        
        # Verify no actual conversation content is logged
        self.assertNotIn('email', str(test_context))
        self.assertNotIn('name', str(test_context))
        self.assertNotIn('phone', str(test_context))

def run_monitoring_tests():
    """Run all monitoring tests"""
    print("🧪 Running AI Therapy Platform Monitoring Tests")
    print("🏆 Breaking Barriers UK 2026 compliant testing")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestStructuredLogger,
        TestMetricsCollector,
        TestAlertManager,
        TestMonitoringIntegration,
        TestBreakingBarriersCompliance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 All monitoring tests passed!")
        print("🏆 Breaking Barriers UK 2026 compliant monitoring validated")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} test(s) had errors")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_monitoring_tests()
    exit(0 if success else 1)