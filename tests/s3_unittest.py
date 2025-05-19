import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from wizards import s3_wizard  


class TestS3Wizard(unittest.TestCase):

    @patch('wizards.s3_wizard.boto3.client')
    def test_list_s3_buckets_filters_active_and_inactive(self, mock_boto_client):
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client

        # Mock list_buckets
        mock_s3_client.list_buckets.return_value = {
            'Buckets': [
                {'Name': 'active-bucket', 'CreationDate': datetime(2022, 1, 1)},
                {'Name': 'empty-bucket', 'CreationDate': datetime(2022, 1, 2)},
            ]
        }

        # Mock get_bucket_tagging
        def mock_get_bucket_tagging(Bucket):
            return {'TagSet': [{'Key': 'Description', 'Value': f'Description for {Bucket}'}]}

        # Mock list_objects_v2 for status detection
        def mock_list_objects_v2(Bucket):
            if Bucket == 'active-bucket':
                return {'Contents': [{'Key': 'somefile.txt'}]}  # <-- simulate a non-empty bucket
            return {}  # simulate empty bucket for others


        mock_s3_client.get_bucket_tagging.side_effect = mock_get_bucket_tagging
        mock_s3_client.list_objects_v2.side_effect = mock_list_objects_v2

        result = s3_wizard.list_s3_buckets()

        self.assertIsInstance(result, dict)
        self.assertEqual(result['active-bucket']['Status'], 'Active')
        self.assertEqual(result['empty-bucket']['Status'], 'Inactive ❌')
        self.assertEqual(result['active-bucket']['Description'], 'Description for active-bucket')


    @patch('wizards.s3_wizard.boto3.client')
    @patch('wizards.s3_wizard.input')
    @patch('wizards.s3_wizard.log_action')
    @patch('wizards.s3_wizard.config')
    def test_delete_real(self, mock_config, mock_log_action, mock_input, mock_boto_client):
        mock_config.delete_for_real = True
        s3_wizard.list_s3_buckets = MagicMock(return_value={
            'test-bucket': {'Status': 'Inactive ❌', 'Description': 'Desc', 'CreationDate': datetime(2022, 1, 1)}
        })

        mock_input.side_effect = ['1', 'yes']
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client

        mock_s3_client.list_objects_v2.return_value = {}
        mock_s3_client.list_object_versions.return_value = {}

        s3_wizard.delete_selected_buckets()

        mock_boto_client.assert_any_call('s3') 


    @patch('wizards.s3_wizard.boto3.client')
    @patch('wizards.s3_wizard.input')
    @patch('wizards.s3_wizard.log_action')
    @patch('wizards.s3_wizard.config')
    def test_delete_simulated(self, mock_config, mock_log_action, mock_input, mock_boto_client):
        mock_config.delete_for_real = False
        s3_wizard.list_s3_buckets = MagicMock(return_value={
            'test-bucket': {'Status': 'Inactive ❌', 'Description': 'Simulated', 'CreationDate': datetime(2022, 1, 1)}
        })

        mock_input.side_effect = ['1', 'yes']
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client

        s3_wizard.delete_selected_buckets()

        mock_s3_client.delete_bucket.assert_not_called()
        mock_log_action.assert_called_once_with('S3', 'test-bucket', True, mode='deletion')


if __name__ == '__main__':
    unittest.main()
