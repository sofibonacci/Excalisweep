import subprocess
import boto3
import re
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

#PRECONDITION: the testing bucket already exists (bucket_name is hardcoded) AND config.py has delete_for_real set to True
#TODO: move this file to folder tests and change paths from above if necessary

def test_s3_wizard_deletes_known_bucket():
    bucket_name = "excali-test-bucket"
    s3_client = boto3.client('s3')

    # Ensure the test bucket exists
    assert bucket_name in [b['Name'] for b in s3_client.list_buckets()['Buckets']]

    # Run the wizard with menu option 2 to get the bucket list
    script_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "wizards", "s3_wizard.py")
    )
    result = subprocess.run(
        ["python", script_path],
        input="2\nexit\n".encode(),
        capture_output=True,
        timeout=30
    )
    output = result.stdout.decode()
    print("Wizard output:\n", output)

    # Extract the bucket's number from the menu using regex
    match = re.search(rf"(\d+)\. {bucket_name}", output)
    assert match, f"Bucket '{bucket_name}' not found in wizard output"
    bucket_index = match.group(1)

    # Run the wizard again to delete the bucket
    delete_input = f"2\n{bucket_index}\nyes\n3\n"
    result = subprocess.run(
        ["python", script_path],
        input=delete_input.encode(),
        capture_output=True,
        timeout=30
    )
    final_output = result.stdout.decode()
    print("Final output:\n", final_output)

    # Assert deletion message and that the bucket is now gone
    assert "Successfully deleted" in final_output or "Logged delete attempt" in final_output
    time.sleep(3)
    assert bucket_name not in [b['Name'] for b in s3_client.list_buckets()['Buckets']]
