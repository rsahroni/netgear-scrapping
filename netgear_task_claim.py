import time
import os
import sys
from getpass import getpass
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)
from webdriver_manager.chrome import ChromeDriverManager


def log_message(message, log_type="info", new_line_before=False):
    """Prints a message with a timestamp and log type indicator."""
    log_indicators = {
        "process": "[*]",
        "success": "[+]",
        "error": "[!]",
        "info": "[-]",  # Default/info indicator
    }
    indicator = log_indicators.get(log_type, "[?]")  # Fallback for unknown types

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if new_line_before:
        print()
    print(f"[{timestamp}] {indicator} {message}")


def countdown(seconds, message="Waiting"):
    """Displays a countdown timer in the console for the given duration."""
    for i in range(int(seconds), 0, -1):
        # Use \r to return to the beginning of the line and flush to ensure it's displayed immediately
        print(f"\r{message} for {i} more second(s)...", end="", flush=True)
        time.sleep(1)
    # Clear the countdown line after finishing
    print("\r" + " " * 70 + "\r", end="", flush=True)


def format_duration(seconds):
    """Converts seconds into a human-readable string (e.g., 2 minute(s) 15 second(s))."""
    if seconds < 0:
        return "0 seconds"

    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    parts = (
        [f"{h} hour(s)" for h in [hours] if h > 0]
        + [f"{m} minute(s)" for m in [minutes] if m > 0]
        + [f"{s} second(s)" for s in [seconds] if s >= 0]
    )
    return " ".join(parts) if parts else "0 seconds"


def get_credentials():
    """Handles getting username and password from the user, reading a saved username if available."""
    log_message("Please enter your login credentials.", "process", new_line_before=True)
    CREDENTIALS_FILE = "credentials.dat"
    saved_username = None

    # Check if a credentials file exists
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            saved_username = f.read().strip()

    username = ""
    if saved_username:
        use_saved = input(f"Use saved username '{saved_username}'? (Y/n): ")
        if use_saved:
            use_saved = use_saved.lower().strip()
        else:
            raise Exception("Interrupted by user.")
        if use_saved in ["", "y", "yes"]:
            username = saved_username
            log_message(f"Using username: {username}", "info")
        else:
            username = input("Enter new username: ").strip()
    else:
        username = input("Enter username: ").strip()

    password = getpass("Enter password: ")
    return username, password


# --- Configuration ---
# Login Page URL
LOGIN_URL = "https://geotagging.indosatooredoo.com/"
INSURANCE_URL = "https://geotagging.indosatooredoo.com/astweb/ast_insurance_main.php"

# --- Main Execution ---
print("=" * 50)
print(" " * 15 + "Task Claim Downloader")
print(" " * 18 + "by Rahmat Sahroni")
print("=" * 50)

driver = None
try:
    # Determine if the browser should be shown based on command-line arguments
    # Use --show-browser when running the script to make the browser visible.
    show_browser = "--show-browser" in sys.argv

    # Get credentials from user input
    USERNAME, PASSWORD = get_credentials()

    # --- Browser setup is moved here, after getting credentials ---
    log_message("Setting up WebDriver...", "process", new_line_before=True)

    # Set a custom cache path for webdriver-manager
    # This will store the downloaded chromedriver inside a 'driver_cache' folder
    # within your project directory, instead of the default user home directory.
    driver_cache_path = os.path.join(os.path.dirname(__file__), "driver_cache")
    os.environ["WDM_LOCAL"] = driver_cache_path
    log_message(f"WebDriver-Manager cache path set to: {driver_cache_path}", "info")
    log_message("Installing/Checking for compatible Chrome driver...", "process")

    # Configure Chrome options
    chrome_options = webdriver.ChromeOptions()
    if not show_browser:
        log_message("Running in headless mode (browser window is hidden).", "info")
        chrome_options.add_argument("--headless")  # This enables headless mode
        chrome_options.add_argument("--window-size=1920,1080")  # Set a window size
        chrome_options.add_argument("--disable-gpu")  # Often recommended for headless
    else:
        log_message("Running with a visible browser window.", "info")
        chrome_options.add_argument("--start-maximized")

    # This will automatically download and set up the appropriate chromedriver
    # The cache path is already set via os.environ["WDM_LOCAL"].
    # This ensures webdriver-manager uses the specified directory and avoids conflicts.
    log_message("Initializing Chrome browser service...", "process")
    try:
        service = Service(ChromeDriverManager().install())
    except Exception as e:
        log_message(f"Automatic driver download failed: {e}", "error")
        log_message("Attempting to use local 'chromedriver.exe'...", "process")
        local_driver_path = os.path.join(os.path.dirname(__file__), "chromedriver.exe")
        if os.path.exists(local_driver_path):
            service = Service(executable_path=local_driver_path)
            log_message(f"Using local driver: {local_driver_path}", "success")
        else:
            raise Exception(
                "Automatic download failed and local 'chromedriver.exe' not found."
            )

    driver = webdriver.Chrome(service=service, options=chrome_options)
    log_message(
        "WebDriver setup complete. Browser is running in the background.", "success"
    )

    start_time = time.monotonic()
    log_message(f"Navigating to {LOGIN_URL}", "process", new_line_before=True)
    # driver.maximize_window() # This is not needed and can cause errors in headless mode
    driver.get(LOGIN_URL)

    # Wait until the login page is fully loaded (waiting for the username element to appear)
    # Timeout is set to 10 seconds
    wait_short = WebDriverWait(driver, 20)
    wait_long = WebDriverWait(driver, 180)

    username_field = wait_short.until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    log_message("Login page loaded. Finding login elements...", "process")

    # Find the password and login button elements
    password_field = driver.find_element(By.NAME, "password")
    login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")

    log_message("Entering credentials...", "process")
    username_field.send_keys(USERNAME)
    time.sleep(0.5)
    password_field.send_keys(PASSWORD)
    time.sleep(0.5)

    log_message("Clicking login button...", "process")
    login_button.click()

    try:
        # Wait for the main page (dashboard) to load after login
        # We use the search input with id 'searchInput' as an indicator of success
        log_message("Waiting for login verification...", "process")
        wait_short.until(EC.presence_of_element_located((By.ID, "searchInput")))
        log_message("Login successful!", "success")

        # Save the username only after a successful login
        CREDENTIALS_FILE = "credentials.dat"
        with open(CREDENTIALS_FILE, "w") as f:
            f.write(USERNAME)
        log_message(
            f"Successfully logged in. Username '{USERNAME}' saved for future use.",
            "info",
        )
    except TimeoutException:
        log_message("LOGIN FAILED", "error", new_line_before=True)
        log_message(
            "Could not find the main page after login. Please check if your username and password are correct.",
            "error",
        )
        # Exit the script gracefully as we cannot continue
        raise Exception("Invalid credentials or login issue.")

    log_message("Navigating to insurance page...", "process", new_line_before=True)
    driver.get(INSURANCE_URL)
    wait_short.until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[@id='tbl_doc_list']/tbody/tr/td")
        )
    )
    log_message("Insurance page loaded.", "process")

    # Define the list of date ranges you want to download
    date_ranges_to_process = [
        {"start": "", "end": "2023-01-01"},
        {"start": "2023-01-01", "end": "2024-01-01"},
        {"start": "2024-01-01", "end": "2025-01-01"},
        {"start": "2025-01-01", "end": "2025-07-01"},
        {"start": "2025-07-01", "end": "2026-01-01"},
        {"start": "2026-01-01", "end": ""},
    ]

    # Loop through each date range and perform the download
    i: int = 1
    for date_range in date_ranges_to_process:
        start_date = date_range["start"]
        end_date = date_range["end"]

        # Create a more descriptive log message for the date range
        log_start_date = start_date if start_date else "the beginning"
        log_end_date = end_date if end_date else "today"

        log_message(
            f"Processing date range: from {log_start_date} to {log_end_date} ({i} of {len(date_ranges_to_process)})",
            "process",
            new_line_before=True,
        )

        countdown(5, "Pausing before opening filter")
        advance_filter_button = wait_short.until(
            EC.element_to_be_clickable((By.ID, "btn-task-filter"))
        )
        advance_filter_button.click()
        wait_short.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@id='filterModal']/div/div/div[1]/h4")
            )
        )
        log_message("Advanced filter opened.", "process")

        countdown(10, "Pausing before filling dates")
        start_date_field = wait_short.until(
            EC.presence_of_element_located((By.ID, "filter_form-event_start_date"))
        )
        end_date_field = wait_short.until(
            EC.presence_of_element_located((By.ID, "filter_form-event_end_date"))
        )

        start_date_field.clear()
        start_date_field.send_keys(start_date)

        end_date_field.clear()
        end_date_field.send_keys(end_date)

        countdown(2, "Pausing before applying filter")
        apply_filter_button = wait_short.until(
            EC.element_to_be_clickable((By.ID, "filter_form-apply"))
        )
        apply_filter_button.click()
        wait_short.until(
            EC.invisibility_of_element_located(
                (By.XPATH, "//*[@id='tbl_doc_list_processing']/div")
            )
        )

        total_entries = 0
        # Parse the total number of entries from the info element
        try:
            info_element = wait_short.until(
                EC.visibility_of_element_located((By.ID, "tbl_doc_list_info"))
            )
            info_text = info_element.text  # e.g., "Showing 1 to 10 of 6,209 entries"

            parts = info_text.split()
            if "of" in parts and "entries" in parts:
                # The number is usually the word before "entries"
                total_entries_str = parts[parts.index("entries") - 1]
                total_entries = int(total_entries_str.replace(",", ""))
            elif "No matching records found" in info_text:
                total_entries = 0
        except TimeoutException:
            log_message(
                "Could not find the table info element to get total entries.", "error"
            )

        log_message(
            f"Filter applied. Found {total_entries:,} entries for range {log_start_date} to {log_end_date}.",
            "info",
        )

        if total_entries > 0:
            log_message("Initiating data export...", "process")
            export_button = wait_short.until(
                EC.element_to_be_clickable((By.ID, "btn-task-export"))
            )
            export_button.click()
            # Wait for the radio button to be clickable, which is more reliable than a fixed sleep
            all_pages_option = wait_short.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//*[@id='export_form']/div[1]/div/div[2]/label")
                )
            )
            all_pages_option.click()
            export_task_item_option = wait_short.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//*[@id='export_form']/div[2]/div/div[2]/label")
                )
            )
            export_task_item_option.click()
            export_submit_button = wait_short.until(
                EC.element_to_be_clickable((By.ID, "export_form-submit"))
            )

            # Store the handle of the original window
            original_window = driver.current_window_handle

            export_submit_button.click()

            # Wait for the new window/tab to open
            log_message("Waiting for the download process window to open...", "process")
            wait_long.until(EC.number_of_windows_to_be(2))

            # Wait for the download window to close automatically, which means the download has started/completed
            log_message(
                "Download in progress, waiting for the process window to close...",
                "process",
            )
            wait_long.until(EC.number_of_windows_to_be(1))

            # Switch back to the original window
            driver.switch_to.window(original_window)
            log_message(
                f"Download for range {log_start_date} to {log_end_date} finished.",
                "success",
            )

            # Add a countdown to ensure the file is fully written to disk before the next loop
            countdown(10, "Waiting for file to be written to disk")

        else:
            log_message("Skipping download because no entries were found.", "info")

        i += 1

except TimeoutException:
    log_message(
        "Timeout occurred while waiting for a page element.",
        "error",
        new_line_before=True,
    )
    log_message("Please check your internet connection and try again.", "error")
except NoSuchElementException as e:
    log_message(
        f"An expected element was not found: {e}", "error", new_line_before=True
    )
    log_message(
        "The website structure may have changed. Please review the script.", "error"
    )
except ElementClickInterceptedException as e:
    log_message(f"\n[!] Could not click on an element: {e}")
    log_message(
        "[!] The element might be covered by another element or not interactable."
    )
except ElementNotInteractableException as e:
    log_message(f"\n[!] An element was not interactable: {e}")
    log_message("[!] The element might be hidden or disabled.")
except Exception as e:
    log_message(f"An error occurred: {e}", "error", new_line_before=True)
    log_message(
        "Make sure your credentials are correct and your internet connection is stable.",
        "error",
    )

finally:
    # Calculate total execution time
    total_duration_str = ""
    if "start_time" in locals():
        end_time = time.monotonic()
        duration_seconds = end_time - start_time
        total_duration_str = format_duration(duration_seconds)

    # Let the browser stay open for inspection
    log_message(
        f"Script finished in {total_duration_str}. Press Enter in this terminal to close the browser.",
        "info",
        new_line_before=True,
    )
    input()
    if driver:
        driver.quit()
    log_message("Browser closed.", "info")
