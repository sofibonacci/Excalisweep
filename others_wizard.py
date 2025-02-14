import boto3
import inspect
import json

def list_services():
    session = boto3.Session()
    return session.get_available_services()

def list_all_methods(service_name):
    #shows all methods of a service
    try:
        client = boto3.client(service_name)
        methods = [method for method in dir(client) if callable(getattr(client, method))]
        for idx, method in enumerate(methods, start=1):
            print(f"  {idx}. {method}")
    except Exception as e:
        print("Error")
    return methods



def choose_method():
    available_services=list_services()
    print(available_services)
    service = input("\nEnter an AWS service name (e.g., s3, ec2, lambda): ").strip().lower()

    if service not in available_services:
        print("\n❌ Invalid service name. Use one of these:\n", ", ".join(available_services))
        return
    
    methods = list_all_methods(service)
    if not methods:
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
    
def execute_method(service_name, method_name):
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
        response = method(**params_dict)
        print("\nResponse:", response)
    except Exception as e:
        print(f"Error executing method: {e}")



choose_method()


