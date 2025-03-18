from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import random
from fake_useragent import UserAgent

class webscrape:
    def __init__(self,path):
        ua = UserAgent()
        options = webdriver.ChromeOptions()
        #options.add_argument("--headless")
        options.add_argument(f'user-agent={ua.random}')
        self.path = path
        self.driver = webdriver.Chrome(service=Service(executable_path=path),options=options)

    def get_repo_names_from_target_name(self,target_name: str,limit = 1000) -> list:
        self.driver.get("https://github.com/"+ target_name)
        temp = self.driver.find_element(By.TAG_NAME,"turbo-frame")
        temp = temp.find_element(By.CLASS_NAME,"position-relative")
        counter = 0
        while counter < 24:
            try:
                sleep(1)
                temp.find_element(By.NAME,"button").click()
                counter += 1
            except:
                break
        l = set()
        soup = BeautifulSoup(temp.get_attribute("innerHTML"),"html.parser")
        for i,link in enumerate(soup.find_all("a")):
            if i <= limit:
                href = link.get("href")
                text = link.get_text(strip=True)
        
                if href and text in href and text != "":
                    l.add(href)
            else:
                break
        return list(l)
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
        sleep(1)
        temp = self.driver.find_elements(By.TAG_NAME,"a")
        for i in temp:
            if i.get_attribute("class") == "prc-Button-ButtonBase-c50BI LinkButton-module__code-view-link-button--xvCGA flex-items-center fgColor-default":
                self.driver.get(i.get_attribute("href"))
                break
        sleep(2)
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
    def search_result_from_query(self, query : str, recommend=5, max_retries=3, base_delay=10) -> list:
        ua = UserAgent()
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-agent={ua.random}')
        driver = webdriver.Chrome(service=Service(executable_path=self.path),options=options)

        try:
            repositories = []
            attempt = 0

            # Handle C++ query special case
            if query.lower() == "c++":
                query = "C%2B%2B"

            while attempt < max_retries and len(repositories) < recommend:
                try:
                    # Add delay with randomization
                    wait_time = base_delay * (1 ** attempt) + random.uniform(1, 5)
                    print(f"Waiting {wait_time:.2f} seconds before request...")
                    time.sleep(wait_time)

                    # Make the request
                    url = f"https://github.com/search?q={query}&type=repositories"
                    driver.get(url)

                    # Wait for content to load
                    wait = WebDriverWait(driver, 5)
                    repo_list = wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, "logged-out"))
                    )
                    temp = driver.find_element(By.CLASS_NAME,"logged-out").find_element(By.CLASS_NAME,"application-main ").find_element(By.TAG_NAME,"main")
                    temp.find_element(By.CLASS_NAME,"gZKkEq")
                    for k,i in enumerate(temp.find_elements(By.CLASS_NAME,"iwUbcA")):
                        if k <= recommend:
                            repositories.append(i.find_element(By.CLASS_NAME,"kYLlPM").find_element(By.TAG_NAME,"a").get_attribute("href"))
                        else:
                            break
                    # Find repository links
                    # repo_elements = repo_list.find_elements(By.CSS_SELECTOR, "a[data-hydro-click]")

                    # for repo in repo_elements:
                    #     href = repo.get_attribute("href")
                    #     if href and "/repository/" in href and href not in repositories:
                    #         repositories.append(href)
                    #         if len(repositories) >= recommend:
                    #             break
                            
                    if repositories:  # If we found repositories, break the retry loop
                        break

                except TimeoutException:
                    print(f"Timeout on attempt {attempt + 1}/{max_retries}. Possibly rate limited.")
                    attempt += 1
                    if attempt < max_retries:
                        # If rate limited, wait longer and rotate user agent
                        time.sleep(5 * attempt)  # Progressive waiting: 1min, 2min, 3min
                        driver.quit()
                        options.add_argument(f'user-agent={ua.random}')
                        driver = webdriver.Chrome(options=options)

                except Exception as e:
                    print(f"Error on attempt {attempt + 1}/{max_retries}: {str(e)}")
                    attempt += 1
                    if attempt < max_retries:
                        time.sleep(30)

            return repositories[:recommend]  # Ensure we don't return more than requested

        finally:
            driver.quit()

# Example usage

# Example usage

"""
from del__ import webscrape

obj = webscrape("D:\webdriver\chromedriver-win64\chromedriver.exe")
print(obj.get_repo_names_from_target_name("chanakya2006"))
print(obj.get_repo_readme(["https://github.com/chanakya2006/github-repo-recommendation-on-basis-of-profile"]))
print(obj.get_commits_from_repo_url("https://github.com/chanakya2006/github-repo-recommendation-on-basis-of-profile"))
"""

if __name__ == "__main__":
    obj = webscrape("chromedriver.exe")
    #print(obj.search_result_from_query("mkc"))
    print(obj.search_result_from_query("hello"))