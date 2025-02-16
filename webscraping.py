from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service

driver = webdriver.Chrome(service=Service(executable_path="D:\webdriver\chromedriver-win64\chromedriver.exe"))

def get_repo_names_from_target_name(target_name):
    # Set up the WebDriver
    # options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode (optional)
    # driver = webdriver.Chrome(service=Service(executable_path="D:\webdriver\chromedriver-win64\chromedriver.exe"))
    driver.get("https://github.com/"+ target_name)
    temp = driver.find_element(By.TAG_NAME,"turbo-frame")
    temp = temp.find_element(By.CLASS_NAME,"position-relative")
    #print(temp.find_element(By.CLASS_NAME,"mt-4"))
    time.sleep(1)
    temp.find_element(By.NAME,"button").click()
    while True:
        try:
            time.sleep(1)
            temp.find_element(By.NAME,"button").click()
        except:
            break
    driver.find_element(By.CLASS_NAME,"js-yearly-contributions")

def get_repo_readme(target_repo_urls : list) -> dict:
    # driver = webdriver.Chrome(service=Service(executable_path="D:\webdriver\chromedriver-win64\chromedriver.exe"))
    dic = {}
    for i in target_repo_urls:
        driver.get(i)
        try:
            l = ""
            for k in driver.find_element(By.CLASS_NAME,"application-main").find_element(By.ID,"js-repo-pjax-container").find_elements(By.TAG_NAME,"p"):
                l += k.text
            dic[i] = l
        except:
            print("No readme of url : "+ i)
    return dic


get_repo_names_from_target_name("chanakya2006")