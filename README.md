# 🗡️ Welcome to Excalisweep v.1.0 🧹

## What is ExcaliSweep?

It's a Python tool designed to automatically delete the content and instances of AWS Services. Instead of going to the webpage of each one and deleting them manually, you can run ExcaliSweep in CloudShell and it will take you through a wizard to list and delete interactively.

For commonly used services, Excalisweep provides dedicated wizards. If you need to manage a service not listed, you can use the **Other Services Wizard**, where you can select any AWS service and send custom requests to the Boto3 API by inputting a JSON payload directly.

Excalisweep also includes:

- Automated logging: Every deletion attempt is recorded on a separate file.

- Cost tracking: The main menu features a dashboard displaying services that are actively incurring costs, with an adjustable time frame.

- Testing mode: Run ExcaliSweep in a safe mode to simulate deletions before executing them, ideal for debugging or verification.

## Starting ExcaliSweep

To begin, clone the repo in CloudShell within the AWS Sandbox you desire to manage and run

```bash
bash excalisweep.sh
```

This launches ExcaliSweep, displaying the main menu:

```
executing ExcaliSweep...

****************************************
*     Welcome to ExcaliSweep v.1.0!    *
*   Your AWS Cleanup Wizard Assistant  *
****************************************

Warning: The resources displayed are based on your current Availability Zone (AZ) and Region.
If you're unable to find what you're looking for, try switching to a different AZ or Region.
📍 Region: us-east-1
🏠 Availability Zone: us-east-1b

Currently, deletion mode is set to True
If you'd like to change it, go to option Change Mode

Options:
  1. Show billed AWS services
  2. Run S3 Cleanup Wizard
  3. Run CloudFormation Cleanup Wizard
  4. Run Other Services Cleanup Wizard
  5. Run EC2 Cleanup Wizard
  6. Run Lambda Cleanup Wizard
  7. View logs
  8. Change mode
  9. Exit
Select an option: 
```

## Example deleting an S3 Bucket

From the main menu, we choose option `2` to start the S3 Cleanup Wizard and we get:
```
Running s3_wizard...

*****************************************
*   Welcome to ExcaliSweep S3 Wizard!   *
*   Your S3 Buckets Cleanup Assistant   *
*****************************************

Main Menu:
1. List S3 Buckets and Status
2. Delete Buckets
3. Exit
Enter your choice: 
```

### Step 2: Choose to Delete Buckets

Select option `2` to proceed with deleting buckets and the tool will list all S3 buckets in your current region:

```
Waiting for buckets...

🗑️ All S3 Buckets:
1. excalisweet-bucket (Active)
```
Now we'll select the bucket to delete, and confirm the deletion

```
Enter the numbers of the buckets you want to delete (comma-separated), type 'all' to delete all, or 'exit' to cancel: 1
Are you sure you want to delete these 1 bucket(s)? (yes/no/exit): yes 
```

Finally, the tool empties and deletes the bucket, showing:

```
Emptying bucket: excalisweet-bucket...
✅ Successfully deleted: excalisweet-bucket
```

## Testing Mode

ExcaliSweep supports a testing mode where deletions are simulated and logged without actually deleting resources. To enable testing mode:

From the main menu, select option `8` (Change mode)

```
Choose a mode: press 'r' for real deletion of instances, or 't' for testing only: t
Testing mode activated.
Currently, deletion mode is set to False
```

If you were to do the S3 bucket deletion process same as before but in testing mode, the output will be:

```
📝 Logged delete attempt for: excalisweet-bucket
```

## Logs

To review actions taken by ExcaliSweep, go to main menu and select option View logs.
The logs display actions, including testing, successful and failed deletions. This is a file unique to each user.

```
--- Logs ---
2025-05-26 22:21:50 (UTC +0) | S3 | excalisweet-bucket | TESTING
2025-05-26 22:22:54 (UTC +0) | S3 | excalisweet-bucket | SUCCESFULLY DELETED
```
## Details

Every AWS Service (S3, EC2, etc) has its own deletion process (e.g., different boto3 functions to see which ones are active and delete them), so generalizing is difficult and we've created one separated script for each one of them. For now, we're focusing on the ones that we see on the Sandboxes we have access to:

- S3
- EC2
- Cloud Formation
- Lambda
- Other Services -> A Python CLI tool to explore and interact with AWS services using **Boto3**. Ideal for listing services, discovering methods (especially those for listing or deletion), and executing them with parameter support.

  **Features**

  - List all available AWS services
  - View methods for a selected service (filtered for `list`, `delete`, `terminate`, etc.)
  - Shows:
    - Method description
    - Required parameters
    - Example response syntax
  - Prompt for JSON-formatted input when parameters are required
  - Logs delete attempts or executions based on config


## Credits

This tool was developed by:

- Sofía Gurruchaga - Team Lead and Developer 
- Lourdes Micaela Suarez - Developer  
- Martina Toffoletto - Developer

