import boto3, botocore
import datetime
from utility import *
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from logger import log_deletion_attempt
import config

def list_cloudformation_stacks(): #retrieve and display all cloudformation stacks
    try:
        client = boto3.client('cloudformation')
        stacks = {}
        response = client.list_stacks()

        for stack in response.get('StackSummaries', []):
            stack_name = stack['StackName']
            stack_status = stack['StackStatus']
            
            stacks[stack_name] = {
                'CreationTime': stack['CreationTime'],
                'StackStatus': stack_status,
                'StackId': stack['StackId'],
                'Description': 'No description retrieved (deleted stack)' if stack_status == 'DELETE_COMPLETE' else None
            }
        
        while 'NextToken' in response: 
            response = client.list_stacks(NextToken=response['NextToken'])
            for stack in response.get('StackSummaries', []):
                stack_name = stack['StackName']
                stack_status = stack['StackStatus']
                
                stacks[stack_name] = {
                    'CreationTime': stack['CreationTime'],
                    'StackStatus': stack['StackStatus'],
                    'StackId': stack['StackId'],
                'Description': 'No description retrieved (deleted stack)' if stack_status == 'DELETE_COMPLETE' else None
                }
                
        for stack_name, stack_info in stacks.items():
            try:
                if stack_info['StackStatus'] != 'DELETE_COMPLETE':
                    stack_details = client.describe_stacks(StackName=stack_name)['Stacks'][0]
                    stacks[stack_name]['Description'] = stack_details.get('Description', 'No description provided')
            except botocore.exceptions.ClientError as e:
                print(f"⚠️ No se pudo obtener la descripción de {stack_name}: {e}")
                stacks[stack_name]['Description'] = 'Error retrieving description'
        
        
        print_list_enumerate(stacks, "CloudFormation Stacks")
        
        return stacks if stacks else {}
    
    except botocore.exceptions.EndpointConnectionError as e:
        print(f"❌ Connection error: {e}")
        return {}
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ AWS BotoCore error: {e}")
        return {}
    except boto3.exceptions.Boto3Error as e:
        print(f"❌ AWS Boto3 error: {e}")
        return {}
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return {}
        
        


def delete_selected_stacks(): #delete selected cloudformation stacks
    print("Waiting for stacks...")
    stacks = list_cloudformation_stacks()  
    
    if not stacks:
        return
        
    selected_stacks = select_from_list(list(stacks.keys()),
                                       "Enter the numbers of the stacks you want to delete (comma-separated), or type 'all' to delete all:",)

    if not selected_stacks:
        print("\n🚫 No valid stacks selected for deletion.")
        return

    confirm = input(f"\n⚠️ Are you sure you want to delete these {len(selected_stacks)} stack(s)? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        print("🚫 Deletion canceled.")
        return
    
    try:
        cloudformation_client = boto3.client('cloudformation')
        for stack in selected_stacks:
            
            try:
                if config.delete_for_real:
                    cloudformation_client.delete_stack(StackName=stack)
                    log_deletion_attempt(stack, "CloudFormation",True)
                    print(f"✅ Successfully deleted: {stack}")
                else:
                    log_deletion_attempt(stack, "CloudFormation",True)
                    print(f" Logged delete attempt for: {stack}")
            
            except (botocore.exceptions.EndpointConnectionError, 
                    botocore.exceptions.BotoCoreError, 
                    boto3.exceptions.Boto3Error, 
                    Exception) as e:
                print(f"❌ Error while deleting {stack}: {e}")
                log_deletion_attempt(stack, "CloudFormation", False) 
    
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ General AWS BotoCore error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
            
def interactive_menu():
    print("""
    *****************************************
    *   Welcome to ExcaliSweep Cloud Formation Wizard!   *
    *   Your Cloud Formation Stacks Cleanup Assistant   *
    *****************************************
""")

    while True:
        #add choice to show logs
        print("\nMain Menu:")
        print("1. List Cloud Formation Stacks and Status")
        print("2. Delete Stacks")
        print("3. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            print("Waiting for stacks...")
            buckets = list_cloudformation_stacks()
        
        elif choice == "2":
            delete_selected_stacks()

        elif choice == "3":
            print("\n🔚 Exiting Excalisweep CloudFormation Wizard. Have a great day!")
            break
        
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    interactive_menu()

            
