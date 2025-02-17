from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service
import requests
from bs4 import BeautifulSoup

driver = webdriver.Chrome(service=Service(executable_path="D:\webdriver\chromedriver-win64\chromedriver.exe"))

def get_repo_names_from_target_name(target_name: str) -> list:
    # Set up the WebDriver
    # options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode (optional)
    # driver = webdriver.Chrome(service=Service(executable_path="D:\webdriver\chromedriver-win64\chromedriver.exe"))
    driver.get("https://github.com/"+ target_name)
    temp = driver.find_element(By.TAG_NAME,"turbo-frame")
    temp = temp.find_element(By.CLASS_NAME,"position-relative")
    counter = 0
    while counter < 24:
        try:
            time.sleep(1)
            temp.find_element(By.NAME,"button").click()
            counter += 1
        except:
            break
    l = []
    soup = BeautifulSoup(temp.get_attribute("innerHTML"),"html.parser")
    for link in soup.find_all("a"):
        href = link.get("href")
        text = link.get_text(strip=True)
        
        if href and text in href and text != "":
            l.append(href)
    return l

def get_repo_readme(target_repo_urls : list) -> dict:
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

def get_commits_from_repo_url(link_to_repo: str):
    driver.get(link_to_repo)
    time.sleep(1)
    temp = driver.find_elements(By.TAG_NAME,"a")
    for i in temp:
        if i.get_attribute("class") == "prc-Button-ButtonBase-c50BI LinkButton-module__code-view-link-button--xvCGA flex-items-center fgColor-default":
            driver.get(i.get_attribute("href"))
            break
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source,"html.parser")
    dic = {}
    for i in soup.find_all("div",class_ = "Timeline__ToggleTimelineItem-sc-1nkzbnu-1 ehuczD Timeline-Item"):
        for k in i.find_all("a",class_ = "prc-Link-Link-85e08"):
            if k.get("class") != ['Box-sc-g0xbh4-0', 'epISVM', 'prc-Link-Link-85e08']:
                print(k.get("href"))
                if k.get("href") not in dic:
                    dic[k.get("href")] = 1
                else :
                    dic[k.get("href")] += 1
    for i in soup.find_all("div",class_ = "Timeline__ToggleTimelineItem-sc-1nkzbnu-1 bTwOen Timeline-Item"):
        for k in i.find_all("a",class_ = "prc-Link-Link-85e08"):
            if k.get("class") != ['Box-sc-g0xbh4-0', 'epISVM', 'prc-Link-Link-85e08']:
                print(k.get("href"))
                if k.get("href") not in dic:
                    dic[k.get("href")] = 1
                else :
                    dic[k.get("href")] += 1

    # error occurs at https://github.com/chanakya2006/github-repo-recommendation-on-basis-of-profile/commits/main/ check on this repo
    return dic

get_commits_from_repo_url("https://github.com/DoingWoW/buildWow/commits/master/")