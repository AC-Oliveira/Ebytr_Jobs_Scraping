import json
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions  # type: ignore
from bs4 import BeautifulSoup
from time import sleep


class job_scraper:
    def window(self):
        opts = ChromeOptions()
        opts.add_experimental_option("detach", True)

        driver = webdriver.Chrome(  # type: ignore
            service=Service(ChromeDriverManager().install()), options=opts
        )

        return driver

    def __login_list_load(self):
        file = open("logins.json")
        data = json.load(file)
        return data

    def login_and_redirect(self):
        chrome_window = self.window()
        chrome_window.get("https://app.betrybe.com/login")

        trybe_data = self.__login_list_load()["trybe"]
        chrome_window.implicitly_wait(10)

        password = chrome_window.find_element(By.XPATH, "//*[@id='password']")
        email = chrome_window.find_element(By.ID, "email")

        email.send_keys(trybe_data["login"])
        password.send_keys(trybe_data["password"])

        chrome_window.find_element(
            By.XPATH,
            "//*[@id='root']/div[2]/div[2]/div/div/div[2]/div/div/form/div[3]/button",
        ).click()  # flake8: noqa

        sleep(3)
        chrome_window.get("https://app.betrybe.com/career/openings")
        sleep(10)

        page_source = chrome_window.page_source
        content = BeautifulSoup(page_source, "lxml")
        job_list = content.find_all("li")
        print(job_list)

    def trybe_jobs_scraper(self, url):
        response = requests.get(url)
        content = BeautifulSoup(response.text, "lxml")
        job_list = content.find_all("li", {"aria-label": "Item da Listagem de Vagas"})
        jobs = []
        for job in job_list:
            job_title = " ".join(
                job.find("span", {"class": "openings__job-title"})
                .text.replace("\n", "")
                .split()
            )

            job_type = job.find("div", {"class": "openings__detail openings__fulltime"})
            if job_type:
                job_type = job_type.text.split()[-1]

            job_address = job.find(
                "div", {"class": "openings__detail openings__crop-chips"}
            )
            if job_address:
                if len(job_address.text):
                    job_address = job_address.text
                else:
                    job_address = None

            job_link = job.find(
                "a",
                {
                    "aria-label": "Cartão contendo informações sobre a Vaga, ao clicar redirecionará para a vaga em questão."  # noqa: E501
                },
                href=True,
            )["href"]

            jobs.append(
                {
                    "title": job_title,
                    "type": job_type,
                    "address": job_address,
                    "url": job_link,
                }
            )

        return jobs


scraper = job_scraper()
scraper.trybe_jobs_scraper("http://127.0.0.1:5500/jobslist.html")
