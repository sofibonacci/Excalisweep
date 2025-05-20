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
    
        mock_s3_client.list_buckets.return_value = {
            'Buckets': [
                {'Name': 'active-bucket', 'CreationDate': datetime(2022, 1, 1)},
                {'Name': 'empty-bucket', 'CreationDate': datetime(2022, 1, 2)},
            ]
        }
    
        def mock_get_bucket_tagging(Bucket):
            if Bucket == 'active-bucket':
                return {'TagSet': [{'Key': 'Description', 'Value': 'Active Bucket'}]}
            elif Bucket == 'empty-bucket':
                return {'TagSet': []}
        
        def mock_list_objects_v2(Bucket):
            return {'Contents': [{'Key': 'file.txt'}]} if Bucket == 'active-bucket' else {}
    
        mock_s3_client.get_bucket_tagging.side_effect = mock_get_bucket_tagging
        mock_s3_client.list_objects_v2.side_effect = mock_list_objects_v2
    
        result = s3_wizard.list_s3_buckets()
        self.assertIn('active-bucket', result)
        self.assertIn('empty-bucket', result)
        self.assertEqual(result['active-bucket']['Status'], 'Active')
        self.assertEqual(result['empty-bucket']['Status'], 'Inactive ❌')
    
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
    def test_delete_skips_active_buckets(self, mock_config, mock_log_action, mock_input, mock_boto_client):
        mock_config.delete_for_real = True
        s3_wizard.list_s3_buckets = MagicMock(return_value={
            'active-bucket': {'Status': 'Active', 'Description': 'Desc', 'CreationDate': datetime(2022, 1, 1)}
        })

        mock_input.side_effect = ['1', 'no', 'exit']
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client

        s3_wizard.delete_selected_buckets()

        # The delete_bucket method should not be called because it's an active bucket
        mock_s3_client.delete_bucket.assert_not_called()


if __name__ == '__main__':
    unittest.main()
