import boto3, botocore
import datetime
from utility import *
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logger import log_action
import config

def list_cloudformation_stacks(): #retrieve and display all cloudformation stacks
    StackStatusFilter=[
                'CREATE_IN_PROGRESS', 'CREATE_FAILED', 'CREATE_COMPLETE',
                'ROLLBACK_IN_PROGRESS', 'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE',
                'DELETE_IN_PROGRESS', 'DELETE_FAILED',
                'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
                'UPDATE_COMPLETE', 'UPDATE_FAILED',
                'UPDATE_ROLLBACK_IN_PROGRESS', 'UPDATE_ROLLBACK_FAILED',
                'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_COMPLETE',
                'REVIEW_IN_PROGRESS', 'IMPORT_IN_PROGRESS', 'IMPORT_COMPLETE',
                'IMPORT_ROLLBACK_IN_PROGRESS', 'IMPORT_ROLLBACK_FAILED', 'IMPORT_ROLLBACK_COMPLETE'
            ]
    try:
        client = boto3.client('cloudformation')
        stacks = {}
        response = client.list_stacks(StackStatusFilter=StackStatusFilter)

        for stack in response.get('StackSummaries', []):
            stack_name = stack['StackName']
            stack_status = stack['StackStatus']
            
            stacks[stack_name] = {
                'StackStatus': stack_status,
                'StackId': stack['StackId'],
                'Description': None
            }
        
        while 'NextToken' in response: 
            response = client.list_stacks(StackStatusFilter=StackStatusFilter,NextToken=response['NextToken'])
            
            for stack in response.get('StackSummaries', []):
                stack_name = stack['StackName']
                stacks[stack_name] = {
                    'StackStatus': stack['StackStatus'],
                    'StackId': stack['StackId'],
                    'Description': None  
                }
                
        for stack_name in stacks.keys():
            try:
                stack_details = client.describe_stacks(StackName=stack_name)['Stacks'][0]
                stacks[stack_name]['Description'] = stack_details.get('Description', 'No description provided')
            except botocore.exceptions.ClientError as e:
                print(f"⚠️ Failed to get the description of {stack_name}: {e}")
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
    print("Retrieving CloudFormation stacks......")
    stacks = list_cloudformation_stacks()  
    
    if not stacks:
        return
        
    selected_stacks = select_from_list(list(stacks.keys()),
                                       "Enter the numbers of the stacks you want to delete (comma-separated), type 'all' to delete all or 'exit' to cancel: ",)

    if not selected_stacks:
        print("\n🚫 No valid stacks were selected for deletion.")
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
                    print(f"⏳ Deletion initiated for: {stack}, waiting for confirmation...")
                    waiter = cloudformation_client.get_waiter('stack_delete_complete')
                    try:
                        waiter.wait(StackName=stack)
                        print(f"✅ Successfully deleted: {stack}")
                        log_action("Cloud Formation",stack, True, mode="deletion")
                    except botocore.exceptions.WaiterError as e:
                        print(f"⚠️ Failed to delete {stack}. It may have dependencies.")
                        log_action("Cloud Formation",stack, False, mode="deletion")
                else:
                    log_action("Cloud Formation", stack, True, mode="deletion")
                    print(f" Logged delete attempt for: {stack}")
            
            except (botocore.exceptions.EndpointConnectionError, 
                    botocore.exceptions.BotoCoreError, 
                    boto3.exceptions.Boto3Error, 
                    Exception) as e:
                print(f"❌ Error while deleting {stack}: {e}")
                log_action("Cloud Formation", stack, False, mode="deletion")
    
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ General AWS BotoCore error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
            


if __name__ == "__main__":
    run_interactive_menu(
    "*   Welcome to ExcaliSweep Cloud Formation Wizard!   *\n*   Your Cloud Formation Stacks Cleanup Assistant   *",
    [
        ("List CloudFormation Stacks and Status", list_cloudformation_stacks, False),
        ("Delete Stacks", delete_selected_stacks, False),
        ("Exit", None, True)
    ]
)

            
