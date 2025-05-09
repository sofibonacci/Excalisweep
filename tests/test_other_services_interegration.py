import subprocess
import boto3
import re
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config

def test_aws_service_explorer_lists_services():
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "other_services_wizard.py"))
    result = subprocess.run(
        ["python", script_path],
        input="1\nexit\n".encode(),
        capture_output=True,
        timeout=30
    )
    output = result.stdout.decode()
    print("AWS Services Output:\n", output)

    known_services = ['s3', 'ec2', 'lambda']
    for service in known_services:
        assert service in output, f"Service '{service}' not found in output"

def test_aws_service_explorer_detects_deletion_method():
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "other_services_wizard.py"))
    bucket_name = "excali-test-bucket"
    input_sequence = f"2\ns3\n1\n{{\"Bucket\": \"{bucket_name}\"}}\nyes\nexit\n"
    result = subprocess.run(
        ["python", script_path],
        input=input_sequence.encode(),
        capture_output=True,
        timeout=60
    )
    output = result.stdout.decode()
    print("AWS Service Explorer Deletion Test Output:\n", output)

    if config.delete_for_real:
        assert "Successfully deleted" in output, "No deletion occurred even though delete_for_real is True"
    else:
        assert "Logged delete attempt" in output, "Deletion attempt was not logged when delete_for_real is False"

def test_aws_service_explorer_no_delete_action_when_config_is_false():
    config.delete_for_real = False 
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "other_services_wizard.py"))
    bucket_name = "excali-test-bucket"
    input_sequence = f"2\ns3\n1\n{{\"Bucket\": \"{bucket_name}\"}}\nyes\nexit\n"

    result = subprocess.run(
        ["python", script_path],
        input=input_sequence.encode(),
        capture_output=True,
        timeout=60
    )
    output = result.stdout.decode()
    print("AWS Service Explorer No Delete Action Output:\n", output)

    assert "Logged delete attempt" in output, "Deletion attempt was not logged when delete_for_real is False"

if __name__ == "__main__":
   
    test_aws_service_explorer_lists_services()
    test_aws_service_explorer_detects_deletion_method()
    test_aws_service_explorer_no_delete_action_when_config_is_false()