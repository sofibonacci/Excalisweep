# 🗡️ Welcome to Excalisweep 🧹
## What this app (tries to) do:
- Show the services that are actively incurring costs
- List them individually, so you can choose which ones to delete
- Log the attempted/succesful/failed actions

## Currently working on...
Every AWS Service (S3, EC2, etc) has its own deletion process (e.g., different boto3 functions to see which ones are active and delete them), so generalizing is difficult. For now, we're focusing on the ones that we see on the Sandboxes we have access to, which are used for DeepRacer training.

## How to use: 
Run the wizard in CloudShell within the AWS Sandbox you desire to manage.

## Logs:
When an action is performed it's logged to excalisweep.logs, a file unique to each user -added to .gitignore just in case-. A log entry should look like this:
```bash
2025-02-18 14:00:03 (UTC +0) | S3 Bucket | {bucket_name} | SUCCESSFUL
```
