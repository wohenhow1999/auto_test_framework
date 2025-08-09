import os
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from test_framework.base.abstract_test_base import AbstractTestBase


class TestWebUI(AbstractTestBase):

    @classmethod
    def get_test_case_catalog(cls):
        return {
            "testcase 1": {
                "test_function_name": cls.test_google,
                "description": "Jamie self test about slb ip",
                # https://google.com
            },
        }

    def setup(self):
        self.logger.info("---setup---")
    
    def teardown(self):
        self.logger.info("----teardown----")

    @allure.description("Web UI demo")
    def test_google(self):
        with self.allure.step_with_log("Step1: open google page"):
            print(f"DISPLAY = {os.environ.get('DISPLAY')}")
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")

            service = Service("/usr/local/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=options)

            driver.get("https://www.google.com")
            assert "Google" in driver.title

            driver.quit()