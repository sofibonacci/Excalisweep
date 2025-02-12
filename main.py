import boto3
from datetime import datetime, timedelta

def list_billed_services():
    #list of AWS services that have incurred costs in the last 30 days 
    client = boto3.client('ce')  # cost explorer
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



def list_all_methods(service_name):
    #shows all methods of a service
    try:
        client = boto3.client(service_name)
        methods = [method for method in dir(client) if callable(getattr(client, method))]
        for method in methods:
            print(f"  - {method}")
    except Exception as e:
        print("Error")


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
    billed_services = list_billed_services()
    print("list of AWS services that have incurred costs in the last 30 days ")
    for service_name, cost in billed_services.items():
        print(f"  {service_name}: ${cost}")

    selected_service = input("\nchoose service ").strip()
    list_all_methods(selected_service)
    stacks = list_cloudformation_stacks()

    print("CloudFormation Stacks:") #print pretty
    for stack_name, stack_info in stacks.items():
        print(f"{stack_name}:")
        for key, value in stack_info.items():
            print(f"  {key}: {value}")
