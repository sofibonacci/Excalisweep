from tests.test_fixtures import BaseTestCase
from unittest.mock import MagicMock, patch
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from wizards import ec2_wizard 

class TestEC2Wizard(BaseTestCase):
    patch_path = 'wizards.ec2_wizard.boto3.client'
    def test_list_ec2_instances_filters_terminated(self):
        # Creates mock instance using function from parent class 
        running_instance = self.create_resource(
            resource_id='i-123',
            status='running',
            name='TestInstance',
            resource_type='ec2',
            extra_fields={
                'InstanceId': 'i-123',
                'LaunchTime': '2022-01-01T00:00:00Z',
                'State': {'Name': 'running'},
                'InstanceType': 't2.micro',
                'Tags': [{'Key': 'Name', 'Value': 'TestInstance'}]
            }
        )
        terminated_instance = self.create_resource(
            resource_id='i-456',
            status='terminated',
            name='TerminatedInstance',
            resource_type='ec2',
            extra_fields={
                'InstanceId': 'i-456',
                'LaunchTime': '2022-01-01T00:00:00Z',
                'State': {'Name': 'terminated'},
                'InstanceType': 't2.micro',
                'Tags': [{'Key': 'Name', 'Value': 'TerminatedInstance'}]
            }
        )

        # Boto3 client mock already exists in self.boto3_client (patch created in BaseTestCase)
        self.boto3_client.describe_instances.return_value = {
            'Reservations': [{'Instances': [running_instance, terminated_instance]}]
        }

        result = ec2_wizard.list_ec2_instances()

        self.assertIsInstance(result, dict)
        self.assertIn('i-123', result)
        self.assertNotIn('i-456', result)
        self.assertEqual(result['i-123']['Status'], 'running')
        self.assertEqual(result['i-123']['Description'], 'TestInstance')
"""
    def test_terminate_real(self):

        with patch('wizards.ec2_wizard.input') as mock_input, \
             patch('wizards.ec2_wizard.log_action') as mock_log_action, \
             patch('wizards.ec2_wizard.config') as mock_config:

            mock_config.delete_for_real = True
            ec2_wizard.list_ec2_instances = MagicMock(return_value={
                'i-abc123': {'Status': 'running', 'Description': 'Test instance'}
            })

            mock_input.side_effect = ['1', 'yes']

            ec2_wizard.terminate_selected_instances()

            self.mock_boto_client.assert_called_once_with('ec2')
            self.boto3_client.terminate_instances.assert_called_once_with(InstanceIds=['i-abc123'])
            mock_log_action.assert_called_once_with("EC2", 'i-abc123', True, mode="deletion")

            self.assertTrue(self.boto3_client.terminate_instances.called)
            self.assertEqual(self.boto3_client.terminate_instances.call_count, 1)

    def test_terminate_simulated(self):
        from unittest.mock import patch

        with patch('wizards.ec2_wizard.input') as mock_input, \
             patch('wizards.ec2_wizard.log_action') as mock_log_action, \
             patch('wizards.ec2_wizard.config') as mock_config:

            mock_config.delete_for_real = False
            ec2_wizard.list_ec2_instances = MagicMock(return_value={
                'i-abc123': {'Status': 'running', 'Description': 'Simulated'}
            })

            mock_input.side_effect = ['1', 'yes']

            ec2_wizard.terminate_selected_instances()

            self.boto3_client.terminate_instances.assert_not_called()
            mock_log_action.assert_called_once_with("EC2", 'i-abc123', True, mode="deletion")

            self.assertFalse(self.boto3_client.terminate_instances.called)
            self.assertEqual(mock_log_action.call_count, 1)
"""
if __name__ == '__main__':
    import unittest
    unittest.main()
