def log_deletion_attempt(service_name, timestamp):
    with open("logger.py", "a") as log_file:
        log_file.write(f"# Attempted deletion: {service_name} at {timestamp}\n")
