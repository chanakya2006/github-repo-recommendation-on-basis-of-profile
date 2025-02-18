from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service
import requests
from bs4 import BeautifulSoup

class webscrape:
    def __init__(self,path):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless") 
        self.driver = webdriver.Chrome(service=Service(executable_path=path),options=options)
    def get_repo_names_from_target_name(self,target_name: str) -> list:
        self.driver.get("https://github.com/"+ target_name)
        temp = self.driver.find_element(By.TAG_NAME,"turbo-frame")
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
    def get_repo_readme(self,target_repo_urls : list) -> dict:
        dic = {}
        for i in target_repo_urls:
            self.driver.get(i)
            try:
                l = ""
                for k in self.driver.find_element(By.CLASS_NAME,"application-main").find_element(By.ID,"js-repo-pjax-container").find_elements(By.TAG_NAME,"p"):
                    l += k.text
                dic[i] = l
            except:
                print("No readme of url : "+ i)
        return dic

    def get_commits_from_repo_url(self,link_to_repo: str):
        self.driver.get(link_to_repo)
        time.sleep(1)
        temp = self.driver.find_elements(By.TAG_NAME,"a")
        for i in temp:
            if i.get_attribute("class") == "prc-Button-ButtonBase-c50BI LinkButton-module__code-view-link-button--xvCGA flex-items-center fgColor-default":
                self.driver.get(i.get_attribute("href"))
                break
        time.sleep(2)
        soup = BeautifulSoup(self.driver.page_source,"html.parser")
        dic = {}
        for i in soup.find_all("div",class_ = "Timeline__ToggleTimelineItem-sc-1nkzbnu-1 ehuczD Timeline-Item"):
            for k in i.find_all("a",class_ = "prc-Link-Link-85e08"):
                if k.get("class") != ['Box-sc-g0xbh4-0', 'epISVM', 'prc-Link-Link-85e08']:
                    if k.get("href") not in dic:
                        dic[k.get("href")] = 1
                    else :
                        dic[k.get("href")] += 1
        for i in soup.find_all("div",class_ = "Timeline__ToggleTimelineItem-sc-1nkzbnu-1 bTwOen Timeline-Item"):
            for k in i.find_all("a",class_ = "prc-Link-Link-85e08"):
                if k.get("class") != ['Box-sc-g0xbh4-0', 'epISVM', 'prc-Link-Link-85e08']:
                    if k.get("href") not in dic:
                        dic[k.get("href")] = 1
                    else :
                        dic[k.get("href")] += 1

        return dic


print(webscrape(path="D:\webdriver\chromedriver-win64\chromedriver.exe").get_repo_names_from_target_name("chanakya2006"))
print(webscrape(path="D:\webdriver\chromedriver-win64\chromedriver.exe").get_repo_readme(["https://github.com/chanakya2006/github-repo-recommendation-on-basis-of-profile"]))
print(webscrape(path="D:\webdriver\chromedriver-win64\chromedriver.exe").get_commits_from_repo_url("https://github.com/chanakya2006/github-repo-recommendation-on-basis-of-profile"))