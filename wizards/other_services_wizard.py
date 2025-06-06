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
# Get delete_for_real from environment variable
delete_for_real = os.getenv('DELETE_FOR_REAL', 'False') == 'True'

def list_services():  #list all available AWS services
    try:
        session = boto3.Session()
        services = sorted(session.get_available_services())
        print_columns(services, "Available AWS services")
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
    chosen_method = select_from_list(methods, "Choose a method to use by index or 'exit' to cancel: ", False)
    
    if chosen_method:
        execute_method(service, chosen_method[0])
    else:
        print("\n🚫 No valid method was selected.")
        return


def execute_method(service_name, method_name): #execute the method u choose (and asks u for the parameters)
    try:
        client = boto3.client(service_name)
        method = getattr(client, method_name)
        docstring = inspect.getdoc(method)
        lines= docstring.split('\n')
        
        #regex
        pattern_response = r'(\bresponse\s*=\s*client\.[\w_]+\([^)]*\))'
        response_syntax = re.findall(pattern_response, docstring)
        pattern_required  = r':param (\w+):\s+\*\*\[REQUIRED\]\*\*'
        required_params = re.findall(pattern_required , docstring)
        pattern_all_params = r':param (\w+):'
        all_params = re.findall(pattern_all_params, docstring)
        optional_params = [p for p in all_params if p not in required_params]
        
        print(f"\n🛠️ Method: {method_name}")
        print(f"\n📄 Description:{lines[0]}" if docstring else "No description available.\n")
        print(f"\n📦 Response Syntax:\n\n {response_syntax[0]}\n" if response_syntax else "\nNo response syntax available.\n")
        print(f"{'⚠️ Required Parameters: ' + ', '.join(required_params) if required_params else '✅ This method does not require any parameters.'}")
        print(f"{'📌 Optional Parameters: ' + ', '.join(optional_params) if optional_params else 'This method does not have any parameters'}")
        
        params_dict = {}
    
        if required_params:
            print("\n📥 Please provide values for the required parameters:")
            for param in required_params:
                value = input(f"  🔹 {param}: ").strip()
                if not value:
                    print(f"\n❌ No value provided for required parameter '{param}'. Aborting execution.")
                    return
                try:
                    params_dict[param] = json.loads(value)
                except json.JSONDecodeError:
                    params_dict[param] = value
        
        if optional_params:
            print("\n📥 Please provide values for the optional parameters (or leave blank):")
            for param in optional_params:
                value = input(f"  🔹 {param}: ").strip()
                if value:
                    try:
                        params_dict[param] = json.loads(value)
                    except json.JSONDecodeError:
                        params_dict[param] = value
        
        print(f"\nExecuting {service_name}.{method_name}()...\n")
        print(f"\nParameters:  {json.dumps(params_dict, indent=2)}")
        
        delete=any(word in method_name.lower() for word in ["delete", "terminate", "remove", "drop", "destroy", "purge"])
        if delete:
            if delete_for_real:
                try:
                    response = method(**params_dict)
                    log_action( service_name.title(),', '.join(map(str, params_dict.values())),True,mode="deletion")
                except Exception as e:
                    print(f"Error executing method: {e}")
                    log_action(service_name.title(),', '.join(map(str, params_dict.values())),False,mode="deletion")
            else:
                log_action(service_name.title(),', '.join(map(str, params_dict.values())),True,mode="deletion")
                print(f" Logged delete attempt for: {', '.join(map(str, params_dict.values()))}")
                return
        else:
            try:
                response = method(**params_dict)
            except Exception as e:
                    print(f"Error executing method: {e}")  
        
        
        status_code = response.get("ResponseMetadata", {}).get("HTTPStatusCode", None)
        if status_code == 200:
            response.pop("ResponseMetadata", None) 
            print(f"\n✅ Response:\n{json.dumps(response, indent=4, sort_keys=True, default=str)}")

        else:
            print(f"Failed with status code: {status_code if status_code else 'Unknown'}")
            
            
                
           
    except Exception as e:
        print(f"{e}")


if __name__ == "__main__":
    run_interactive_menu(
    "* Welcome to AWS Service Explorer!      *\n* Your AWS Service and Method Assistant *",
    [
        ("List AWS Services", list_services, False),
        ("Choose a Service and Method", choose_method, False),
        ("How to Use the AWS Service Explorer", lambda: print("""
            🧙 HOW TO USE THE AWS Service Explorer

            🔹 Option 1 - List AWS Services:
                This will list the available AWS services.

            🔹 Option 2 - Choose a Service and Method:
                Choose an AWS service (e.g., s3, ec2, eks), then select a method.
                The wizard will provide:
                ✅ A short description of the method
                ✅ Required & optional parameters
                ✅ An example of the response syntax
                
                You'll be prompted to input parameters:
                - Required: Must be entered
                - Optional: Can be skipped
                ⚠️ Enter them using **valid JSON** (e.g., lists as ["item1", "item2"])

                If the method is for deletion, it will log the action.

            🔹 Option 4 - Exit:
                Exits the AWS Service Explorer.

            -------------------------------------------------------------
            🎓 EXAMPLES USING EKS

            🔹 Example 1 - Method with REQUIRED parameter:
            👉 Service: eks
            👉 Method: delete_cluster
            👉 Required parameter: name

            📘 JSON input: "my-cluster"

            🔹 Example 2 - Method with optional parameters:
            👉 Service: cloudformation
            👉 Method: list_stacks
            👉 Optional: StackStatusFilter

            📘 JSON input: ["CREATE_IN_PROGRESS", "UPDATE_COMPLETE"]

            -------------------------------------------------------------
        """), False),

        ("Exit", None, True),
    ]
)
