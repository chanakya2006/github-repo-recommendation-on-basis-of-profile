from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# import time
from selenium.webdriver.chrome.service import Service

driver = webdriver.Chrome(service=Service(executable_path="D:\webdriver\chromedriver-win64\chromedriver.exe"))

def get_repo_names(traget_name):
    # Set up the WebDriver
    # options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode (optional)
    # driver = webdriver.Chrome(service=Service(executable_path="D:\webdriver\chromedriver-win64\chromedriver.exe"))
    l = []
    driver.get("https://github.com/"+traget_name+"?tab=repositories")
    for i in driver.find_elements(By.CLASS_NAME,"wb-break-all"):
        l.append(i.find_element(By.TAG_NAME,"a").get_attribute("href"))
    return l

def get_repo_readme(target_repo_urls):
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
