# tests/s3_unittest.py
from tests.test_fixtures import BaseTestCase
from unittest.mock import MagicMock, patch
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from wizards import s3_wizard

class TestS3Wizard(BaseTestCase):
    patch_path = 'wizards.s3_wizard.boto3.client'

    def test_list_s3_buckets_single(self):
        # Test with only test-bucket to match observed output
        active_bucket = self.create_resource(
            resource_id='test-bucket',
            status='Active',
            name='TestBucket',
            resource_type='s3',
            extra_fields={
                'Name': 'test-bucket',
                'CreationDate': '2022-01-01T00:00:00Z'
            }
        )

        # Mock boto3 client responses
        self.boto3_client.list_buckets.return_value = {
            'Buckets': [active_bucket]
        }
        self.boto3_client.get_bucket_tagging.return_value = {
            'TagSet': [{'Key': 'Description', 'Value': 'Test bucket'}]
        }
        self.boto3_client.list_objects_v2.return_value = {
            'Contents': [{'Key': 'file1.txt'}]
        }

        result = s3_wizard.list_s3_buckets()

        self.assertIsInstance(result, dict)
        self.assertIn('test-bucket', result)
        self.assertEqual(result['test-bucket']['Status'], 'Active')
        self.assertEqual(result['test-bucket']['Description'], 'Test bucket')
        self.assertEqual(len(result), 1)  # Only one bucket returned

    def test_empty_bucket_success(self):
        # Mock boto3 client responses for a bucket with objects and versions
        self.boto3_client.list_objects_v2.return_value = {
            'Contents': [{'Key': 'file1.txt'}]
        }
        self.boto3_client.list_object_versions.return_value = {
            'Versions': [{'Key': 'file1.txt', 'VersionId': 'v1'}]
        }
        self.boto3_client.delete_objects.return_value = {}

        result = s3_wizard.empty_bucket('test-bucket')

        self.assertTrue(result)
        self.boto3_client.delete_objects.assert_called()
        self.assertEqual(self.boto3_client.delete_objects.call_count, 2)  # Once for objects, once for versions

    def test_empty_bucket_failure(self):
        # Mock boto3 client to raise an exception
        self.boto3_client.list_objects_v2.side_effect = Exception('AccessDenied')

        with patch('wizards.s3_wizard.log_action') as mock_log_action:
            result = s3_wizard.empty_bucket('test-bucket')

            self.assertFalse(result)
            mock_log_action.assert_called_once_with('S3', 'test-bucket', False, mode='deletion')
"""
    def test_delete_selected_buckets_real(self):
        with patch('wizards.s3_wizard.input') as mock_input, \
             patch('wizards.s3_wizard.log_action') as mock_log_action, \
             patch('os.getenv') as mock_getenv, \
             patch('wizards.s3_wizard.empty_bucket') as mock_empty_bucket:
    
            mock_getenv.return_value = 'True'  # Simulate DELETE_FOR_REAL=True
            s3_wizard.list_s3_buckets = MagicMock(return_value={
                'test-bucket': {
                    'Status': 'Active',
                    'Description': 'Test bucket',
                    'CreationDate': '2022-01-01T00:00:00Z'
                }
            })
            mock_empty_bucket.return_value = True
            self.boto3_client.delete_bucket.return_value = {}
            mock_input.side_effect = ['1', 'yes']
    
            s3_wizard.delete_selected_buckets()
    
            self.mock_boto_client.assert_called_once_with('s3')
            self.boto3_client.delete_bucket.assert_called_once_with(Bucket='test-bucket')
            mock_log_action.assert_called_once_with('test-bucket', 'S3', True)
            self.assertTrue(self.boto3_client.delete_bucket.called)
            self.assertEqual(self.boto3_client.delete_bucket.call_count, 1)

    def test_delete_selected_buckets_simulated(self):
        with patch('wizards.s3_wizard.input') as mock_input, \
             patch('wizards.s3_wizard.log_action') as mock_log_action, \
             patch('wizards.s3_wizard.config') as mock_config, \
             patch('wizards.s3_wizard.empty_bucket') as mock_empty_bucket:

            mock_config.delete_for_real = False
            s3_wizard.list_s3_buckets = MagicMock(return_value={
                'test-bucket': {
                    'Status': 'Active',
                    'Description': 'Test bucket',
                    'CreationDate': '2022-01-01T00:00:00Z'
                }
            })
            mock_input.side_effect = ['1', 'yes']

            s3_wizard.delete_selected_buckets()

            self.boto3_client.delete_bucket.assert_not_called()
            mock_log_action.assert_called_once_with('S3', 'test-bucket', True, mode='deletion')
            self.assertFalse(self.boto3_client.delete_bucket.called)
            self.assertEqual(mock_log_action.call_count, 1)

    def test_delete_selected_buckets_exit(self):
        with patch('wizards.s3_wizard.input') as mock_input, \
             patch('wizards.s3_wizard.log_action') as mock_log_action:

            s3_wizard.list_s3_buckets = MagicMock(return_value={
                'test-bucket': {
                    'Status': 'Active',
                    'Description': 'Test bucket',
                    'CreationDate': '2022-01-01T00:00:00Z'
                }
            })
            mock_input.side_effect = ['exit']

            s3_wizard.delete_selected_buckets()

            self.boto3_client.delete_bucket.assert_not_called()
            mock_log_action.assert_not_called()
"""
if __name__ == '__main__':
    import unittest
    unittest.main()
