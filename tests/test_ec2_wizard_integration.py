import subprocess
import boto3
import re
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_ec2_wizard_terminates_named_instance():
    ec2_client = boto3.client("ec2")
    instance_name = "excali-test-ec2"

    # Find instance ID from Name tag
    reservations = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [instance_name]},
            {"Name": "instance-state-name", "Values": ["pending", "running", "stopped", "stopping"]}
        ]
    )["Reservations"]
    assert reservations, f"Instance named '{instance_name}' not found"

    instance_id = reservations[0]["Instances"][0]["InstanceId"]

    # Path to EC2 wizard
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "wizards", "ec2_wizard.py")
    )

    # Step 1: Run wizard and print list of instances (menu option 2)
    result = subprocess.run(
        ["python", script_path],
        input="2\nexit\n".encode(),  # Shows terminate menu, then exits
        capture_output=True,
        timeout=30
    )
    output = result.stdout.decode()
    print("Wizard output:\n", output)

    # Find the index of the instance based on its name
    match = re.search(rf"(\d+)\. {instance_id} \([^)]+\) - {instance_name}", output)
    assert match, f"Instance '{instance_name}' not found in wizard output"
    instance_index = match.group(1)

    # Step 2: Run wizard to terminate the instance
    delete_input = f"2\n{instance_index}\nyes\n3\n"
    result = subprocess.run(
        ["python", script_path],
        input=delete_input.encode(),
        capture_output=True,
        timeout=30
    )
    final_output = result.stdout.decode()
    print("Final output:\n", final_output)

    assert "Successfully terminated" in final_output or "Logged terminate attempt" in final_output

# Wait for instance to reach 'terminated' state (polling every 5s, up to 60s)
timeout = 60
interval = 5
elapsed = 0
final_state = None

while elapsed < timeout:
    final_state = ec2_client.describe_instances(InstanceIds=[instance_id])
    instance_status = final_state["Reservations"][0]["Instances"][0]["State"]["Name"]
    if instance_status == "terminated":
        break
    print(f"Waiting for termination... current state: {instance_status}")
    time.sleep(interval)
    elapsed += interval

assert instance_status == "terminated", f"Instance not terminated after {timeout}s, current state: {instance_status}"
