Setting Up PostgreSQL Password for faa-aircraft-lookup

This document provides instructions for securely setting up the PostgreSQL password for the faa-aircraft-lookup app using an environment variable and a secure file.
Steps Overview

Create a hidden file to store the PostgreSQL password.
Secure the file by restricting its permissions.
Load the password into an environment variable (FAA_DB_PASSWORD) to be used by the app.
Configure the cron job (or similar) to use this process for secure password management.
Step 1: Create a Password File

You’ll store the PostgreSQL password in a file located in the config/ directory. This file will be hidden for extra security.
Navigate to the config/ directory inside the faa-aircraft-lookup root folder:
bash
Copy code
cd /path/to/faa-aircraft-lookup/config
Create a hidden file named .db_password to store the password:
bash
Copy code
touch .db_password
Edit the file and add your PostgreSQL password:
bash
Copy code
echo "your_secure_password_here" > .db_password
Step 2: Secure the Password File

To ensure the password file is secure, restrict the permissions so that only the owner can read it.
Set permissions to 600 (or 400 for read-only):
bash
Copy code
chmod 600 .db_password  # or chmod 400 .db_password for read-only
Ensure only the necessary user can access the file and confirm the permissions:
bash
Copy code
ls -l .db_password
# Output should be similar to: -rw------- 1 youruser yourgroup ... .db_password
Step 3: Load the Password into an Environment Variable

The app retrieves the PostgreSQL password from the FAA_DB_PASSWORD environment variable. You can load the password from the .db_password file into this variable before running the app.
Option 1: Manual Setup (for local development)
Load the password into the environment variable using this command:
bash
Copy code
export FAA_DB_PASSWORD=$(cat /path/to/faa-aircraft-lookup/config/.db_password)
Verify the environment variable is set:
bash
Copy code
echo $FAA_DB_PASSWORD  # Should print the password
Step 4: Configure the Cron Job

If you’re using a cron job to automate the faa_data_sync.py script, ensure the password is loaded as part of the cron job.
Edit your cron jobs using:
bash
Copy code
crontab -e
Add the following cron job, ensuring the password is loaded from the file:
bash
Copy code
0 */12 * * * export FAA_DB_PASSWORD=$(cat /var/bertain-cdn/faa-aircraft-lookup/config/.db_password) && /var/bertain-cdn/faa-aircraft-lookup/faa_data_sync.py
This will ensure that the password is set securely every time the cron job runs.
Step 5: Exclude the Password File from Version Control

To prevent accidental inclusion of the password file in version control, ensure that .db_password is listed in .gitignore.
Open (or create) a .gitignore file in the root of your project:
bash
Copy code
touch /path/to/faa-aircraft-lookup/.gitignore
Add the following line to exclude the .db_password file:
bash
Copy code
config/.db_password
Save and verify the password file is not being tracked:
bash
Copy code
git status
Security Considerations

File Permissions: Ensure that only the necessary user has access to the .db_password file by keeping permissions restricted (e.g., 600 or 400).
Do Not Hardcode Passwords: Avoid hardcoding the PostgreSQL password in code or scripts. Always use environment variables for secure password management.
Backup: Ensure that the .db_password file is backed up securely, but is not included in version control.
Conclusion

Following this setup, the PostgreSQL password for the faa-aircraft-lookup app will be managed securely, reducing the risk of exposure while maintaining flexibility for deployments. If you have further questions, feel free to refer to additional documentation or consult your system administrator.

