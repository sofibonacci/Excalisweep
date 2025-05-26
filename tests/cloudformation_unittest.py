import sys
import os
import unittest
from unittest.mock import patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tests.test_fixtures import BaseTestCase, create_mock_client
import wizards.cloud_formation_wizard as explorer
import config

class TestCloudFormationWizard(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.patch_path = 'wizards.cloud_formation_wizard.boto3.client'
        self.boto3_client = create_mock_client()

    def test_list_cloudformation_stacks_success(self):
        # Create mock stack using create_resource
        mock_stack = self.create_resource(
            resource_id='id1',
            status='CREATE_COMPLETE',
            name='stack1',
            resource_type='cloudformation_stack',
            extra_fields={'Description': 'Test stack description'}
        )

        # Configure mock client responses
        self.boto3_client.list_stacks.return_value = {
            'StackSummaries': [
                {
                    'StackName': mock_stack['Name'],
                    'StackStatus': mock_stack['Status'],
                    'StackId': mock_stack['ResourceId']
                }
            ]
        }
        self.boto3_client.describe_stacks.return_value = {
            'Stacks': [{'Description': mock_stack['Description']}]
        }

        stacks = explorer.list_cloudformation_stacks()
        self.assertIn('stack1', stacks)
        self.assertEqual(stacks['stack1']['Description'], 'Test stack description')

    def test_list_cloudformation_stacks_client_error(self):
        self.boto3_client.list_stacks.side_effect = Exception("AWS error")
        stacks = explorer.list_cloudformation_stacks()
        self.assertEqual(stacks, {})

    def test_delete_selected_stacks_success(self):
        with patch('wizards.cloud_formation_wizard.select_from_list') as mock_select, \
             patch('wizards.cloud_formation_wizard.input') as mock_input, \
             patch('wizards.cloud_formation_wizard.log_action') as mock_log, \
             patch('wizards.cloud_formation_wizard.delete_for_real', True):
            # Mock stack list
            mock_stack = self.create_resource(
                resource_id='id1',
                status='CREATE_COMPLETE',
                name='stack1',
                resource_type='cloudformation_stack'
            )
            self.boto3_client.list_stacks.return_value = {
                'StackSummaries': [{
                    'StackName': mock_stack['Name'],
                    'StackStatus': mock_stack['Status'],
                    'StackId': mock_stack['ResourceId']
                }]
            }
            self.boto3_client.describe_stacks.return_value = {
                'Stacks': [{'Description': 'Test stack'}]
            }
            
            # Mock user input
            mock_select.return_value = ['stack1']
            mock_input.return_value = 'yes'
            
            # Mock waiter
            self.boto3_client.get_waiter.return_value.wait.return_value = None
            
            explorer.delete_selected_stacks()
            
            self.boto3_client.delete_stack.assert_called_with(StackName='stack1')
            mock_log.assert_called_with("Cloud Formation", 'stack1', True, mode="deletion")

    def test_delete_selected_stacks_dry_run(self):
        with patch('wizards.cloud_formation_wizard.select_from_list') as mock_select, \
             patch('wizards.cloud_formation_wizard.input') as mock_input, \
             patch('wizards.cloud_formation_wizard.log_action') as mock_log, \
             patch('wizards.cloud_formation_wizard.delete_for_real', False):
            # Mock stack list
            mock_stack = self.create_resource(
                resource_id='id1',
                status='CREATE_COMPLETE',
                name='stack1',
                resource_type='cloudformation_stack'
            )
            self.boto3_client.list_stacks.return_value = {
                'StackSummaries': [{
                    'StackName': mock_stack['Name'],
                    'StackStatus': mock_stack['Status'],
                    'StackId': mock_stack['ResourceId']
                }]
            }
            self.boto3_client.describe_stacks.return_value = {
                'Stacks': [{'Description': 'Test stack'}]
            }
            
            # Mock user input
            mock_select.return_value = ['stack1']
            mock_input.return_value = 'yes'
            
            explorer.delete_selected_stacks()
            
            self.boto3_client.delete_stack.assert_not_called()
            mock_log.assert_called_with("Cloud Formation", 'stack1', True, mode="deletion")

    def test_delete_selected_stacks_error(self):
        with patch('wizards.cloud_formation_wizard.select_from_list') as mock_select, \
             patch('wizards.cloud_formation_wizard.input') as mock_input, \
             patch('wizards.cloud_formation_wizard.log_action') as mock_log, \
             patch('wizards.cloud_formation_wizard.delete_for_real', True):
            # Mock stack list
            mock_stack = self.create_resource(
                resource_id='id1',
                status='CREATE_COMPLETE',
                name='stack1',
                resource_type='cloudformation_stack'
            )
            self.boto3_client.list_stacks.return_value = {
                'StackSummaries': [{
                    'StackName': mock_stack['Name'],
                    'StackStatus': mock_stack['Status'],
                    'StackId': mock_stack['ResourceId']
                }]
            }
            self.boto3_client.describe_stacks.return_value = {
                'Stacks': [{'Description': 'Test stack'}]
            }
            
            # Mock user input
            mock_select.return_value = ['stack1']
            mock_input.return_value = 'yes'
            
            # Mock deletion error
            self.boto3_client.delete_stack.side_effect = Exception("Deletion error")
            
            explorer.delete_selected_stacks()
            
            mock_log.assert_called_with("Cloud Formation", 'stack1', False, mode="deletion")

    def test_delete_selected_stacks_empty_selection(self):
        with patch('wizards.cloud_formation_wizard.select_from_list') as mock_select:
            # Mock empty stack list
            self.boto3_client.list_stacks.return_value = {'StackSummaries': []}
            mock_select.return_value = []
            
            explorer.delete_selected_stacks()
            
            self.boto3_client.delete_stack.assert_not_called()

    def test_delete_selected_stacks_cancelled(self):
        with patch('wizards.cloud_formation_wizard.select_from_list') as mock_select, \
             patch('wizards.cloud_formation_wizard.input') as mock_input:
            # Mock stack list
            mock_stack = self.create_resource(
                resource_id='id1',
                status='CREATE_COMPLETE',
                name='stack1',
                resource_type='cloudformation_stack'
            )
            self.boto3_client.list_stacks.return_value = {
                'StackSummaries': [{
                    'StackName': mock_stack['Name'],
                    'StackStatus': mock_stack['Status'],
                    'StackId': mock_stack['ResourceId']
                }]
            }
            self.boto3_client.describe_stacks.return_value = {
                'Stacks': [{'Description': 'Test stack'}]
            }
            
            # Mock user cancellation
            mock_select.return_value = ['stack1']
            mock_input.return_value = 'no'
            
            explorer.delete_selected_stacks()
            
            self.boto3_client.delete_stack.assert_not_called()

if __name__ == '__main__':
    unittest.main()
