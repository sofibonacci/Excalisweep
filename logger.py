def log_deletion_attempt(service_name, timestamp):
    with open("logs.txt", "a") as log_file:  # Logs go to logs.txt
        log_file.write(f"{timestamp} - Attempted deletion: {service_name}\n")