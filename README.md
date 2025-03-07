VPSMigrator
===========

VPSMigrator is a Python script designed to automate the migration of server setups 
from one Virtual Private Server (VPS) to another. It simplifies the transfer of 
installed packages, web services, and key directories. This tool is ideal for 
moving web applications such as WordPress or custom Go-based projects.

Table of Contents
-----------------
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Example Configuration](#example-configuration)
5. [How It Works](#how-it-works)
6. [Troubleshooting](#troubleshooting)
7. [Contributing](#contributing)
8. [License](#license)

Prerequisites
-------------
Before using VPSMigrator, ensure you have:

- Python 3.x installed on your local machine.
- The "paramiko" and "requests" Python libraries. Install them with:
  
      pip install paramiko requests

- Root access to both the source (old) and destination (new) VPS.
- SSH access to both VPS instances, supporting either password-based or key-based authentication.

Installation
------------
Clone the repository from GitHub using your username, "ayroop":

      git clone https://github.com/ayroop/VPSMigrator.git

Then, navigate to the project directory:

      cd VPSMigrator



Usage
-----
1. Open "vps_migrator.py" and configure the OLD_VPS and NEW_VPS dictionaries with your server details.
2. For password-based authentication, leave "key_filename" blank; the script will prompt for passwords.
   For key-based authentication, specify the full path to your private key.
3. Optionally, update the custom_directories list with additional directories to migrate.
4. Run the script:

      python vps_migrator.py

5. Follow the on-screen prompts to complete the migration.

Example Configuration
---------------------
Below is an example configuration snippet to update in "vps_migrator.py":

      OLD_VPS = {
          "host": "192.168.1.100",      # IP address of the old VPS
          "user": "root",               # SSH username
          "port": 2211,                 # SSH port (default: 22)
          "key_filename": "/path/to/old_vps_key"  # Optional: path to the private key
      }

      NEW_VPS = {
          "host": "192.168.1.101",      # IP address of the new VPS
          "user": "root",               # SSH username
          "port": 22,                   # SSH port (default: 22)
          "key_filename": "/path/to/new_vps_key"  # Optional: path to the private key
      }

      custom_directories = ["/var/www/html", "/opt/myapp"]  # Additional directories to migrate

How It Works
------------
VPSMigrator automates the migration process as follows:

- Package Detection: Identifies installed packages on the old VPS using "dpkg".
- Service Detection: Detects running web services (e.g., Nginx, Apache, PHP, MySQL) using "systemctl".
- Directory Detection: Identifies common web directories such as "/var/www" or "/etc/nginx".
- File Transfer: Archives directories with "tar" and transfers them using "scp".
- Package Installation: Installs detected packages on the new VPS using "apt".
- Service Restart: Restarts the detected services on the new VPS.
- Validation (Optional): Checks if the migrated web application is accessible.

Troubleshooting
---------------
- SSH Authentication Fails: Verify SSH access manually by running "ssh root@<host>" 
  and ensure your credentials or key settings are correct.
- Package Installation Errors: Confirm that both VPS instances run compatible Ubuntu 
  versions; some packages might differ.
- File Transfer Issues: Check that the directories exist on the old VPS and that the 
  new VPS has sufficient disk space.
- Service Restart Problems: Use "systemctl status <service>" on the new VPS to diagnose 
  issues and review logs.

Contributing
------------
We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new branch for your changes:

       git checkout -b feature-or-bugfix-name

3. Commit your changes with descriptive messages.
4. Push to your fork and submit a pull request.

For detailed guidelines, see the CONTRIBUTING.md file.

License
-------
This project is licensed under the MIT License.

NOTE:
-----
Always back up your data before migrating. Test the script in a staging environment 
to ensure it works with your setup.
