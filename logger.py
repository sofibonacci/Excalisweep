import os
from datetime import datetime, timezone
import config

def log_action(service_name, resource_name, success, mode="deletion", function_name=None, json_input=None, response_json=None):
    log_file_path = "excalisweep.logs"
    
    # Ensure the file exists
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w") as f:
            pass
    
    # Format timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S (UTC +0)")
    
    # Determine status
    if mode in ["deletion", "request"]:
        if config.delete_for_real:
            if mode == "deletion":
                status = "SUCCESFULLY DELETED" if success else "DELETION FAILED"
            elif mode == "request":
                status = "SUCCESFULLY REQUESTED DELETION" if success else "FAILED REQUESTED DELETION"
            else:
                status = "UNKNOWN ACTION"
        else:
            status = "TESTING"
        log_entry = f"{timestamp} | {service_name} | {resource_name} | {status}\n"
    else:
        log_entry = f"{timestamp} | {service_name} | {resource_name} | {function_name} | {json_input} | {response_json}\n"
    
    # Write log entry
    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry)