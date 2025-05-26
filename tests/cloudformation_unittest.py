# tests/cloudformation_unittest.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tests.test_fixtures import BaseTestCase
import wizards.cloud_formation_wizard as explorer
import config

class TestCloudFormationWizard(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.patch_path = 'wizards.cloud_formation_wizard.boto3.client'

    def test_list_cloudformation_stacks_success(self):
        # Create mock stack using create_mock_resource
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

    @patch('wizards.cloud_formation_wizard.list_cloudformation_stacks')
    @patch('wizards.cloud_formation_wizard.select_from_list')
    """
    def test_delete_selected_stacks_no_stacks(self, mock_select, mock_list):
        mock_list.return_value = {}
        result = explorer.delete_selected_stacks()
        mock_select.assert_not_called()

    @patch('wizards.cloud_formation_wizard.list_cloudformation_stacks')
    @patch('wizards.cloud_formation_wizard.select_from_list')
    def test_delete_selected_stacks_no_valid_selection(self, mock_select, mock_list):
        mock_list.return_value = {
            'stack1': self.create_resource(name='stack1'),
            'stack2': self.create_resource(name='stack2')
        }
        mock_select.return_value = []
        result = explorer.delete_selected_stacks()
        self.assertIsNone(result)

    @patch('wizards.cloud_formation_wizard.log_action')
    @patch('wizards.cloud_formation_wizard.list_cloudformation_stacks')
    @patch('wizards.cloud_formation_wizard.select_from_list')
    @patch('builtins.input')
    def test_delete_selected_stacks_confirmation_no(self, mock_input, mock_select, mock_list, mock_log):
        mock_list.return_value = {
            'stack1': self.create_resource(name='stack1'),
            'stack2': self.create_resource(name='stack2')
        }
        mock_select.return_value = ['stack1']
        mock_input.return_value = 'no'

        explorer.delete_selected_stacks()
        mock_log.assert_not_called()

    @patch('wizards.cloud_formation_wizard.log_action')
    @patch('wizards.cloud_formation_wizard.list_cloudformation_stacks')
    @patch('wizards.cloud_formation_wizard.select_from_list')
    @patch('builtins.input')
    def test_delete_selected_stacks_for_real_success(self, mock_input, mock_select, mock_list, mock_log):
        mock_list.return_value = {
            'stack1': self.create_resource(name='stack1'),
            'stack2': self.create_resource(name='stack2')
        }
        mock_select.return_value = ['stack1']
        mock_input.return_value = 'yes'
        config.delete_for_real = True

        mock_waiter = MagicMock()
        self.boto3_client.get_waiter.return_value = mock_waiter

        explorer.delete_selected_stacks()

        self.boto3_client.delete_stack.assert_called_once_with(StackName='stack1')
        mock_waiter.wait.assert_called_once_with(StackName='stack1')
        mock_log.assert_called_once_with("Cloud Formation", 'stack1', True, mode="deletion")
        """
if __name__ == '__main__':
    unittest.main()
