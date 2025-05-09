import unittest
from unittest.mock import patch, MagicMock
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import wizards.other_services_wizard as explorer

class TestAWSServiceExplorer(unittest.TestCase):

    @patch('boto3.Session')
    def test_list_services(self, mock_session):
        mock_instance = MagicMock()
        mock_instance.get_available_services.return_value = ['s3', 'ec2', 'lambda']
        mock_session.return_value = mock_instance

        result = explorer.list_services()
        self.assertIn('s3', result)
        self.assertCountEqual(result, ['s3', 'ec2', 'lambda'])


    @patch('boto3.client')
    def test_list_all_methods(self, mock_client):
        mock_instance = MagicMock()
        
        mock_instance.some_method = MagicMock()
        mock_client.return_value = mock_instance

        methods = explorer.list_all_methods('s3')
        self.assertIsInstance(methods, list)



if __name__ == '__main__':
    unittest.main()