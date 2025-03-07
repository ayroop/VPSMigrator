import paramiko
import time
import os
import requests
import getpass

# SSH Configuration
OLD_VPS = {
    "host": "OLD_SERVER_IP",  # Replace with your old VPS IP
    "user": "root",
    "port": 2211              # Custom SSH port for old VPS
}

NEW_VPS = {
    "host": "NEW_SERVER_IP",  # Replace with your new VPS IP
    "user": "root",
    "port": 22                # Default SSH port for new VPS (adjust if different)
}

def ssh_connect(server, password):
    """Establish an SSH connection using a password."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())  # Warns about unknown hosts
    client.connect(server["host"], username=server["user"], password=password, port=server["port"])
    return client

def run_command(client, command):
    """Execute a command on the remote server and return output."""
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    if error:
        raise Exception(f"Command '{command}' failed: {error}")
    return output

def detect_installed_packages(old_client):
    """Detect installed packages on the old VPS."""
    print("Detecting installed packages...")
    package_list = run_command(old_client, "dpkg --get-selections | awk '{print $1}'")
    return [pkg for pkg in package_list.split("\n") if pkg]

def detect_web_services(old_client):
    """Detect running web services on the old VPS."""
    print("Detecting running web services...")
    services = run_command(old_client, "systemctl list-units --type=service --state=running | grep -E 'nginx|apache|php|mysql|mariadb' | awk '{print $1}'")
    return [svc for svc in services.split("\n") if svc]

def detect_directories(old_client):
    """Detect common web directories on the old VPS."""
    print("Detecting important directories...")
    common_dirs = ["/var/www", "/etc/nginx", "/etc/apache2", "/etc/php", "/etc/mysql", "/etc/letsencrypt"]
    existing_dirs = []
    for directory in common_dirs:
        output = run_command(old_client, f"if [ -d {directory} ]; then echo {directory}; fi")
        if output.strip():
            existing_dirs.append(directory)
    return existing_dirs

def transfer_files(old_client, new_client, directories):
    """Transfer files from old VPS to new VPS."""
    for directory in directories:
        print(f"Transferring {directory}...")
        tar_filename = f"/tmp/migrate_{directory.replace('/', '_')}.tar.gz"
        run_command(old_client, f"tar -czf {tar_filename} {directory}")
        # Use the custom port for SCP from old VPS
        run_command(old_client, f"scp -P {OLD_VPS['port']} {tar_filename} {NEW_VPS['user']}@{NEW_VPS['host']}:/tmp/")
        run_command(new_client, f"tar -xzf {tar_filename} -C / && rm {tar_filename}")
        run_command(old_client, f"rm {tar_filename}")

def install_packages(new_client, packages):
    """Install detected packages on the new VPS."""
    if packages:
        print("Installing detected packages...")
        package_list = " ".join(packages)
        run_command(new_client, f"apt update && apt install -y {package_list}")
    else:
        print("No packages to install.")

def restart_services(new_client, services):
    """Restart detected services on the new VPS."""
    if services:
        print("Restarting services...")
        for service in services:
            run_command(new_client, f"systemctl restart {service}")
    else:
        print("No services to restart.")

def check_web_application(new_vps_host):
    """Check if the web application is accessible on the new VPS."""
    print("Checking web application accessibility...")
    try:
        response = requests.get(f"http://{new_vps_host}", timeout=10)
        if response.status_code == 200:
            print("Web application is accessible!")
        else:
            print(f"Warning: Web application returned status code {response.status_code}.")
    except requests.exceptions.RequestException as e:
        print(f"Error accessing web application: {e}")

def migrate_server(custom_dirs=None):
    """Main function to orchestrate the migration."""
    # Prompt for passwords securely
    old_password = getpass.getpass(f"Enter root password for old VPS ({OLD_VPS['host']}:{OLD_VPS['port']}): ")
    new_password = getpass.getpass(f"Enter root password for new VPS ({NEW_VPS['host']}:{NEW_VPS['port']}): ")

    old_client = None
    new_client = None
    try:
        # Connect to both servers
        old_client = ssh_connect(OLD_VPS, old_password)
        new_client = ssh_connect(NEW_VPS, new_password)

        print("Starting automated migration...")

        # Detect configurations
        packages = detect_installed_packages(old_client)
        services = detect_web_services(old_client)
        directories = detect_directories(old_client)
        if custom_dirs:
            directories.extend([d for d in custom_dirs if d not in directories])

        # Transfer files
        transfer_files(old_client, new_client, directories)

        # Install packages
        install_packages(new_client, packages)

        # Restart services
        restart_services(new_client, services)

        # Validate web application
        check_web_application(NEW_VPS["host"])

        print("Migration completed successfully! Update your domain's IP to the new VPS.")

    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        if old_client:
            old_client.close()
        if new_client:
            new_client.close()

if __name__ == "__main__":
    # Add custom directories if needed (e.g., for WordPress or Go app)
    custom_directories = ["/var/www/html", "/path/to/go/app"]
    migrate_server(custom_dirs=custom_directories)
