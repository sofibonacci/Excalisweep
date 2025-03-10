import boto3
import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import logger as l
import config as c

def list_ec2_instances():
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_instances()
    
    instances = {}
    for reservation in response.get('Reservations', []):
        for instance in reservation.get('Instances', []):
            instance_id = instance['InstanceId']
            state = instance['State']['Name']
            launch_time = instance['LaunchTime']
            instance_type = instance['InstanceType']
            description = instance.get('Tags', [{'Key': 'Name', 'Value': 'No Description'}])[0]['Value']
            
            instances[instance_id] = {
                'LaunchTime': launch_time,
                'Status': state,
                'InstanceType': instance_type,
                'Description': description
            }
    
    return instances

def terminate_selected_instances():
    print("Waiting for instances...")
    ec2_client = boto3.client('ec2')
    instances = list_ec2_instances()

    if not instances:
        print("\n⚠️ No EC2 instances found.")
        return

    print("\n All EC2 Instances:")
    instance_list = list(instances.keys())
    for idx, instance in enumerate(instance_list, start=1):
        status = instances[instance]['Status']
        description = instances[instance]['Description']
        print(f"{idx}. {instance} ({status}) - {description}")

    print("\nEnter the numbers of the instances you want to terminate (comma-separated), or type 'all' to terminate all:")
    choice = input("Your choice: ").strip().lower()

    if choice == "all":
        selected_instances = instance_list
    else:
        try:
            indices = [int(i.strip()) - 1 for i in choice.split(",")]
            selected_instances = [instance_list[i] for i in indices if 0 <= i < len(instance_list)]
        except (ValueError, IndexError):
            print("\nInvalid selection. No instances terminated.")
            return

    if not selected_instances:
        print("\nNo valid instances selected for termination.")
        return

    confirm = input(f"\nAre you sure you want to terminate these {len(selected_instances)} instance(s)? (yes/no): ").strip().lower()
    if confirm == "yes":
        for instance in selected_instances:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if c.config.delete_for_real:
                try:
                    ec2_client.terminate_instances(InstanceIds=[instance])
                    print(f"Successfully terminated: {instance}")
                except Exception as e:
                    print(f"Failed to terminate {instance}: {str(e)}")
                    l.log_deletion_attempt(instance, "EC2", False)
            else:
                l.log_deletion_attempt(instance, "EC2", True)
                print(f"Logged terminate attempt for: {instance}")
    else:
        print("Termination canceled.")

def interactive_menu():
    print("""
    *****************************************
    *   Welcome to ExcaliSweep EC2 Wizard!  *
    *   Your EC2 Instances Cleanup Assistant  *
    *****************************************
""")

    while True:
        print("\nMain Menu:")
        print("1. List EC2 Instances and Status")
        print("2. Terminate Instances")
        print("3. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            print("Waiting for instances...")
            instances = list_ec2_instances()
            if instances:
                print("\n🖥️ EC2 Instances:")
                for instance_id, instance_info in instances.items():
                    print(f"\n{instance_id}:")
                    for key, value in instance_info.items():
                        print(f"  {key}: {value}")
            else:
                print("\nNo EC2 instances found.")
        
        elif choice == "2":
            terminate_selected_instances()

        elif choice == "3":
            print("\n🔚 Exiting Excalisweep EC2 Wizard. Have a great day!")
            break
        
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    interactive_menu()
