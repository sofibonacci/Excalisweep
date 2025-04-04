import boto3, botocore
import re
import inspect
import json
from utility import *
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from logger import log_action
import config

"""
example for saving logs:
log_action(
    service_name="Lambda",
    resource_name={here goes the resource being called}, 
    success=None,  # Not needed for this mode
    mode="other",
    function_name="{here goes the function name}",
    json_input='{here goes the json input}',
    response_json='{here goes the response}'

    when testing, see how it looks on the log file and if it needs formatting, specially for the jsons
)
"""


def list_services():  #list all available AWS servicees
    try:
        session = boto3.Session()
        services  = session.get_available_services()
        print_list_enumerate(services, "Available AWS services")
        return services 
        
    except botocore.exceptions.BotoCoreError as e:
        print(f"Error with Boto3: {e}")
        return []
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []


def list_all_methods(service_name): #list all methods of a specific AWS service
    try:
        client = boto3.client(service_name)
        methods = [method for method in dir(client) if callable(getattr(client, method))]
        
        # Filter methods related to deletion and listing
        keywords = {"delete", "terminate", "remove", "drop", "destroy", "purge", "list"}
        filtered_methods = [method for method in methods if any(kw in method.lower() for kw in keywords)]
        
        print_list_enumerate(filtered_methods, "Methods related to deletion and listing")
        return filtered_methods
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ Error retrieving methods for service '{service_name}': {e}")
        return []
    except Exception as e:
        print(f"❌ An unexpected error occurred for '{service_name}': {e}")
        return []



def choose_method():  #choose a service and a method to execute
    available_services = list_services()
    service = input("\nEnter an AWS service name (e.g., s3, ec2, lambda): ").strip().lower()
    if service not in available_services:
        print("\nInvalid service name")
        return
    
    methods = list_all_methods(service)
    chosen_method = select_from_list(methods, "Choose a method to use by index")
    
    if chosen_method:
        execute_method(service, chosen_method[0])
    

def execute_method(service_name, method_name): #execute the method u choose (and asks u for the parameters)
    try:
        client = boto3.client(service_name)
        method = getattr(client, method_name)
        signature = inspect.signature(method)
        docstring = inspect.getdoc(method).split('\n')
        pattern = r'(\bresponse\s*=\s*client\.[\w_]+\([^)]*\))'
        match = re.findall(pattern, inspect.getdoc(method))
        required_params = [param for param, details in signature.parameters.items() if details.default == inspect.Parameter.empty]
        
        print(f"\nMethod: {method_name}")
        print(f"\nDescription:\n{docstring[0]} \nResponse Syntax: {match[0]}\n" if docstring else "\nNo description available.\n")
        
        
        if required_params:
            params = input('Enter parameters as a JSON string (ex. : {"key": "value"}): ').strip() 
            params_dict = {}
            if params:
                try:
                    params_dict = json.loads(params)
                except json.JSONDecodeError:
                    print("\n❌ Invalid JSON format. Aborting execution.")
                    return
        else:
            params_dict = {}
        
        print(f"\nExecuting {service_name}.{method_name}()...")
        #if config.delete_for_real:
        response = method(**params_dict)
        print("\nResponse:", response)
    except Exception as e:
        print(f"Error executing method: {e}")


def interactive_menu():  # Interactive menu for user interaction
    print("""
    *****************************************
    *   Welcome to AWS Service Explorer!   *
    *   Your AWS Service and Method Assistant   *
    *****************************************
    """)

    while True:
        print("\nMain Menu:")
        print("1. List AWS Services")
        print("2. Choose a Service and Method")
        print("3. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            services = list_services()
        
        elif choice == "2":
            choose_method()

        elif choice == "3":
            print("\n🔚 Exiting AWS Service Explorer. Have a great day!")
            break
        
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    interactive_menu()



