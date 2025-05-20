import unittest
from unittest.mock import patch, MagicMock
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import wizards.cloud_formation_wizard as explorer
import config

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

    @patch('wizards.cloud_formation_wizard.list_cloudformation_stacks')
    @patch('wizards.cloud_formation_wizard.select_from_list')
    def test_delete_selected_stacks_no_stacks(self, mock_select, mock_list):
        mock_list.return_value = {}
        result = explorer.delete_selected_stacks()
        mock_select.assert_not_called()

    @patch('wizards.cloud_formation_wizard.list_cloudformation_stacks')
    @patch('wizards.cloud_formation_wizard.select_from_list')
    def test_delete_selected_stacks_no_valid_selection(self, mock_select, mock_list):
        mock_list.return_value = {'stack1': {}, 'stack2': {}}
        mock_select.return_value = []
        result = explorer.delete_selected_stacks()
        self.assertIsNone(result)

    @patch('wizards.cloud_formation_wizard.boto3.client')
    @patch('wizards.cloud_formation_wizard.log_action')
    @patch('wizards.cloud_formation_wizard.list_cloudformation_stacks')
    @patch('wizards.cloud_formation_wizard.select_from_list')
    @patch('builtins.input')
    def test_delete_selected_stacks_confirmation_no(self, mock_input, mock_select, mock_list, mock_log, mock_boto):
        mock_list.return_value = {'stack1': {}, 'stack2': {}}
        mock_select.return_value = ['stack1']
        mock_input.return_value = 'no'

        explorer.delete_selected_stacks()
        mock_log.assert_not_called()

    @patch('wizards.cloud_formation_wizard.boto3.client')
    @patch('wizards.cloud_formation_wizard.log_action')
    @patch('wizards.cloud_formation_wizard.list_cloudformation_stacks')
    @patch('wizards.cloud_formation_wizard.select_from_list')
    @patch('builtins.input')
    def test_delete_selected_stacks_for_real_success(self, mock_input, mock_select, mock_list, mock_log, mock_boto):
        mock_list.return_value = {'stack1': {}, 'stack2': {}}
        mock_select.return_value = ['stack1']
        mock_input.return_value = 'yes'
        config.delete_for_real = True

        mock_client = MagicMock()
        mock_boto.return_value = mock_client

        mock_waiter = MagicMock()
        mock_client.get_waiter.return_value = mock_waiter

        explorer.delete_selected_stacks()

        mock_client.delete_stack.assert_called_once_with(StackName='stack1')
        mock_waiter.wait.assert_called_once_with(StackName='stack1')
        mock_log.assert_called_once_with("Cloud Formation", 'stack1', True, mode="deletion")

if __name__ == '__main__':
    unittest.main()