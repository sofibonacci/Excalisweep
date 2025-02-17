import boto3
import os
import subprocess
from datetime import datetime, timedelta
from config import days_to_observe

def show_intro():
    print("""
    ****************************************
    *        Welcome to ExcaliSweep!        *
    *   Your AWS Cleanup Wizard Assistant  *
    ****************************************
    """)

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
    """Display AWS services that have incurred costs in the last specified number of days."""
    print(f"\nAWS Services with costs in the last {days_to_observe} days:")
    services = list_billed_services()
    if not services:
        print("  No services with costs found.")
    else:
        for service, cost in sorted(services.items(), key=lambda x: x[1], reverse=True):
            print(f"  {service}: ${cost:.2f}")

def invoke_script(script_name):
    """Execute a cleanup wizard script safely."""
    print(f"\nRunning {script_name}...")
    try:
        if not os.path.exists(script_name):
            raise FileNotFoundError(f"Error: {script_name} not found.")
        subprocess.run(['python', script_name], check=True)
    except FileNotFoundError as e:
        print(e)
    except subprocess.CalledProcessError:
        print(f"Error: {script_name} encountered an issue.")
    except Exception as e:
        print(f"Unexpected error running {script_name}: {e}")

def show_logs():
    """Display logs if available."""
    log_file = 'logs.txt'
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
        '2': lambda: invoke_script('s3_wizard.py'),
        '3': lambda: invoke_script('cloud_formation_wizard.py'),
        '4': lambda: invoke_script('other_services_wizard.py'),
        '5': show_logs,
        '6': lambda: print("Exiting ExcaliSweep. Goodbye!")
    }
    
    while True:
        print("\nOptions:")
        print("  1. Show billed AWS services")
        print("  2. Run S3 Cleanup Wizard")
        print("  3. Run CloudFormation Cleanup Wizard")
        print("  4. Run Other Services Cleanup Wizard")
        print("  5. View logs")
        print("  6. Exit")
        choice = input("Select an option: ").strip()
        
        action = options.get(choice)
        if action:
            if choice == '6':
                action()
                break
            else:
                action()
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    show_intro()
    main_menu()
