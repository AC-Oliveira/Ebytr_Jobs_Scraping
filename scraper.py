# pyright: reportOptionalMemberAccess=false
# pyright: reportPrivateImportUsage=false
# pyright: reportGeneralTypeIssues=false
import json
import pyautogui
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from bs4 import BeautifulSoup
from time import sleep


class job_scraper:
    def __init__(self) -> None:
        self.chrome_window = None

    def window(self):
        opts = ChromeOptions()
        opts.add_argument("--start-maximized")
        opts.add_experimental_option("detach", True)

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=opts
        )

        self.chrome_window = driver

    def __login_list_load(self):
        try:
            file = open("logins.json")
            data = json.load(file)
            return data
        except json.decoder.JSONDecodeError:
            raise Exception("Json read error try again!")

    def login_and_redirect(self):
        self.window()

        self.chrome_window.get("https://app.betrybe.com/login")

        data = self.__login_list_load()
        self.chrome_window.implicitly_wait(10)

        password = self.chrome_window.find_element(By.XPATH, "//*[@id='password']")
        email = self.chrome_window.find_element(By.ID, "email")

        email.send_keys(data["email"])
        password.send_keys(data["trybe"]["password"])

        self.chrome_window.find_element(
            By.XPATH,
            "//*[@id='root']/div[2]/div[2]/div/div/div[2]/div/div/form/div[3]/button",
        ).click()  # flake8: noqa

        sleep(3)
        self.chrome_window.get("https://app.betrybe.com/career/openings")

        sleep(7)

        mouse_scrolls = 0
        while mouse_scrolls <= 4:
            pyautogui.mouseDown(x=5107, y=2593)
            sleep(1)
            pyautogui.mouseUp()
            sleep(4)
            mouse_scrolls += 1

        print("fim da espera")
        self.chrome_window.execute_script(
            "window.scrollBy(0,document.body.scrollHeight || document.documentElement.scrollHeight);",  # noqa: E501
            "",
        )

        page_source = self.chrome_window.page_source
        content = BeautifulSoup(page_source, "lxml")

        job_list = content.find_all("li", {"aria-label": "Item da Listagem de Vagas"})
        return job_list

    def trybe_jobs_scraper(self):

        job_list = self.login_and_redirect()
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
                    "url": f"https://app.betrybe.com{job_link}",
                }
            )

        return jobs

    def register_page(self):  # noqa: C901
        jobs_to_register = self.trybe_jobs_scraper()
        jobs_data = open("jobs_data.json")
        jobs_data = json.load(jobs_data)
        # data = self.__login_list_load()
        # with open("jobs_data.json", "a") as file:
        #     file.write(json.dumps(jobs_to_register))
        #     file.close
        # frame = self.chrome_window.find_elements(By.TAG_NAME, "iframe")
        # frame_wrapper.find_element(By.TAG_NAME, "iframe")
        new_jobs = []
        for job in jobs_to_register:
            if job["type"] != "Presencial" and "mulher" not in job["title"]:
                self.chrome_window.get(job["url"])
                self.chrome_window.implicitly_wait(3)
                try:
                    register_button = self.chrome_window.find_element(
                        By.XPATH, "//*[text()='Quero me candidatar!']"
                    )

                    if register_button:
                        register_button.click()
                        self.chrome_window.implicitly_wait(10)

                        frame_wrapper = self.chrome_window.find_element(
                            By.CLASS_NAME, "tf-v1-iframe-wrapper"
                        )
                        frame_src = frame_wrapper.find_element(
                            By.TAG_NAME, "iframe"
                        ).get_attribute("src")

                        job["form_url"] = frame_src
                        new_jobs.append(job)
                    else:
                        with open("unregistred_jobs.json", "a") as file:
                            job["unregister_cause"] = "Outiside Job Page"
                            file.write(json.dumps(job))
                            file.close
                except selenium.common.exceptions.NoSuchElementException:
                    print(f'falha no preenchimento do form de: {job["title"]}')
                    with open("unregistred_jobs.json", "a") as file:
                        job["unregister_cause"] = "Form element not found"
                        file.write(f"{json.dumps(job)},")
                        file.close

        with open("form_links.json", "w") as file:
            file.write(json.dumps(new_jobs))
            file.close

    def form_filler(self):
        self.window()
        data = self.__login_list_load()
        file = open("form_links.json")
        forms = json.load(file)

        for form in forms:
            self.chrome_window.get(form["form_url"])
            self.chrome_window.implicitly_wait(10)

            span = self.chrome_window.find_element(By.XPATH, "//span[text()='Começar']")
            span.find_element(By.XPATH, "./../../..").click()

            inputs = self.chrome_window.find_elements(
                By.XPATH, "//input[@placeholder='Type or select an option']"
            )

            value = inputs[0].get_attribute("value")
            if value:
                inputs[0].send_keys("")

            inputs[0].send_keys(data["trybe"]["trybe_name"])

            self.chrome_window.find_element(
                By.XPATH, f'//mark[text()="{data["trybe"]["trybe_name"]}"]'
            ).click()

            inputs[1].send_keys(data["trybe"]["trybe_class"])
            self.chrome_window.find_element(
                By.XPATH, f'//mark[text()="{data["trybe"]["trybe_class"]}"]'
            ).click()

            self.chrome_window.find_element(
                By.XPATH, "//input[@placeholder='name@example.com']"
            ).send_keys(f'{data["email"]}{Keys.ENTER}')
            self.chrome_window.find_element(
                By.XPATH, "//input[@placeholder='(11) 96123-4567']"
            ).send_keys(f'{data["phone_number"]}{Keys.ENTER}')

            social_medias = self.chrome_window.find_elements(
                By.XPATH, "//input[@placeholder='https://']"
            )
            social_medias[0].send_keys(f'{data["linkedin"]}{Keys.ENTER}')
            social_medias[1].send_keys(f'{data["github"]}{Keys.ENTER}')

            self.chrome_window.find_element(
                By.XPATH, "//textarea[@placeholder='Type your answer here...']"
            ).send_keys(f'{data["trybe"]["trybe_answer"]}{Keys.ENTER}')

            self.chrome_window.find_element(By.XPATH, "//div[text()='Sim']").click()

            submit_span = self.chrome_window.find_element(
                By.XPATH, "//span[text()='Submit']"
            )
            submit_span.find_element(By.XPATH, "./../../..").click()


if __name__ == "__main__":
    scraper = job_scraper()
    scraper.form_filler()
