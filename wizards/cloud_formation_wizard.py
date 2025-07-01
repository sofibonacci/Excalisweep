import boto3, botocore
from utility import *
import sys
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from logger import log_action
import config

# Get delete_for_real from environment variable
delete_for_real = os.getenv('DELETE_FOR_REAL', 'False') == 'True'
MAX_WORKERS = 5  # limit of stacks deleted at the same time

successfully_deleted = []
failed_to_delete = []
lock = threading.Lock()

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
        
        


def delete_stack_worker(stack_name):
    cloudformation_client = boto3.client('cloudformation')
    try:
        if delete_for_real:
            cloudformation_client.delete_stack(StackName=stack_name)
            waiter = cloudformation_client.get_waiter('stack_delete_complete')
            waiter.wait(StackName=stack_name)
            with lock:
                successfully_deleted.append(stack_name)
            log_action("Cloud Formation", stack_name, True, mode="deletion")
        else:
            with lock:
                successfully_deleted.append(stack_name)
            log_action("Cloud Formation", stack_name, True, mode="deletion")
    except Exception as e:
        with lock:
            failed_to_delete.append((stack_name, str(e)))
        log_action("Cloud Formation", stack_name, False, mode="deletion")


def _background_stack_deletion(selected_stacks):
    print(f"Starting deletion in background with up to {MAX_WORKERS} concurrent stacks...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(delete_stack_worker, stack): stack for stack in selected_stacks}
        for future in as_completed(futures):
            pass  

    print("\nAll deletions have finished.\n")

    # sumarry of operations
    print("\n" + "="*50)
    print("🔔 OPERATION SUMMARY".center(50))
    print("="*50)

    if successfully_deleted:
        print("\n✅ Successfully deleted stacks:")
        for stack in successfully_deleted:
            print(f"   - {stack}")
    else:
        print("\n⚠️  No stacks were successfully deleted.")

    if failed_to_delete:
        print("\n❌ Stacks that failed to delete:")
        for stack, error in failed_to_delete:
            print(f"   - {stack}: {error}")
    else:
        print("\n✅ No deletion errors occurred.")

    print("="*50 + "\n")



def delete_selected_stacks():
    print("Retrieving CloudFormation stacks...")
    stacks = list_cloudformation_stacks()  

    if not stacks:
        return

    selected_stacks = select_from_list(
        list(stacks.keys()),
        "Enter the numbers of the stacks you want to delete (comma-separated), type 'all' to delete all or 'exit' to cancel: ",
    )

    if not selected_stacks:
        print("No valid stacks were selected for deletion.")
        return

    confirm = input(f"Are you sure you want to delete these {len(selected_stacks)} stack(s)? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Deletion canceled.")
        return

    thread = threading.Thread(target=_background_stack_deletion, args=(selected_stacks,))
    thread.daemon = True
    thread.start()

    print("Deletion has been initiated in the background. You can continue working.")


if __name__ == "__main__":
    run_interactive_menu(
    "*   Welcome to ExcaliSweep Cloud Formation Wizard!  *\n*   Your Cloud Formation Stacks Cleanup Assistant   *",
    [
        ("List CloudFormation Stacks and Status", list_cloudformation_stacks, False),
        ("Delete Stacks", delete_selected_stacks, False),
        ("Exit", None, True)
    ]
)

            
