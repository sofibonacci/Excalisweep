import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from wizards import s3_wizard

class TestS3Wizard(unittest.TestCase):

    @patch('wizards.s3_wizard.boto3.client')
    def test_list_s3_buckets_handles_active_and_inactive(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        mock_s3.list_buckets.return_value = {
            'Buckets': [
                {'Name': 'test-bucket-1', 'CreationDate': '2024-01-01T00:00:00Z'},
                {'Name': 'test-bucket-2', 'CreationDate': '2024-01-01T00:00:00Z'}
            ]
        }

        def mock_get_bucket_tagging(Bucket):
            return {'TagSet': [{'Key': 'Description', 'Value': f'{Bucket} description'}]}
        
        def mock_list_objects_v2(Bucket):
            return {'Contents': [{'Key': 'file1.txt'}]} if Bucket == 'test-bucket-1' else {}

        mock_s3.get_bucket_tagging.side_effect = mock_get_bucket_tagging
        mock_s3.list_objects_v2.side_effect = mock_list_objects_v2

        result = s3_wizard.list_s3_buckets()
        self.assertEqual(result['test-bucket-1']['Status'], 'Active')
        self.assertEqual(result['test-bucket-2']['Status'], 'Inactive ❌')
        self.assertIn('Description', result['test-bucket-1'])
    
    @patch('wizards.s3_wizard.boto3.client')
    def test_empty_bucket_deletes_objects_and_versions(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        mock_s3.list_objects_v2.return_value = {
            'Contents': [{'Key': 'test.txt'}]
        }
        mock_s3.list_object_versions.return_value = {
            'Versions': [{'Key': 'test.txt', 'VersionId': '1'}]
        }

        result = s3_wizard.empty_bucket('my-bucket')

        mock_s3.delete_objects.assert_any_call(
            Bucket='my-bucket',
            Delete={'Objects': [{'Key': 'test.txt'}]}
        )
        mock_s3.delete_objects.assert_any_call(
            Bucket='my-bucket',
            Delete={'Objects': [{'Key': 'test.txt', 'VersionId': '1'}]}
        )
        self.assertTrue(result)

    @patch('wizards.s3_wizard.boto3.client')
    @patch('wizards.s3_wizard.input')
    @patch('wizards.s3_wizard.log_action')
    @patch('wizards.s3_wizard.config')
    def test_delete_selected_buckets_real_deletion(self, mock_config, mock_log_action, mock_input, mock_boto_client):
        mock_config.delete_for_real = True
        mock_input.side_effect = ['1', 'yes']

        s3_wizard.list_s3_buckets = MagicMock(return_value={
            'bucket-one': {'Status': 'Inactive ❌', 'Description': 'Test Bucket', 'CreationDate': '2023-01-01'}
        })
        s3_wizard.empty_bucket = MagicMock(return_value=True)

        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        s3_wizard.delete_selected_buckets()

        mock_s3.delete_bucket.assert_called_once_with(Bucket='bucket-one')
        mock_log_action.assert_called_with('bucket-one', 'S3', True)

    @patch('wizards.s3_wizard.boto3.client')
    @patch('wizards.s3_wizard.input')
    @patch('wizards.s3_wizard.log_action')
    @patch('wizards.s3_wizard.config')
    def test_delete_selected_buckets_simulation(self, mock_config, mock_log_action, mock_input, mock_boto_client):
        mock_config.delete_for_real = False
        mock_input.side_effect = ['1', 'yes']

        s3_wizard.list_s3_buckets = MagicMock(return_value={
            'bucket-one': {'Status': 'Inactive ❌', 'Description': 'Test Bucket', 'CreationDate': '2023-01-01'}
        })

        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        s3_wizard.delete_selected_buckets()

        mock_s3.delete_bucket.assert_not_called()
        mock_log_action.assert_called_once_with("S3", 'bucket-one', True, mode="deletion")

if __name__ == '__main__':
    unittest.main()
