import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from wizards import ec2_wizard  

class TestEC2Wizard(unittest.TestCase):

    @patch('ec2_wizard.boto3.client')
    def test_list_ec2_instances_filters_terminated(self, mock_boto_client):
        mock_ec2_client = MagicMock()
        mock_boto_client.return_value = mock_ec2_client

        mock_ec2_client.describe_instances.return_value = {
            'Reservations': [
                {'Instances': [
                    {
                        'InstanceId': 'i-123',
                        'LaunchTime': '2022-01-01T00:00:00Z',
                        'State': {'Name': 'running'},
                        'InstanceType': 't2.micro',
                        'Tags': [{'Key': 'Name', 'Value': 'TestInstance'}]
                    },
                    {
                        'InstanceId': 'i-456',
                        'LaunchTime': '2022-01-01T00:00:00Z',
                        'State': {'Name': 'terminated'},
                        'InstanceType': 't2.micro',
                        'Tags': [{'Key': 'Name', 'Value': 'TerminatedInstance'}]
                    }
                ]}
            ]
        }

        result = ec2_wizard.list_ec2_instances()

        self.assertIsInstance(result, dict)
        self.assertIn('i-123', result)
        self.assertNotIn('i-456', result)
        self.assertEqual(result['i-123']['Status'], 'running')
        self.assertEqual(result['i-123']['Description'], 'TestInstance')

    @patch('ec2_wizard.boto3.client')
    @patch('ec2_wizard.input')
    @patch('ec2_wizard.log_action')
    @patch('ec2_wizard.config')
    def test_terminate_real(self, mock_config, mock_log_action, mock_input, mock_boto_client):
        mock_config.delete_for_real = True
        ec2_wizard.list_ec2_instances = MagicMock(return_value={
            'i-abc123': {'Status': 'running', 'Description': 'Test instance'}
        })

        mock_input.side_effect = ['1', 'yes']
        mock_ec2_client = MagicMock()
        mock_boto_client.return_value = mock_ec2_client

        ec2_wizard.terminate_selected_instances()

        mock_boto_client.assert_called_once_with('ec2')
        mock_ec2_client.terminate_instances.assert_called_once_with(InstanceIds=['i-abc123'])
        mock_log_action.assert_called_once_with("EC2", 'i-abc123', True, mode="deletion")

        self.assertTrue(mock_ec2_client.terminate_instances.called)
        self.assertEqual(mock_ec2_client.terminate_instances.call_count, 1)

    @patch('ec2_wizard.boto3.client')
    @patch('ec2_wizard.input')
    @patch('ec2_wizard.log_action')
    @patch('ec2_wizard.config')
    def test_terminate_simulated(self, mock_config, mock_log_action, mock_input, mock_boto_client):
        mock_config.delete_for_real = False
        ec2_wizard.list_ec2_instances = MagicMock(return_value={
            'i-abc123': {'Status': 'running', 'Description': 'Simulated'}
        })

        mock_input.side_effect = ['1', 'yes']
        mock_ec2_client = MagicMock()
        mock_boto_client.return_value = mock_ec2_client

        ec2_wizard.terminate_selected_instances()

        mock_ec2_client.terminate_instances.assert_not_called()
        mock_log_action.assert_called_once_with("EC2", 'i-abc123', True, mode="deletion")

        self.assertFalse(mock_ec2_client.terminate_instances.called)
        self.assertEqual(mock_log_action.call_count, 1)

if __name__ == '__main__':
    unittest.main()
