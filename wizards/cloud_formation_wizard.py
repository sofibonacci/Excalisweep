import boto3
import datetime
from main import logger as l, config as c

def list_cloudformation_stacks():
    try:
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
        
        if not stacks:
            print("\n⚠️ No CloudFormation stacks found.")
            return None
    
        return stacks
    
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        
        


def delete_selected_stacks():
    stacks = list_cloudformation_stacks()  
    
    if stacks:
        
        print("\n All CloudFormation Stacks:")
        stack_list = list(stacks.keys())
        for idx, stack in enumerate(stack_list, start=1):
            status = stacks[stack]['StackStatus']
            print(f"{idx}. {stack} ({status})")

        print("\nEnter the numbers of the stacks you want to delete (comma-separated), or type 'all' to delete all:")
        choice = input("Your choice: ").strip().lower()

        if choice == "all":
            selected_stacks = stack_list
        else:
            try:
                indices = [int(i.strip()) - 1 for i in choice.split(",")]
                selected_stacks = [stack_list[i] for i in indices if 0 <= i < len(stack_list)]
            except (ValueError, IndexError):
                print("\n❌ Invalid selection. No stacks deleted.")
                return

        if not selected_stacks:
            print("\n🚫 No valid stacks selected for deletion.")
            return

        confirm = input(f"\n⚠️ Are you sure you want to delete these {len(selected_stacks)} stack(s)? (yes/no): ").strip().lower()
        if confirm == "yes":
            cloudformation_client = boto3.client('cloudformation')
            for stack in selected_stacks:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if c.config.delete_for_real == False:
                    l.log_deletion_attempt(stack, timestamp)
                    print(f"📝 Logged delete attempt for: {stack}")
                else:
                    cloudformation_client.delete_stack(StackName=stack)
        else:
            print("🚫 Deletion canceled.")
            
delete_selected_stacks()