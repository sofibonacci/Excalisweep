# 🗡️ Welcome to Excalisweep 🧹

## What is ExcaliSweep?  
It's a Python tool designed to automatically delete the content and instances of AWS Services. Instead of going to the webpage of each one and deleting them manually, you can run ExcaliSweep in CloudShell and it will take you through a wizard to list and delete interactively. 

For commonly used services, Excalisweep provides dedicated wizards. If you need to manage a service not listed, you can use the **Other Services Wizard**, where you can select any AWS service and send custom requests to the Boto3 API by inputting a JSON payload directly.

Excalisweep also includes:

- Automated logging: Every deletion attempt is recorded on a separate file.

- Cost tracking: The main menu features a dashboard displaying services that are actively incurring costs, with an adjustable time frame.

- Testing mode: Run ExcaliSweep in a safe mode to simulate deletions before executing them, ideal for debugging or verification.

## Details
Every AWS Service (S3, EC2, etc) has its own deletion process (e.g., different boto3 functions to see which ones are active and delete them), so generalizing is difficult and we've created one separated script for each one of them. For now, we're focusing on the ones that we see on the Sandboxes we have access to, which are used for DeepRacer training:
- S3
- EC2
- Cloud Formation
- Lambda
- Other Services -> here you'll have all the AWS services available to interact with, and have to input a JSON for the function you want to excecute (you'll be sending API calls yourself)

## How to use: 
Clone the repo and run the wizard in CloudShell within the AWS Sandbox you desire to manage.

## Logs:
When an action is performed it's logged to excalisweep.logs, a file unique to each user -added to .gitignore-. A log entry should look like this:
```bash
2025-02-18 14:00:03 (UTC +0) | S3 Bucket | {bucket_name} | SUCCESSFULLY DELETED/DELETION FAILED/TESTING
```
