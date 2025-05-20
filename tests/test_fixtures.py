# test_fixtures.py
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

def create_mock_client():
    return MagicMock()

def create_mock_resource(
    resource_id='resource-123',
    status='active',
    name='MockedResource',
    resource_type='generic',
    created_at=None,
    extra_fields=None
):
    """
    Creates a mock instance for any AWS service (EC2, S3, Lambda... )

    - resource_id: (example: 'i-123', 'bucket-abc')
    - status:  (example: 'running', 'deleted')
    - name: name or identifier
    - resource_type: logic type of resource (just for reference)
    - created_at: optional date
    - extra_fields: optional dict with additional keys
    """

    resource = {
        'ResourceId': resource_id,
        'Status': status,
        'Name': name,
        'Type': resource_type,
        'CreatedAt': created_at or datetime.utcnow().isoformat()
    }

    if extra_fields:
        resource.update(extra_fields)

    return resource

class BaseTestCase(unittest.TestCase):
    patch_path='boto3.client'
    def setUp(self):
        patcher= patch(self.patch_path)
        self.mock_boto_client = patcher.start()

        self.boto3_client = create_mock_client()
        self.mock_boto_client.return_value = self.boto3_client

    def create_resource(self, **kwargs):
        return create_mock_resource(**kwargs)
