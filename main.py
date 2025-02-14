import boto3
import os
import subprocess
from datetime import datetime, timedelta

def show_intro():
    print("""
    ****************************************
    *        Welcome to ExaliSweep!        *
    *   Your AWS Cleanup Wizard Assistant  *
    ****************************************
    """)

def list_billed_services():
    client = boto3.client('ce')  # Cost Explorer
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=30)

    response = client.get_cost_and_usage(
        TimePeriod={'Start': start_date.strftime('%Y-%m-%d'), 'End': end_date.strftime('%Y-%m-%d')},
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )

    billed_services = {}
    for group in response.get('ResultsByTime', [])[0].get('Groups', []):
        service_name = group['Keys'][0]
        cost = float(group['Metrics']['UnblendedCost']['Amount'])
        if cost > 0:
            billed_services[service_name] = cost

    return billed_services

def show_billed_services():
    print("\nAWS Services with costs in the last 30 days:")
    services = list_billed_services()
    if not services:
        print("  No services with costs found.")
    else:
        for service, cost in services.items():
            print(f"  {service}: ${cost:.2f}")

def invoke_script(script_name):
    print(f"\nRunning {script_name}...")
    try:
        subprocess.run(['python', script_name], check=True)
    except FileNotFoundError:
        print(f"Error: {script_name} not found.")
    except subprocess.CalledProcessError:
        print(f"Error: {script_name} encountered an issue.")

def show_logs():
    log_file = 'logs.txt'
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            print("\n--- Logs ---")
            print(file.read())
    else:
        print("\nNo log file found.")

def main_menu():
    while True:
        print("\nOptions:")
        print("  1. Show billed AWS services")
        print("  2. Run S3 Cleanup Wizard")
        print("  3. Run CloudFormation Cleanup Wizard")
        print("  4. View logs")
        print("  5. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            show_billed_services()
        elif choice == '2':
            invoke_script('s3_wizard.py')
        elif choice == '3':
            invoke_script('cloud_formation_wizard.py')
        elif choice == '4':
            show_logs()
        elif choice == '5':
            print("Exiting ExaliSweep. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    show_intro()
    main_menu()



#----


""" should go on cloud formation wizard


def list_cloudformation_stacks():
    client = boto3.client('cloudformation') #choose the client (ex. ec2, lambda....)
    stacks = {}
    response = client.list_stacks(StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE']) #retrives a list of the stacks
    
    for stack in response.get('StackSummaries', []):
        stacks[stack['StackName']] = {
            'CreationTime': stack['CreationTime'],
            'StackStatus': stack['StackStatus'],
            'StackId': stack['StackId']
        }
    
    while 'NextToken' in response: #if NextToken is present, there are more stacks to fetch (Pagination Handling)
        response = client.list_stacks(StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE'], NextToken=response['NextToken'])
        for stack in response.get('StackSummaries', []):
            stacks[stack['StackName']] = {
                'CreationTime': stack['CreationTime'],
                'StackStatus': stack['StackStatus'],
                'StackId': stack['StackId']
            }
    
    return stacks

stacks = list_cloudformation_stacks()

print("CloudFormation Stacks:") #print pretty
for stack_name, stack_info in stacks.items():
    print(f"{stack_name}:")
    for key, value in stack_info.items():
        print(f"  {key}: {value}")

should go on others wizard


def list_all_methods(service_name):
    #shows all methods of a service
    try:
        client = boto3.client(service_name)
        methods = [method for method in dir(client) if callable(getattr(client, method))]
        for method in methods:
            print(f"  - {method}")
    except Exception as e:
        print("Error")

selected_service = input("\nchoose service ").strip()
list_all_methods(selected_service) """