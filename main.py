import boto3
import os
import subprocess
from datetime import datetime, timedelta
from config import *
import requests
import time

def show_intro():
    print("""
    ****************************************
    *        Welcome to ExcaliSweep!        *
    *   Your AWS Cleanup Wizard Assistant  *
    ****************************************
    """)
    print("Warning: The resources displayed are based on your current Availability Zone (AZ) and Region. If you're unable to find what you're looking for, try switching to a different AZ or Region.")


    region = get_region()
    az = get_availability_zone()
    print(f"📍 Region: {region}")
    print(f"🏠 Availability Zone: {az}\n")
    set_status()

def get_region():
    """Get current AWS region from boto3 session, or fallback to instance metadata."""
    session = boto3.session.Session()
    region = session.region_name
    if region:
        return region
    else:
        raise Exception("Region not available")

def get_availability_zone():
    """Get AZ using AWS IMDSv2 if running on EC2."""
    try:
        # Getting the token 
        token_url = "http://169.254.169.254/latest/api/token"
        headers = {"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
        token = requests.put(token_url, headers=headers, timeout=2).text

        # Using that token to get the AZ
        metadata_url = "http://169.254.169.254/latest/meta-data/placement/availability-zone"
        headers = {"X-aws-ec2-metadata-token": token}
        response = requests.get(metadata_url, headers=headers, timeout=2)
        return response.text
    except requests.RequestException:
        return "Not available (outside EC2 or IMDSv2 required)"
def set_status():
    """set status to real deletion or testing"""
    global delete_for_real
    while True:
        print()
        status=input("Choose a mode: press 'r' for real deletion of buckets, or 't' for testing only: ").strip().lower()
        if status in ("r","t"):
            if status=="r":
                delete_for_real= True
                print("Real deletion mode activated.")
            else:
                delete_for_real=False
                print("Testing mode activated.")
            break
        print("Invalid input. Please enter 'r' or 't'.")
        time.sleep(1)

def list_billed_services():
    """Retrieve AWS services that incurred costs in the last specified number of days on config.py."""
    try:
        client = boto3.client('ce')  # Cost Explorer
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days_to_observe)

        response = client.get_cost_and_usage(
            TimePeriod={'Start': start_date.strftime('%Y-%m-%d'), 'End': end_date.strftime('%Y-%m-%d')},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )

        billed_services = {
            group['Keys'][0]: float(group['Metrics']['UnblendedCost']['Amount'])
            for group in response.get('ResultsByTime', [])[0].get('Groups', [])
            if float(group['Metrics']['UnblendedCost']['Amount']) > 0
        }
        return billed_services
    except boto3.exceptions.Boto3Error as e:
        print(f"Error retrieving billed services: {e}")
        return {}

def show_billed_services():
    """Display AWS services that have been active on the last specified number of days."""
    print(f"\nAWS Services that have been active on the last {days_to_observe} days:")

    services = list_billed_services()
    if not services:
        print("No active services found.")
    else: 
        for service, cost in sorted(services.items(), key=lambda x: x[1], reverse=True):
            print(f" {service}: ${cost:.2f}")

def invoke_script(script_name):
    """Execute a cleanup wizard script safely."""
    print(f"\nRunning {script_name}...")
    script_path=f'wizards.{script_name}'
    try:
        subprocess.run(['python','-m',script_path], check=True)
    except FileNotFoundError as e:
        print(e)
    except subprocess.CalledProcessError:
        print(f"Error: {script_name} encountered an issue.")
    except Exception as e:
        print(f"Unexpected error running {script_name}: {e}")

def show_logs():
    """Display logs if available."""
    log_file = 'excalisweep.logs'
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as file:
                print("\n--- Logs ---")
                print(file.read())
        except IOError as e:
            print(f"Error reading log file: {e}")
    else:
        print("\nNo log file found.")

def main_menu():
    """Display the main menu and handle user selection."""
    options = {
        '1': show_billed_services,
        '2': lambda: invoke_script('s3_wizard'),
        '3': lambda: invoke_script('cloud_formation_wizard'),
        '4': lambda: invoke_script('other_services_wizard'),
        '5': lambda: invoke_script('ec2_wizard'),
        '6': lambda: invoke_script('lambda_wizard'),
        '7': show_logs,
        '8': set_status,
        '9': lambda: print("Exiting ExcaliSweep. Goodbye!")
    }
    
    while True:
        print("\nOptions:")
        print("  1. Show billed AWS services")
        print("  2. Run S3 Cleanup Wizard")
        print("  3. Run CloudFormation Cleanup Wizard")
        print("  4. Run Other Services Cleanup Wizard")
        print("  5. Run EC2 Cleanup Wizard")
        print("  6. Run Lambda Cleanup Wizard")
        print("  7. View logs")
        print("  8. Change mode")
        print("  9. Exit")
        choice = input("Select an option: ").strip()
        
        action = options.get(choice)
        if action:
            if choice == '9':
                action()
                break
            else:
                action()
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    show_intro()
    main_menu()
