import boto3
import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import logger as l
import config as c

def list_s3_buckets():
    s3_client = boto3.client('s3')
    response = s3_client.list_buckets()
    
    buckets = {}
    for bucket in response.get('Buckets', []):
        bucket_name = bucket['Name']
        try:
            # Retrieve the bucket's tags (including description if it exists)
            tags_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
            description = None
            for tag in tags_response.get('TagSet', []):
                if tag['Key'].lower() == 'description':
                    description = tag['Value']
                    break
            
            # Check if the bucket contains objects to determine if it's active or inactive
            objects = s3_client.list_objects_v2(Bucket=bucket_name)
            is_active = "Active" if "Contents" in objects else "Inactive ❌"
            
        except Exception as e:
            description = f"Error retrieving description: {str(e)}"
            is_active = f"Error checking status: {str(e)}"
        
        buckets[bucket_name] = {
            'CreationDate': bucket['CreationDate'],
            'Status': is_active,
            'Description': description if description else "No description available"
        }
    
    return buckets

def empty_bucket(bucket_name):
    s3_client = boto3.client('s3')
    
    # Empty the bucket (delete objects)
    try:
        print(f"\nEmptying bucket: {bucket_name}...")
        # List objects in the bucket
        objects = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' in objects:
            # Delete all objects
            delete_objects = {'Objects': [{'Key': obj['Key']} for obj in objects['Contents']]}
            s3_client.delete_objects(Bucket=bucket_name, Delete=delete_objects)
            print(f"Successfully deleted objects from bucket: {bucket_name}")
        
        # If versioning is enabled, delete all versions
        versions = s3_client.list_object_versions(Bucket=bucket_name)
        if 'Versions' in versions:
            delete_versions = {'Objects': [{'Key': obj['Key'], 'VersionId': obj['VersionId']} for obj in versions['Versions']]}
            s3_client.delete_objects(Bucket=bucket_name, Delete=delete_versions)
            print(f"Successfully deleted versions from bucket: {bucket_name}")

    except Exception as e:
        print(f"Error emptying bucket {bucket_name}: {str(e)}")
        l.log_deletion_attempt(bucket_name, "S3", False)
        return False

    return True

def delete_selected_buckets():
    print("Waiting for buckets...")
    s3_client = boto3.client('s3')
    buckets = list_s3_buckets()

    if not buckets:
        print("\n⚠️ No S3 buckets found.")
        return

    print("\n🗑️ All S3 Buckets:")
    bucket_list = list(buckets.keys())
    for idx, bucket in enumerate(bucket_list, start=1):
        status = buckets[bucket]['Status']
        print(f"{idx}. {bucket} ({status})")

    print("\nEnter the numbers of the buckets you want to delete (comma-separated), or type 'all' to delete all:")
    choice = input("Your choice: ").strip().lower()

    if choice == "all":
        selected_buckets = bucket_list
    else:
        try:
            indices = [int(i.strip()) - 1 for i in choice.split(",")]
            selected_buckets = [bucket_list[i] for i in indices if 0 <= i < len(bucket_list)]
        except (ValueError, IndexError):
            print("\nInvalid selection. No buckets deleted.")
            return

    if not selected_buckets:
        print("\nNo valid buckets selected for deletion.")
        return

    confirm = input(f"\nAre you sure you want to delete these {len(selected_buckets)} bucket(s)? (yes/no): ").strip().lower()
    if confirm == "yes":
        for bucket in selected_buckets:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if c.config.delete_for_real:
                # Empty the bucket before deleting it
                if empty_bucket(bucket):
                    try:
                        s3_client.delete_bucket(Bucket=bucket)
                        print(f"Successfully deleted: {bucket}")
                    except Exception as e:
                        print(f"Failed to delete {bucket}: {str(e)}")
                        l.log_deletion_attempt(bucket, "S3", False)
                else:
                    print(f"Failed to empty bucket {bucket}. Skipping deletion.")
            else:
                l.log_deletion_attempt(bucket, "S3", True)
                print(f"Logged delete attempt for: {bucket}")
    else:
        print("Deletion canceled.")

def interactive_menu():
    print("""
    *****************************************
    *   Welcome to ExcaliSweep S3 Wizard!   *
    *   Your S3 Buckets Cleanup Assistant   *
    *****************************************
""")

    while True:
        print("\nMain Menu:")
        print("1. List S3 Buckets and Status")
        print("2. Delete Buckets")
        print("3. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            print("Waiting for buckets...")
            buckets = list_s3_buckets()
            if buckets:
                print("\n🪣 S3 Buckets:")
                for bucket_name, bucket_info in buckets.items():
                    print(f"\n{bucket_name}:")
                    for key, value in bucket_info.items():
                        print(f"  {key}: {value}")
            else:
                print("\nNo S3 buckets found.")
        
        elif choice == "2":
            delete_selected_buckets()

        elif choice == "3":
            print("\n🔚 Exiting Excalisweep S3 Wizard. Have a great day!")
            break
        
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    interactive_menu()
