import allure
import time
from test_framework.base.abstract_test_base import AbstractTestBase


class TestWebUI(AbstractTestBase):

    @classmethod
    def get_test_case_catalog(cls):
        return {
            "testcase 1": {
                "test_function_name": cls.test_google_navigation,
                "description": "Sample test case showing basic browser navigation to Google.",
                # https://google.com
            },
        }

    def setup(self):
        with self.allure.step_with_log("Setup"):
            self.playwright.launch()

    def teardown(self):
        with self.allure.step_with_log("Teardown"):
            self.playwright.close()

    @allure.description("Sample test case showing basic browser navigation to Google")
    def test_google_navigation(self):
        with self.allure.step_with_log("Step1: Navigate to Google page"):
            google_page_url = "https://www.google.com"
            self.playwright.open_page(
                url=google_page_url, 
                expected_title="Google",
                expect_url="google.com"
            )
            time.sleep(5)