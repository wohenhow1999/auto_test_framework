import pytest
import allure
import time
from infrastructure.base.abstract_test_base import AbstractTestBase


class TestSUM(AbstractTestBase):

    @classmethod
    def get_test_case_catalog(cls):
        return {
            "testcase 1": {
                "test_function_name": cls.test_sum,
                "description": "test sum",
                # https://google.com
            },
            "testcase 2": {
                "test_function_name": cls.test_string,
                "description": "test string",
                # https://google.com
            },
            "testcase 3": {
                "test_function_name": cls.test_minus,
                "description": "test minus",
                # https://google.com
            },
        }

    def setup(self):
        self.logger.info("----setup----")

    def teardown(self):
        self.logger.info("----teardown----")

    @pytest.mark.no_setup
    @allure.description("test sum")
    def test_sum(self):
        with self.allure.step_with_log("Step1: test the result of sum."):
            x = 1 + 2
            self.assertion.assert_equal(x, 3, "wrong sum")

    @pytest.mark.no_setup
    @pytest.mark.no_teardown
    @allure.description("test string")
    def test_string(self):
        with self.allure.step_with_log("Step1: test the result of string."):
            x = "jfeijfoejfoei"
            self.assertion.assert_equal(x, "jfeijfoejfoei", "wrong string")

    @allure.description("test minus")
    def test_minus(self):
        with self.allure.step_with_log("Step1: input 5 to x."):
            self.logger.info("x = 5")
            x = 5
            time.sleep(1)

        with self.allure.step_with_log("Step2: input 2 to y."):
            self.logger.info("y = 2")
            y = 2
            time.sleep(1)

        with self.allure.step_with_log("Step3: test the result of minus."):
            self.logger.info("z = x - y")
            z = x - y
            time.sleep(1)
            self.assertion.assert_equal(z, 3, "wrong minus")

    @allure.description("kfoekfoko")
    def test_string2(self):
        with allure.step("step1 kodwkdowkwkdo"):
            self.logger.info("x = dddddf")
            x = "ddddf"
            time.sleep(1)

        with allure.step("step2 kodwkdowkwkdo"):
            self.logger.info("y = ddddd")
            y = "dddd"
            time.sleep(1)

        with allure.step("step3 compare"):
            self.logger.info("x = y")
            self.assertion.assert_equal(x, y, "x is not equal to y")
            time.sleep(1)

    def test_assert_equal_pass(self):
        self.assertion.assert_equal(5, 5)

    def test_assert_equal_fail(self):
        self.assertion.assert_equal(5, 10)

    def test_assert_not_equal_pass(self):
        self.assertion.assert_not_equal("foo", "bar")

    def test_assert_not_equal_fail(self):
        self.assertion.assert_not_equal("same", "same")

    def test_assert_true_pass(self):
        self.assertion.assert_true(1 == 1)

    def test_assert_true_fail(self):
        self.assertion.assert_true(False)

    @allure.description("jkfeifjie")
    def test_run_command_success_string(self):
        """Test a successful command execution with string command."""
        command = "echo hello world"
        result = self.cli.run_command(command)
        self.assertion.assert_equal(result.returncode, 0)
        self.assertion.assert_in("hello world", result.stdout)
        assert "hello world" in result.stdout
        self.assertion.assert_equal(result.stderr, "")
        assert result.stderr == ""

    def test_run_command_success_list(self):
        """Test a successful command execution with list command."""
        command = ["echo", "hello", "world"]
        result = self.cli.run_command(command)
        assert result.returncode == 0
        assert "hello world" in result.stdout
        assert result.stderr == ""

    def test_run_command_success_no_output_capture(self):
        """Test successful command execution without capturing output."""
        command = "echo should not be captured"
        result = self.cli.run_command(command, capture_output=False)
        assert result.returncode == 0
        assert result.stdout == None
        assert result.stderr == None

    def test_run_command_success_shell_mode(self):
        """Test a successful command execution in shell mode."""
        command = "ls -l /tmp/ | grep tmp"
        result = self.cli.run_command(command, shell=True)
        assert result.returncode == 0
        assert "tmp" in result.stdout
        assert result.stderr == ""
