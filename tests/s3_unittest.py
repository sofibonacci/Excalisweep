import unittest
from unittest.mock import patch, MagicMock
from wizards import s3_wizard

class TestS3Wizard(unittest.TestCase):

    @patch('wizards.s3_wizard.config')
    @patch('wizards.s3_wizard.log_action')
    @patch('wizards.s3_wizard.input')
    @patch('wizards.s3_wizard.boto3.client')
    @patch('wizards.s3_wizard.list_s3_buckets')
    def test_delete_real(self, mock_list, mock_boto3, mock_input, mock_log, mock_config):
        mock_config.delete_for_real = True
        mock_input.return_value = '1'
        mock_list.return_value = {
            'test-bucket': {'Status': 'Inactive', 'Description': 'Test', 'CreationDate': '2022-01-01T00:00:00Z'}
        }

        mock_s3 = MagicMock()
        mock_boto3.return_value = mock_s3

        s3_wizard.run()

        mock_s3.delete_bucket.assert_called_with(Bucket='test-bucket')

    @patch('wizards.s3_wizard.config')
    @patch('wizards.s3_wizard.log_action')
    @patch('wizards.s3_wizard.input')
    @patch('wizards.s3_wizard.boto3.client')
    @patch('wizards.s3_wizard.list_s3_buckets')
    def test_delete_simulated(self, mock_list, mock_boto3, mock_input, mock_log, mock_config):
        mock_config.delete_for_real = False
        mock_input.return_value = '1'
        mock_list.return_value = {
            'simulated-bucket': {'Status': 'Inactive', 'Description': 'Simulated', 'CreationDate': '2022-01-01T00:00:00Z'}
        }

        s3_wizard.run()

        mock_log.assert_called_with("delete", "simulated-bucket")

    def test_list_s3_buckets_with_active_and_inactive(self):
        with patch('wizards.s3_wizard.boto3.client') as mock_boto3:
            mock_s3 = MagicMock()
            mock_boto3.return_value = mock_s3
            mock_s3.list_buckets.return_value = {
                'Buckets': [
                    {'Name': 'active-bucket', 'CreationDate': '2022-01-01T00:00:00Z'},
                    {'Name': 'empty-bucket', 'CreationDate': '2022-01-01T00:00:00Z'}
                ]
            }
            mock_s3.get_paginator.return_value.paginate.return_value = [
                {'Contents': [{'Key': 'something'}]},  # active-bucket has content
                {'Contents': []}                      # empty-bucket is empty
            ]

            result = s3_wizard.list_s3_buckets()
            self.assertIn('active-bucket', result)
            self.assertIn('empty-bucket', result)
            self.assertEqual(result['empty-bucket']['Status'], 'Inactive')
            self.assertEqual(result['active-bucket']['Status'], 'Active')

if __name__ == '__main__':
    unittest.main()
