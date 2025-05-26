import unittest
from unittest.mock import patch, MagicMock
import botocore
import json
import boto3
import sys, os
import inspect

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import wizards.other_services_wizard as explorer

class TestAWSServiceExplorer(unittest.TestCase):
    
    # Test for list_services
    @patch('boto3.Session')
    def test_list_services_success(self, mock_session):
        mock_instance = MagicMock()
        mock_instance.get_available_services.return_value = ['s3', 'ec2', 'lambda']
        mock_session.return_value = mock_instance
        result = explorer.list_services()
        self.assertEqual(result, ['ec2', 'lambda', 's3'])

    
    # Test for list_services 
    @patch('boto3.Session')
    def test_list_services_boto_error(self, mock_session):
        mock_session.side_effect = botocore.exceptions.BotoCoreError()
        result = explorer.list_services()
        self.assertEqual(result, [])

    @patch('boto3.Session')
    def test_list_services_generic_error(self, mock_session):
        mock_session.side_effect = Exception("Unexpected error")
        result = explorer.list_services()
        self.assertEqual(result, [])

    # Test for list_all_methods
    @patch('boto3.client')
    def test_list_all_methods_success(self, mock_client):
        client_mock = MagicMock()
        setattr(client_mock, 'delete_bucket', MagicMock())
        setattr(client_mock, 'list_objects', MagicMock())
        setattr(client_mock, 'create_bucket', MagicMock())
        setattr(client_mock, 'terminate_instance', MagicMock())

        mock_client.return_value = client_mock
        result = explorer.list_all_methods('s3')
        self.assertIn('delete_bucket', result)
        self.assertIn('list_objects', result)
        self.assertIn('terminate_instance', result)
        self.assertNotIn('create_bucket', result) 

    @patch('boto3.client')
    def test_list_all_methods_boto_error(self, mock_client):
        mock_client.side_effect = botocore.exceptions.BotoCoreError()

        result = explorer.list_all_methods('s3')
        self.assertEqual(result, [])

    @patch('boto3.client')
    def test_list_all_methods_generic_error(self, mock_client):
        mock_client.side_effect = Exception("Unexpected")

        result = explorer.list_all_methods('s3')
        self.assertEqual(result, [])

    # Test for choose_method
    @patch('wizards.other_services_wizard.execute_method')
    @patch('wizards.other_services_wizard.select_from_list')
    @patch('builtins.input', return_value='s3')
    @patch('wizards.other_services_wizard.list_all_methods')
    @patch('wizards.other_services_wizard.list_services')
    def test_choose_method_valid(self, mock_list_services, mock_list_methods, mock_input, mock_select, mock_execute):
        mock_list_services.return_value = ['s3', 'ec2']
        mock_list_methods.return_value = ['list_buckets', 'delete_bucket']
        mock_select.return_value = ['list_buckets']
        explorer.choose_method()
        mock_execute.assert_called_once_with('s3', 'list_buckets')

    @patch('builtins.print')
    @patch('builtins.input', return_value='invalid_service')
    @patch('wizards.other_services_wizard.list_services')
    def test_choose_method_invalid_service(self, mock_list_services, mock_input, mock_print):
        mock_list_services.return_value = ['s3', 'ec2']
        explorer.choose_method()
        mock_print.assert_any_call("\nInvalid service name")
        

    @patch('builtins.print')
    @patch('wizards.other_services_wizard.execute_method')
    @patch('wizards.other_services_wizard.select_from_list')
    @patch('builtins.input', return_value='s3')
    @patch('wizards.other_services_wizard.list_all_methods')
    @patch('wizards.other_services_wizard.list_services')
    def test_choose_method_no_method_selected(self, mock_list_services, mock_list_methods, mock_input, mock_select, mock_execute, mock_print):
        mock_list_services.return_value = ['s3']
        mock_list_methods.return_value = ['list_buckets', 'delete_bucket']
        mock_select.return_value = None  
        explorer.choose_method()
        mock_execute.assert_not_called()
        mock_print.assert_any_call("\n🚫 No valid method was selected.")


    # Test for execute_method
    @patch('builtins.input', side_effect=['"my-bucket"'])
    @patch('boto3.client')
    def test_execute_method_with_required_params(self, mock_boto_client, mock_input):
        mock_method = MagicMock(return_value={"ResponseMetadata": {"HTTPStatusCode": 200}})
        mock_method.__doc__ = ":param Bucket: **[REQUIRED]**"

        client_mock = MagicMock()
        client_mock.list_objects = mock_method
        mock_boto_client.return_value = client_mock

        with patch('wizards.other_services_wizard.getattr', return_value=mock_method):
            explorer.execute_method('s3', 'list_objects')
            mock_method.assert_called_once_with(Bucket="my-bucket")



    @patch('builtins.input', side_effect=[''])
    @patch('boto3.client')
    def test_execute_method_missing_required_param(self, mock_boto_client, mock_input):
        mock_method = MagicMock()
        mock_method.__doc__ = ":param Bucket: **[REQUIRED]**"
        client_mock = MagicMock()
        client_mock.some_method = mock_method
        mock_boto_client.return_value = client_mock

        with patch('wizards.other_services_wizard.getattr', return_value=mock_method):
            explorer.execute_method('s3', 'some_method')
            mock_method.assert_not_called()

    @patch('builtins.input', side_effect=['"my-bucket"'])
    @patch('boto3.client')
    def test_execute_method_raises_exception(self, mock_boto_client, mock_input):
        mock_method = MagicMock()
        mock_method.__doc__ = ":param Bucket: **[REQUIRED]**"
        mock_method.side_effect = Exception("Boom!")
        client_mock = MagicMock()
        client_mock.some_method = mock_method
        mock_boto_client.return_value = client_mock

        with patch('wizards.other_services_wizard.getattr', return_value=mock_method):
            explorer.execute_method('s3', 'some_method')
            mock_method.assert_called_once()

"""
    @patch('builtins.input', side_effect=['"my-bucket"'])
    @patch('wizards.other_services_wizard.config')
    @patch('wizards.other_services_wizard.log_action')
    @patch('boto3.client')
    def test_execute_delete_method_fake(self, mock_boto_client, mock_log_action, mock_config, mock_input):
        mock_config.delete_for_real = False
        
        mock_method = MagicMock()
        mock_method.__doc__ = ":param Bucket: **[REQUIRED]**"
        
        client_mock = MagicMock()
        client_mock.delete_bucket = mock_method
        mock_boto_client.return_value = client_mock

        with patch('wizards.other_services_wizard.getattr', return_value=mock_method):
            explorer.execute_method('s3', 'delete_bucket')
            
            mock_method.assert_not_called()
            mock_log_action.assert_called_once()



    @patch('builtins.input', side_effect=['"my-bucket"'])
    @patch('wizards.other_services_wizard.config')
    @patch('wizards.other_services_wizard.log_action')
    @patch('boto3.client')
    def test_execute_delete_method_real(self, mock_boto_client, mock_log_action, mock_config, mock_input):
        mock_config.delete_for_real = True

        mock_method = MagicMock(return_value={"ResponseMetadata": {"HTTPStatusCode": 200}})
        mock_method.__doc__ = ":param Bucket: **[REQUIRED]**"

        client_mock = MagicMock()
        client_mock.delete_bucket = mock_method
        mock_boto_client.return_value = client_mock

        with patch('wizards.other_services_wizard.getattr', return_value=mock_method):
            explorer.execute_method('s3', 'delete_bucket')

            mock_method.assert_called_once_with(Bucket="my-bucket")
            mock_log_action.assert_called_once()
""" 

if __name__ == '__main__':
    unittest.main()
