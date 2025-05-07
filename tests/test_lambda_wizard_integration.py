import subprocess
import boto3
import re
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_lambda_wizard_terminates_named_function():
    lambda_client = boto3.client("lambda")
    function_name = "excali-test-lambda"

    # Check if the test function exists
    functions = lambda_client.list_functions()["Functions"]
    test_function = next((f for f in functions if f["FunctionName"] == function_name), None)
    assert test_function, f"Lambda function '{function_name}' not found"

    # Path to Lambda wizard
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "wizards", "lambda_wizard.py")
    )

    # Step 1: Run wizard and list functions (option 1)
    result = subprocess.run(
        ["python", script_path],
        input="2\n3\n".encode(),  # List functions then exit
        capture_output=True,
        timeout=30
    )
    output = result.stdout.decode()
    print("Wizard output:\n", output)

    match = re.search(rf"(\d+)\. {function_name}", output)
    assert match, f"Function '{function_name}' not listed in wizard output"
    function_index = match.group(1)

    # Step 2: Run wizard to delete the function
    delete_input = f"2\n{function_index}\nyes\n3\n"
    result = subprocess.run(
        ["python", script_path],
        input=delete_input.encode(),
        capture_output=True,
        timeout=30
    )
    final_output = result.stdout.decode()
    print("Final output:\n", final_output)

    assert "Successfully deleted function" in final_output or "Logged delete attempt" in final_output

    # Step 3: Confirm deletion (polling every 5s, up to 60s)
    timeout = 60
    interval = 5
    elapsed = 0
    still_exists = True

    while elapsed < timeout:
        current_functions = lambda_client.list_functions()["Functions"]
        if not any(f["FunctionName"] == function_name for f in current_functions):
            still_exists = False
            break
        print(f"Waiting for deletion... still found.")
        time.sleep(interval)
        elapsed += interval

    assert not still_exists, f"Function '{function_name}' still exists after {timeout}s"
