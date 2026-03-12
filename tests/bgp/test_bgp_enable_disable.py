import allure
import logging
from test_framework.base.abstract_test_base import AbstractTestBase
from test_framework.utils.ssh_helpers import Ssh
from tests.bgp.settings import SWITCH_ONE_CONFIG


class TestBgpEnableDisable(AbstractTestBase):

    @classmethod
    def get_test_case_catalog(cls):
        return {
            "BGP-L1-001": {
                "test_function_name": cls.test_enable_bgp_with_valid_as_number_asplain_format,
                "description": "Verify that entering a valid asplain-format AS number successfully enables the BGP process",
            },
            "BGP-L1-002": {
                "test_function_name": cls.test_enable_bgp_with_valid_as_number_asdot_format,
                "description": "Verify that enable BGP with Valid AS Number (asdot+ Format)"
            }
        }

    @classmethod
    def setup_class(cls):
        """Connect SSH, collect device info, then enter Klish once for all TCs."""
        cls._ssh = Ssh(logger=logging.getLogger(cls.__name__))
        cls._ssh.connect_shell(
            hostname=SWITCH_ONE_CONFIG.host,
            username=SWITCH_ONE_CONFIG.username,
            password=SWITCH_ONE_CONFIG.password,
            port=SWITCH_ONE_CONFIG.port,
        )
        cls._ssh.enter_klish()

    @classmethod
    def teardown_class(cls):
        """Exit Klish and disconnect after all TCs finish."""
        if hasattr(cls, "_ssh") and cls._ssh:
            cls._ssh.exit_klish()
            cls._ssh.disconnect()

    def setup(self):
        # Bind SSH logger to current test context for accurate log labeling
        self._ssh.logger = self.logger
        # Ensure we start each TC at sonic# regardless of previous state
        self._ssh.end()

    def teardown(self):
        self._ssh.end()
        self._ssh.configure()
        self._ssh.send_klish_command("no router bgp", check=False)
        self._ssh.end()

    @allure.title("BGP-L1-001: Enable BGP with Valid AS Number (asplain Format)")
    @allure.description("Verify that entering a valid asplain-format AS number successfully enables the BGP process")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_enable_bgp_with_valid_as_number_asplain_format(self):
        self.AS_NUMBER = "65100"

        with self.allure.step_with_log("Step 1: Enter configure mode and execute router bgp 65100"):
            self._ssh.configure()
            output = self._ssh.send_klish_command(f"router bgp {self.AS_NUMBER}")
            self.assertion.assert_in(
                "config-router-bgp",
                output,
                "CLI prompt did not change to config-router-bgp mode",
            )

        with self.allure.step_with_log("Step 2: Verify show running-configuration bgp"):
            self._ssh.end()
            output = self._ssh.send_klish_command("show running-configuration bgp")
            self.assertion.assert_in(
                f"router bgp {self.AS_NUMBER}",
                output,
                f"'router bgp {self.AS_NUMBER}' not found in running config",
            )

    @allure.title("BGP-L1-002: Enable BGP with Valid AS Number (asdot+ Format)")
    @allure.description("Verify that enable BGP with Valid AS Number (asdot+ Format)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_enable_bgp_with_valid_as_number_asdot_format(self):
        self.AS_NUMBER = "1.100"
        # asdot+ 1.100 = 1 * 65536 + 100 = 65636 (asplain)
        # SONiC stores AS numbers in asplain format in running-configuration
        AS_NUMBER_ASPLAIN = "65636"

        with self.allure.step_with_log("Step 1: Enter configure mode and execute router bgp 1.100"):
            self._ssh.configure()
            output = self._ssh.send_klish_command(f"router bgp {self.AS_NUMBER}")
            self.assertion.assert_in(
                "config-router-bgp",
                output,
                "CLI prompt did not change to config-router-bgp mode",
            )

        with self.allure.step_with_log("Step 2: Verify show running-configuration bgp shows asplain equivalent"):
            self._ssh.end()
            output = self._ssh.send_klish_command("show running-configuration bgp")
            self.assertion.assert_in(
                f"router bgp {AS_NUMBER_ASPLAIN}",
                output,
                f"'router bgp {AS_NUMBER_ASPLAIN}' (asdot+ 1.100) not found in running config",
            )
