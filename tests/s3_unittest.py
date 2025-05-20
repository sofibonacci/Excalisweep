# test_s3_wizard.py

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from s3_wizard import list_s3_buckets, empty_bucket
from test_fixtures import BaseTestCase

class TestS3Wizard(BaseTestCase):
    def setUp(self):
        super().setUp()

    @patch("s3_wizard.boto3.client")
    def test_list_s3_buckets(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        mock_s3.list_buckets.return_value = {
            'Buckets': [
                {'Name': 'test-bucket-1', 'CreationDate': datetime(2024, 1, 1)},
                {'Name': 'test-bucket-2', 'CreationDate': datetime(2024, 2, 2)}
            ]
        }

        mock_s3.get_bucket_tagging.side_effect = [
            {'TagSet': [{'Key': 'Description', 'Value': 'Test bucket 1'}]},
            Exception("Access Denied")
        ]

        mock_s3.list_objects_v2.side_effect = [
            {'Contents': [{'Key': 'file.txt'}]},  # has objects
            {}  # no objects
        ]

        buckets = list_s3_buckets()
        self.assertEqual(len(buckets), 2)

        self.assertEqual(buckets['test-bucket-1']['Description'], 'Test bucket 1')
        self.assertEqual(buckets['test-bucket-1']['Status'], 'Active')

        self.assertTrue("Error retrieving description" in buckets['test-bucket-2']['Description'])
        self.assertEqual(buckets['test-bucket-2']['Status'], 'Inactive ❌')

    @patch("s3_wizard.boto3.client")
    def test_empty_bucket_with_versions(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        mock_s3.list_objects_v2.return_value = {
            'Contents': [{'Key': 'file1.txt'}, {'Key': 'file2.txt'}]
        }

        mock_s3.list_object_versions.return_value = {
            'Versions': [
                {'Key': 'file1.txt', 'VersionId': 'v1'},
                {'Key': 'file2.txt', 'VersionId': 'v2'}
            ]
        }

        success = empty_bucket("test-bucket")
        self.assertTrue(success)
        mock_s3.delete_objects.assert_called()

    @patch("s3_wizard.boto3.client")
    def test_empty_bucket_with_exception(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        mock_s3.list_objects_v2.side_effect = Exception("Something went wrong")

        with patch("s3_wizard.log_action") as mock_log:
            success = empty_bucket("error-bucket")
            self.assertFalse(success)
            mock_log.assert_called_once_with("S3", "error-bucket", False, mode="deletion")


if __name__ == '__main__':
    unittest.main()
