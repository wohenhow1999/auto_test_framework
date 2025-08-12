import allure
from test_framework.base.abstract_test_base import AbstractTestBase


class TestApi(AbstractTestBase):

    @classmethod
    def get_test_case_catalog(cls):
        return {
            "testcase 1": {
                "test_function_name": cls.test_api_demo,
                "description": "test api",
                # https://google.com
            },
        }
    
    def setup(self):
        pass

    def teardown(self):
        pass

    @allure.description("test api")
    def test_api_demo(self):
        pass