from selenium.webdriver import ChromeOptions, Chrome  # type: ignore


class job_scraper:
    def window(self):
        opts = ChromeOptions()
        opts.add_experimental_option("detach", True)
        PATH = "/home/allan/Projects/ProjectsPy/web-scraping/chromedriver"

        driver = Chrome(
            executable_path=PATH,
            chrome_options=opts,
        )
        return driver

    def trybe_scraper(self):
        chrome_window = self.window()
        chrome_window.get("https://app.betrybe.com/career/openings")


scraper = job_scraper()
scraper.trybe_scraper()
