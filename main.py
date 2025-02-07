import boto3

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

if __name__ == "__main__": 
    stacks = list_cloudformation_stacks()
    print("CloudFormation Stacks:") #print pretty
    for stack_name, stack_info in stacks.items():
        print(f"{stack_name}:")
        for key, value in stack_info.items():
            print(f"  {key}: {value}")
