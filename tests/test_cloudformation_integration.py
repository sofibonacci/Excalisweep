import unittest
from unittest.mock import patch, MagicMock
import botocore
import builtins
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import wizards.other_services_wizard as explorer

class TestOtherServicesWizard(unittest.TestCase):

    @patch('boto3.client')
    def test_list_cloudformation_stacks_success(self, mock_boto_client):
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        
        mock_client.list_stacks.return_value = {
            'StackSummaries': [
                {'StackName': 'stack1', 'StackStatus': 'CREATE_COMPLETE', 'StackId': 'id1'}
            ]
        }
        mock_client.describe_stacks.return_value = {
            'Stacks': [{'Description': 'Test stack description'}]
        }

        stacks = explorer.list_cloudformation_stacks()
        self.assertIn('stack1', stacks)
        self.assertEqual(stacks['stack1']['Description'], 'Test stack description')

    @patch('boto3.client')
    def test_list_cloudformation_stacks_client_error(self, mock_boto_client):
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        
        mock_client.list_stacks.side_effect = Exception("AWS error")

        stacks = explorer.list_cloudformation_stacks()
        self.assertEqual(stacks, {})

    @patch('boto3.client')
    @patch('builtins.input', side_effect=['all', 'yes'])
    def test_delete_selected_stacks(self, mock_input, mock_boto_client):
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        
        stacks = {
            'stack1': {'StackStatus': 'CREATE_COMPLETE', 'StackId': 'id1', 'Description': 'desc'}
        }

        with patch.object(explorer, 'list_cloudformation_stacks', return_value=stacks), \
             patch.object(explorer, 'select_from_list', return_value=['stack1']), \
             patch.object(explorer, 'config') as mock_config, \
             patch.object(explorer, 'log_action') as mock_log_action:
            
            mock_config.delete_for_real = False

            explorer.delete_selected_stacks()

            mock_log_action.assert_called_with("Cloud Formation", 'stack1', True, mode="deletion")

    @patch('boto3.client')
    @patch('builtins.input', side_effect=['all', 'yes'])
    def test_delete_selected_stacks_real_deletion(self, mock_input, mock_boto_client):
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        mock_waiter = MagicMock()
        mock_client.get_waiter.return_value = mock_waiter

        stacks = {
            'stack1': {'StackStatus': 'CREATE_COMPLETE', 'StackId': 'id1', 'Description': 'desc'}
        }

        with patch.object(explorer, 'list_cloudformation_stacks', return_value=stacks), \
             patch.object(explorer, 'select_from_list', return_value=['stack1']), \
             patch.object(explorer, 'config') as mock_config, \
             patch.object(explorer, 'log_action') as mock_log_action:
            
            mock_config.delete_for_real = True

            explorer.delete_selected_stacks()

            mock_client.delete_stack.assert_called_with(StackName='stack1')
            mock_waiter.wait.assert_called_with(StackName='stack1')
            mock_log_action.assert_called_with("Cloud Formation", 'stack1', True, mode="deletion")

    @patch('boto3.client')
    @patch('builtins.input', side_effect=['all', 'no'])
    def test_delete_selected_stacks_canceled(self, mock_input, mock_boto_client):
        stacks = {
            'stack1': {'StackStatus': 'CREATE_COMPLETE', 'StackId': 'id1', 'Description': 'desc'}
        }

        with patch.object(explorer, 'list_cloudformation_stacks', return_value=stacks), \
             patch.object(explorer, 'select_from_list', return_value=['stack1']):
            
            explorer.delete_selected_stacks()

if __name__ == '__main__':
    unittest.main()