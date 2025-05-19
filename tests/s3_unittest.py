import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from wizards import s3_wizard

class TestS3Wizard(unittest.TestCase):

    @patch('wizards.s3_wizard.boto3.client')
    def test_list_s3_buckets_with_active_and_inactive(self, mock_boto_client):
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client

        mock_s3_client.list_buckets.return_value = {
            'Buckets': [
                {'Name': 'active-bucket', 'CreationDate': '2022-01-01T00:00:00Z'},
                {'Name': 'empty-bucket', 'CreationDate': '2022-01-01T00:00:00Z'}
            ]
        }

        def get_bucket_tagging_side_effect(Bucket):
            return {
                'TagSet': [{'Key': 'Description', 'Value': f'{Bucket} description'}]
            }

        def list_objects_v2_side_effect(Bucket):
            if Bucket == 'active-bucket':
                return {'Contents': [{'Key': 'file.txt'}]}
            else:
                return {}

        mock_s3_client.get_bucket_tagging.side_effect = get_bucket_tagging_side_effect
        mock_s3_client.list_objects_v2.side_effect = list_objects_v2_side_effect

        result = s3_wizard.list_s3_buckets()

        self.assertIn('active-bucket', result)
        self.assertIn('empty-bucket', result)
        self.assertEqual(result['active-bucket']['Status'], 'Active')
        self.assertEqual(result['empty-bucket']['Status'], 'Inactive')

    @patch('wizards.s3_wizard.boto3.client')
    @patch('wizards.s3_wizard.input')
    @patch('wizards.s3_wizard.log_action')
    @patch('wizards.s3_wizard.config')
    def test_delete_real(self, mock_config, mock_log_action, mock_input, mock_boto_client):
        mock_config.delete_for_real = True
        mock_input.side_effect = ['1', 'yes']

        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client

        s3_wizard.list_s3_buckets = MagicMock(return_value={
            'test-bucket': {'Status': 'Inactive', 'Description': 'To delete', 'CreationDate': '2022-01-01T00:00:00Z'}
        })

        mock_s3_client.list_objects_v2.return_value = {}
        mock_s3_client.list_object_versions.return_value = {}

        s3_wizard.delete_selected_buckets()

        mock_s3_client.delete_bucket.assert_called_once_with(Bucket='test-bucket')
        mock_log_action.assert_called_with('test-bucket', 'S3', True)

    @patch('wizards.s3_wizard.boto3.client')
    @patch('wizards.s3_wizard.input')
    @patch('wizards.s3_wizard.log_action')
    @patch('wizards.s3_wizard.config')
    def test_delete_simulated(self, mock_config, mock_log_action, mock_input, mock_boto_client):
        mock_config.delete_for_real = False
        mock_input.side_effect = ['1', 'yes']

        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client

        s3_wizard.list_s3_buckets = MagicMock(return_value={
            'simulated-bucket': {'Status': 'Inactive', 'Description': 'Simulated', 'CreationDate': '2022-01-01T00:00:00Z'}
        })

        s3_wizard.delete_selected_buckets()

        mock_s3_client.delete_bucket.assert_not_called()
        mock_log_action.assert_called_once_with('S3', 'simulated-bucket', True, mode='deletion')

if __name__ == '__main__':
    unittest.main()
