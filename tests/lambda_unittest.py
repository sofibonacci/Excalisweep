import unittest
from unittest.mock import patch, MagicMock, call
from test_fixtures import BaseTestCase
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from wizards import lambda_wizard

class TestLambdaWizard(BaseTestCase):
    patch_path = 'wizards.lambda_wizard.boto3.client'  # patch boto3.client heredado

    def test_list_lambda_functions_success(self):
        self.boto3_client.list_functions.return_value = {
            'Functions': [
                {'FunctionName': 'func1', 'LastModified': '2025-05-20T10:00:00'}
            ]
        }
        self.boto3_client.list_aliases.return_value = {'Aliases': [{'AliasName': 'alias1'}]}
        self.boto3_client.list_versions_by_function.return_value = {'Versions': [{'Version': '1'}, {'Version': '$LATEST'}]}

        with patch('wizards.lambda_wizard.log_action') as mock_log_action:
            result = lambda_wizard.list_lambda_functions()

        self.assertIn('func1', result)
        self.assertEqual(result['func1']['Created'], '2025-05-20T10:00:00')
        self.assertEqual(result['func1']['Aliases'], ['alias1'])
        self.assertEqual(result['func1']['Versions'], ['1', '$LATEST'])
        mock_log_action.assert_not_called()

    def test_list_lambda_functions_with_exception(self):
        self.boto3_client.list_functions.return_value = {
            'Functions': [{'FunctionName': 'func2', 'LastModified': '2025-05-20T10:00:00'}]
        }
        self.boto3_client.list_aliases.side_effect = Exception("API error")

        with patch('wizards.lambda_wizard.log_action') as mock_log_action:
            result = lambda_wizard.list_lambda_functions()

        self.assertEqual(result, {})
        mock_log_action.assert_called_once_with("Lambda", 'func2', False, mode="deletion")

    def test_delete_lambda_function_success(self):
        self.boto3_client.list_aliases.return_value = {'Aliases': [{'AliasName': 'alias1'}]}
        self.boto3_client.list_versions_by_function.return_value = {'Versions': [{'Version': '1'}, {'Version': '$LATEST'}]}

        with patch('wizards.lambda_wizard.log_action') as mock_log_action:
            result = lambda_wizard.delete_lambda_function('func1', self.boto3_client)

        self.boto3_client.delete_alias.assert_called_once_with(FunctionName='func1', Name='alias1')
        self.boto3_client.delete_function.assert_has_calls([
            call(FunctionName='func1', Qualifier='1'),
            call(FunctionName='func1')
        ], any_order=True)

        self.assertTrue(result)
        mock_log_action.assert_not_called()

    def test_delete_lambda_function_failure(self):
        self.boto3_client.list_aliases.return_value = {'Aliases': []}
        self.boto3_client.list_versions_by_function.return_value = {'Versions': []}
        self.boto3_client.delete_function.side_effect = Exception("Delete error")

        with patch('wizards.lambda_wizard.log_action') as mock_log_action:
            result = lambda_wizard.delete_lambda_function('func_fail', self.boto3_client)

        self.assertFalse(result)
        mock_log_action.assert_called_once_with("Lambda", 'func_fail', False, mode="deletion")

    def test_delete_selected_lambda_functions_exit_immediately(self):
        with patch('wizards.lambda_wizard.input') as mock_input, \
             patch('wizards.lambda_wizard.config') as mock_config, \
             patch('wizards.lambda_wizard.log_action') as mock_log_action:

            mock_input.side_effect = ['exit']
            mock_config.delete_for_real = True
            self.boto3_client.list_functions.return_value = {'Functions': [{'FunctionName': 'func1', 'LastModified': 'now'}]}

            lambda_wizard.delete_selected_lambda_functions()

            mock_input.assert_called()
            mock_log_action.assert_not_called()

    def test_delete_selected_lambda_functions_all_yes(self):
        with patch('wizards.lambda_wizard.input') as mock_input, \
             patch('wizards.lambda_wizard.config') as mock_config, \
             patch('wizards.lambda_wizard.log_action') as mock_log_action:

            mock_input.side_effect = ['all', 'yes']
            mock_config.delete_for_real = True

            self.boto3_client.list_functions.return_value = {
                'Functions': [
                    {'FunctionName': 'func1', 'LastModified': '2025-05-20T10:00:00'},
                    {'FunctionName': 'func2', 'LastModified': '2025-05-20T11:00:00'},
                ]
            }
            self.boto3_client.list_aliases.return_value = {'Aliases': []}
            self.boto3_client.list_versions_by_function.return_value = {'Versions':[{'Version': '1'}, {'Version': '$LATEST'}]}
            self.boto3_client.delete_function.return_value = None

            lambda_wizard.delete_selected_lambda_functions()

            self.assertEqual(self.boto3_client.delete_function.call_count, 4)
            mock_log_action.assert_any_call("Lambda", 'func1', True, mode="deletion")
            mock_log_action.assert_any_call("Lambda", 'func2', True, mode="deletion")

    def test_delete_selected_lambda_functions_invalid_selection(self):
        with patch('wizards.lambda_wizard.input') as mock_input, \
             patch('wizards.lambda_wizard.config') as mock_config, \
             patch('wizards.lambda_wizard.log_action') as mock_log_action:

            mock_input.side_effect = ['5', 'exit']
            mock_config.delete_for_real = True
            self.boto3_client.list_functions.return_value = {
                'Functions': [{'FunctionName': 'func1', 'LastModified': 'now'}]
            }

            lambda_wizard.delete_selected_lambda_functions()

            mock_log_action.assert_not_called()

    def test_interactive_menu_exit(self):
        with patch('wizards.lambda_wizard.input') as mock_input, patch('builtins.print') as mock_print:

            mock_input.side_effect = ['3']
            lambda_wizard.interactive_menu()
            mock_print.assert_any_call("\n🔚 Exiting Excalisweep Lambda Wizard. Have a great day!")

if __name__ == '__main__':
    unittest.main()
