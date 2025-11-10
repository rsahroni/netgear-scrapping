from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
)
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webelement import WebElement
from dotenv import load_dotenv

from getpass import getpass
from pathlib import Path
import datetime
import time
import os
import xlsxwriter as xlsw

load_dotenv()
url = str(os.getenv("URL"))
user_id = os.getenv("USRID")
password = os.getenv("PWD")
wait_timeout = os.getenv("WAIT_TIMEOUT")

user_id = input("User ID: ")
password = getpass()

basedir = Path.cwd()
inputdir = basedir.joinpath("input")
outputdir = basedir.joinpath("output")
input_file_path = inputdir.joinpath("taskid_list.csv")

input_file = open(input_file_path, "r")
taskid_list = input_file.read().splitlines()
taskid_list.pop(0)
input_file.close()

file_date = datetime.datetime.now().strftime("%Y%m%d%H%M")
new_filename = f"CLM-LST-{file_date}-{len(taskid_list)}.xlsx"
new_dirname = f"CLM-LST-{file_date}-{len(taskid_list)}"
new_filename_path = outputdir.joinpath(new_filename)
new_dirname_path = outputdir.joinpath(new_dirname)

if not new_dirname_path.exists():
    new_dirname_path.mkdir()

wb = xlsw.Workbook(new_filename_path)
ws = wb.add_worksheet("Claim List")

wb.set_properties(
    {
        "title": "Output from Python Selenium Netgear Scrapping",
        "subject": "IOH Internal Use Only",
        "author": "Rahmat Hidayat Sahroni",
        "company": "Indosat Ooredoo Hutchison",
        "category": "Output File",
        "keywords": "Task ID, Task Claim, Insurance Claim",
        "created": datetime.date.today(),
        "comments": "Created with Python and XlsxWriter by Rahmat Sahroni",
    }
)

# Set header table
header_table = (
    "No.",
    "Task ID",
    "Claim Status",
    "Claim Number",
    "Region",
    "Area",
    "Site ID",
    "Site Name",
    "Cause of Loss",
    "Date of Loss",
    "Item Description",
    "Brand",
    "Item Code",
    "UoM",
    "Quantity",
    "Serial No.",
    "Currency",
    "Unit Price",
    "Total Price",
)
row = 0
col = 0
for header in header_table:
    ws.write(row, col, header)
    col += 1

options = webdriver.ChromeOptions()
options.add_experimental_option(
    "prefs",
    {
        "download.default_directory": f"{new_dirname_path}",  # Change default directory for downloads
        "download.prompt_for_download": False,  # To auto download the file
        "plugins.always_open_pdf_externally": True,  # It will not show PDF directly in chrome
        "profile.default_content_settings.popups": 0,
    },
)
drv = webdriver.Chrome(options=options)
drv.maximize_window()
drv.get(url)
print(f"Accessing: {drv.current_url}")
drv_wait = WebDriverWait(driver=drv, timeout=60)

frm_welcome = drv_wait.until(EC.presence_of_element_located((By.ID, "form-signin")))
# login
print("Login with User ID: {}".format(user_id))
print(f"Processing {len(taskid_list)} insurance claim TASK ID:")
lbl_notif = drv.find_element(By.XPATH, "//h3[@class='form-signin-heading']")
txt_username = drv.find_element(By.XPATH, "//input[@id='inputEmail']")
txt_password = drv.find_element(By.XPATH, "//input[@id='inputPassword']")

txt_username.clear()
txt_username.send_keys(user_id)
txt_password.clear()
txt_password.send_keys(password)
txt_password.send_keys(Keys.RETURN)
# choose Claim Management menu
lnk_insurance_claim = drv_wait.until(
    EC.presence_of_element_located((By.LINK_TEXT, "Claim Management"))
)
lnk_insurance_claim.send_keys(Keys.RETURN)

# Claim Management menu -> filter using TASK ID
tsk_no = 1
row = 1
for tsk in taskid_list:
    print(f"{tsk_no}. {tsk}")
    btn_reset_filter = drv_wait.until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='filter-reset-btn']"))
    )
    txt_task_id = drv.find_element(By.XPATH, "//input[@id='doc-task_id']")
    cmb_status = drv.find_element(By.XPATH, "//select[@id='doc-status']")
    btn_search = drv.find_element(By.XPATH, "//a[@id='search-btn']")
    txt_task_id.clear()
    txt_task_id.send_keys(tsk)
    opt_status = cmb_status.find_elements(By.TAG_NAME, "option")
    time.sleep(2)
    for opt_item in opt_status:
        if opt_item.text == "ANY STATUS":
            opt_item.click()
            break
    # search the insurance claim
    btn_search.click()
    try:
        btn_view_detail = drv_wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"//*[@id='{tsk}']/td[9]/button[1]",
                )
            )
        )
        btn_view_detail.click()
    except TimeoutException:
        wb.close()
        drv.close()
        exit()

    lbl_detail_report = drv_wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[2]/div[2]/div[1]/div/div[1]/h4")
        )
    )
    lbl_task_id = drv.find_element(
        By.XPATH,
        "/html/body/div[2]/div[2]/div[2]/form/div/div/div[1]/div[1]/div[1]/p/span",
    )
    lbl_status_claim = drv.find_element(
        By.XPATH,
        "/html/body/div[2]/div[2]/div[2]/form/div/div/div[1]/div[1]/div[2]/p/span",
    )
    txt_claim_number = drv.find_element(
        By.XPATH,
        "/html/body/div[2]/div[2]/div[2]/form/div/div/div[1]/div[1]/div[3]/p/input",
    )
    lbl_region = drv.find_element(
        By.XPATH,
        "/html/body/div[2]/div[2]/div[2]/form/div/div/div[1]/div[2]/div/p/span",
    )
    lbl_site_id = drv.find_element(
        By.XPATH,
        "/html/body/div[2]/div[2]/div[2]/form/div/div/div[3]/div[2]/div[2]/p/span",
    )
    lbl_site_name = drv.find_element(
        By.XPATH,
        "/html/body/div[2]/div[2]/div[2]/form/div/div/div[3]/div[4]/div[2]/input",
    )
    lbl_area = drv.find_element(
        By.XPATH,
        "/html/body/div[2]/div[2]/div[2]/form/div/div/div[3]/div[5]/div[2]/p/span",
    )
    cmb_cause_loss = Select(
        drv.find_element(
            By.XPATH,
            "/html/body/div[2]/div[2]/div[2]/form/div/div/div[5]/div[1]/div[2]/select",
        )
    )
    lbl_event_date = drv.find_element(By.XPATH, '//*[@id="detail_form-event_date"]')
    time.sleep(2)
    tbl_item_list = drv.find_element(
        By.XPATH,
        "/html/body/div[2]/div[2]/div[2]/form/div/div/div[13]/div/div/table/tbody",
    )
    ws.write(row, 0, tsk_no)
    for tr_item in tbl_item_list.find_elements(By.TAG_NAME, "tr"):
        col = 1
        i = 1
        ws.write(row, col, lbl_task_id.text)
        ws.write(row, col + 1, lbl_status_claim.text)
        ws.write(row, col + 2, txt_claim_number.get_attribute("value"))
        ws.write(row, col + 3, lbl_region.text)
        ws.write(row, col + 4, lbl_area.text)
        ws.write(row, col + 5, lbl_site_id.text)
        ws.write(row, col + 6, lbl_site_name.get_attribute("value"))
        ws.write(row, col + 7, cmb_cause_loss.first_selected_option.text)
        ws.write(row, col + 8, lbl_event_date.get_attribute("value"))
        col += 9
        try:
            td_items = tr_item.find_elements(By.TAG_NAME, "td")
        except NoSuchElementException:
            print("Retry collect table..")
            time.sleep(5)
            td_items = tr_item.find_elements(By.TAG_NAME, "td")

        for td_item in td_items:
            txt_item = str()
            try:
                spn_item = td_item.find_element(By.TAG_NAME, "span")
                txt_item = str(spn_item.text)
            except NoSuchElementException:
                txt_item = str(td_item.text)
            except StaleElementReferenceException:
                print("Retry collect detail..")
                spn_item = td_item.find_element(By.TAG_NAME, "span")
                txt_item = str(spn_item.text)

            if i > 1:
                if i == 6:
                    txt_item = int(txt_item)
                elif i == 9 or i == 10:
                    txt_item = float(txt_item.replace(".", ""))
                ws.write(row, col, txt_item)
                col += 1
            i += 1
        row += 1
    tsk_no += 1

print(f"Save result to: {new_filename_path}")
wb.close()
# # logout
drv.quit()
print("Done")
