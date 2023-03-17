from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from dotenv import load_dotenv

import time
import os

load_dotenv()
url = str(os.getenv('URL'))
user_id = os.getenv('USRID')
password = os.getenv('PWD')

drv = webdriver.Chrome()
drv.implicitly_wait(60)
drv.get(url)
print("url: {}".format(drv.current_url))
time.sleep(3)
# login
print("login")
lbl_notif = drv.find_element(By.XPATH, "//h3[@class='form-signin-heading']")
txt_username = drv.find_element(By.XPATH, "//input[@id='inputEmail']")
txt_password = drv.find_element(By.XPATH, "//input[@id='inputPassword']")

txt_username.clear()
txt_username.send_keys(user_id)
txt_password.clear()
txt_password.send_keys(password)
txt_password.send_keys(Keys.RETURN)
time.sleep(2)
# choose Claim Management menu
print("choose Claim Management menu")
# drv.implicitly_wait(60)
lnk_insurance_claim = drv.find_element(By.LINK_TEXT, "Claim Management")
# drv.implicitly_wait(10)
lnk_insurance_claim.send_keys(Keys.RETURN)
time.sleep(7)

# # Claim Management menu -> filter using Site ID & Event Date
# print("Claim Management menu")
# txt_site_id = drv.find_element(By.XPATH, "//input[@id='doc-site_id']")
# txt_event_date = drv.find_element(By.XPATH, "//input[@id='doc-event_date']")
# btn_search = drv.find_element(By.XPATH, "//a[@id='search-btn']")
# cmb_status = drv.find_element(By.XPATH, "//select[@id='doc-status']")
# # btn_print = drv.find_element(By.XPATH, "//button[@class='btn-print btn btn-sm vd_blue vd_bd-blue ']")
# # filtering claim by Site ID & Event Date
# print("filtering claim by Site ID & Event Date")
# # drv.implicitly_wait(10)
# site_id = "03CKR127"
# txt_site_id.clear()
# txt_site_id.send_keys(site_id)
# txt_event_date.clear()
# txt_event_date.send_keys("2022-05-01")
# all_option = cmb_status.find_elements(By.TAG_NAME, "option")
# for option in all_option:
#     if option.text == "ANY STATUS":
#         option.click()
#         break

# Claim Management menu -> filter using TASK ID
print("Claim Management menu")


# # search the insurance claim
# print("search the insurance claim")
# # drv.implicitly_wait(120)
# btn_search.click()
# time.sleep(5)
# tbl = drv.find_element(By.XPATH, "//table[@id='tbl_doc_list']")
# tbody = tbl.find_element(By.TAG_NAME, "tbody")
# # all_tbody = drv.find_elements(By.TAG_NAME, "tbody")
# # all_tbody = drv.switch_to.active_element.find_elements(By.TAG_NAME, "tbody")
# # print("parent={}:location={}:size{}".format(tbody.parent, tbody.location, str(tbody.size)))
# all_tr = tbody.find_elements(By.TAG_NAME, "tr")
# for tr in all_tr:
#     # try:
#     #     print(tr.get_attribute("id"))
#     # except exceptions.NoSuchAttributeException:
#     #     print("NoSuchAttributeException")
#     # except:
#     #     print("other error")
#     # all_td = tr.find_elements(By.TAG_NAME, "td")
#     btn_view = tr.find_element(
#         By.XPATH, "//button[@class='btn-view btn btn-sm vd_green vd_bd-green ']").send_keys(Keys.RETURN)
#     # btn_print = tr.find_element(By.XPATH, "//button[@class='btn-print btn btn-sm vd_blue vd_bd-blue ']").send_keys(Keys.RETURN)
#     # for td in all_td:
#     #     try:
#     #         if td.get_attribute("class") == " text-nowrap text-right":
#     #             btn_print = td.find_element(By.CLASS_NAME, "btn-print btn btn-sm vd_blue vd_bd-blue ")
#     #             btn_print.send_keys(Keys.RETURN)
#     #             # break
#     #         else:
#     #             print(td.text)
#     #     except exceptions.NoSuchElementException as err1:
#     #         print(err1.msg)
#     #     except exceptions.WebDriverException as err2:
#     #         print(err2.msg)
#     #     # break

# # drv.implicitly_wait(10)

# # lbl_task_id = drv.find_element(By.XPATH, "//td[@class='text-nowrap sorting_1']")
# # # print(lbl_task_id.text)
# # # NetGear Task Report TSK-CLM-20220501000001
# # page_pdf_title = "NetGear Task Report {}".format(lbl_task_id.text)
# # # print(page_pdf_title)

# # drv.implicitly_wait(20)
# # i = 0
# # for handle in drv.window_handles:
# #     if i == 1:
# #         drv.switch_to.window(handle)
# #         break
# #     i += 1

# # print(drv.title)
# # # https://geotagging.indosatooredoo.com/astweb/ast_insurance_main_print.php?task_id=TSK-CLM-20221020000010&sessionid=916.124528538614&token=ODFiMjZjNTc5ZWNl

# # btn_download = drv.find_element(By.XPATH, "//cr-icon-button[@id='download']")
# # print(btn_download.text)
# # btn_download.send_keys(Keys.RETURN)

# # drv.implicitly_wait(10)

# # logout

# # drv.quit()
