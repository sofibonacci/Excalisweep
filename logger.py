import os
from datetime import datetime, timezone
import config

def log_deletion_attempt(service_name, resource_name, success):
    log_file_path = "excalisweep.logs"
    
    # Ensure the file exists
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w") as f:
            pass
    
    # Format timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S (UTC +0)")
    
    # Determine status
    if config.delete_for_real:
        status = "SUCCESSFUL" if success else "FAILED"
    else:
        status = "TESTING"
    
    # Write log entry
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{timestamp} | {service_name} | {resource_name} | {status}\n")
