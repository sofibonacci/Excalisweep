import boto3
import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from logger import log_action
import config 

def list_lambda_functions():
    lambda_client = boto3.client('lambda')
    response = lambda_client.list_functions()
    
    functions = {}
    for function in response.get('Functions', []):
        function_name = function['FunctionName']
        try:
            # Get function details including its aliases and versions
            aliases = lambda_client.list_aliases(FunctionName=function_name)
            versions = lambda_client.list_versions_by_function(FunctionName=function_name)
            
            aliases_list = [alias['AliasName'] for alias in aliases.get('Aliases', [])]
            versions_list = [version['Version'] for version in versions.get('Versions', [])]
            
            functions[function_name] = {
                'Created': function['LastModified'],
                'Aliases': aliases_list,
                'Versions': versions_list
            }
        except Exception as e:
            print(f"Error fetching details for Lambda function {function_name}: {str(e)}")
            log_action("Lambda", function_name, False, mode="deletion")
    
    return functions

def delete_lambda_function(function_name, lambda_client):
    try:
        # Delete aliases
        aliases = lambda_client.list_aliases(FunctionName=function_name).get('Aliases', [])
        for alias in aliases:
            lambda_client.delete_alias(FunctionName=function_name, Name=alias['AliasName'])
            print(f"Successfully deleted alias: {alias['AliasName']} for function: {function_name}")

        # Delete all versions of the Lambda function (except $LATEST)
        versions = lambda_client.list_versions_by_function(FunctionName=function_name).get('Versions', [])
        for version in versions:
            if version['Version'] != '$LATEST':
                lambda_client.delete_function(FunctionName=function_name, Qualifier=version['Version'])
                print(f"Successfully deleted version: {version['Version']} of function: {function_name}")
        
        # Delete the Lambda function itself
        lambda_client.delete_function(FunctionName=function_name)
        print(f"Successfully deleted function: {function_name}")
        return True
    except Exception as e:
        print(f"Error deleting Lambda function {function_name}: {str(e)}")
        log_action("Lambda", function_name, False, mode="deletion")
        return False

def delete_selected_lambda_functions():
    print("Waiting for Lambda functions...")
    lambda_client = boto3.client('lambda')
    functions = list_lambda_functions()

    if not functions:
        print("\n⚠️ No Lambda functions found.")
        return

    print("\n🗑️ All Lambda Functions:")
    function_list = list(functions.keys())
    for idx, function in enumerate(function_list, start=1):
        print(f"{idx}. {function} (Created: {functions[function]['Created']})")

    print("\nEnter the numbers of the Lambda functions you want to delete (comma-separated), or type 'all' to delete all:")
    choice = input("Your choice: ").strip().lower()

    if choice == "all":
        selected_functions = function_list
    else:
        try:
            indices = [int(i.strip()) - 1 for i in choice.split(",")]
            selected_functions = [function_list[i] for i in indices if 0 <= i < len(function_list)]
        except (ValueError, IndexError):
            print("\nInvalid selection. No functions deleted.")
            return

    if not selected_functions:
        print("\nNo valid functions selected for deletion.")
        return

    confirm = input(f"\nAre you sure you want to delete these {len(selected_functions)} Lambda function(s)? (yes/no): ").strip().lower()
    if confirm == "yes":
        for function in selected_functions:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if config.delete_for_real:
                # Delete the function and its resources
                if delete_lambda_function(function, lambda_client):
                    print(f"Successfully deleted Lambda function and resources: {function}")
                    logger.log_deletion_attempt(function_name, "Lambda", True)
                else:
                    print(f"Failed to delete Lambda function: {function}. Skipping.")
                    logger.log_deletion_attempt(function_name, "Lambda", False)
            else:
                log_action("Lambda", function, True, mode="deletion")

                print(f"Logged delete attempt for: {function}")
    else:
        print("Deletion canceled.")

def interactive_menu():
    print("""
    *****************************************
    *   Welcome to Excalisweep Lambda Wizard!  *
    *   Your Lambda Functions Cleanup Assistant  *
    *****************************************
""")

    while True:
        print("\nMain Menu:")
        print("1. List Lambda Functions")
        print("2. Delete Lambda Functions")
        print("3. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            print("Waiting for Lambda functions...")
            functions = list_lambda_functions()
            if functions:
                print("\n💻 Lambda Functions:")
                for function_name, function_info in functions.items():
                    print(f"\n{function_name}:")
                    print(f"  Created: {function_info['Created']}")
                    print(f"  Aliases: {', '.join(function_info['Aliases'] or ['No aliases'])}")
                    print(f"  Versions: {', '.join(function_info['Versions'] or ['No versions'])}")
            else:
                print("\nNo Lambda functions found.")
        
        elif choice == "2":
            delete_selected_lambda_functions()

        elif choice == "3":
            print("\n🔚 Exiting Excalisweep Lambda Wizard. Have a great day!")
            break
        
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    interactive_menu()
