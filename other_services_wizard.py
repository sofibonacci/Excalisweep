import boto3
import inspect
import json
import config
from logger import log_deletion_attempt
import datetime
import json


def list_services():  #list of all aws services
    session = boto3.Session()
    return session.get_available_services()

def list_all_methods(service_name): #shows all methods of a service
    try:
        client = boto3.client(service_name)
        methods = [method for method in dir(client) if callable(getattr(client, method))]
        
        # Filter methods related to deletion and listing
        delete_keywords = ["delete", "terminate", "remove", "drop", "destroy", "purge", "list"]
        delete_methods = [method for method in methods if any(kw in method.lower() for kw in delete_keywords)]
        
        print("\nMethods related to deletion and listing:")
        for idx, method in enumerate(delete_methods, start=1):
            print(f"  {idx}. {method}")
        
        return delete_methods
    
    except Exception as e:
        print(f"Error retrieving methods for service '{service_name}': {e}")
        return 



def choose_method():  #shows u all the services and you choose one and then choose a method
    available_services=list_services()
    if not available_services:
        print("\n❌ No available AWS services found.")
        return
    
    print("\nAvailable AWS services:")
    for service in available_services:
        print(f" {service}")
    
    
    service = input("\nEnter an AWS service name (e.g., s3, ec2, lambda): ").strip().lower()

    if service not in available_services:
        print("\n❌ Invalid service name")
        return
    
    methods = list_all_methods(service)
    
    if not methods:
        print("\n❌ No available methods found.")
        return

    method_index = int(input("\nChoose a method to use by index: ")) - 1
    try:
        if 0 <= method_index < len(methods):
            method_name = methods[method_index]
            execute_method(service, method_name)
        else:
            
            print("\n❌ Invalid method index.")
            
    except ValueError:
        print("\n❌ Please enter a valid number.")

def execute_method(service_name, method_name): #execute the method u choose (and asks u for the parameters)
    try:
        client = boto3.client(service_name)
        method = getattr(client, method_name)
        signature = inspect.signature(method)
        docstring = inspect.getdoc(method).split('\n')
        required_params = [param for param, details in signature.parameters.items() if details.default == inspect.Parameter.empty]
        
        print(f"\nMethod: {method_name}")
        print(f"\nDescription:\n{docstring[0]}\n" if docstring else "\nNo description available.\n")
    
        if required_params:
            print(f"This method requires parameters: {', '.join(required_params)}")
            params = input("Enter parameters as a JSON string: ").strip() ##TODO ADD PARMS NAME
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
        #if config.delete_for_real :
        response = method(**params_dict)
        print("\nResponse:")
        print(json.dumps(response, indent=4))
        #else:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #log_deletion_attempt(params_dict, timestamp)
        print(f"📝 Logged delete attempt for: {params_dict}")
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
            if services:
                print("\nAvailable AWS services:")
                for service in services:
                    print(f" {service}")
        
        elif choice == "2":
            choose_method()

        elif choice == "3":
            print("\n🔚 Exiting AWS Service Explorer. Have a great day!")
            break
        
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    interactive_menu()



