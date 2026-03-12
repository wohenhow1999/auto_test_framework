import allure
import logging
from test_framework.base.abstract_test_base import AbstractTestBase
from test_framework.utils.ssh_helpers import Ssh
from tests.issue_test.settings import SWITCH_ONE_CONFIG


# All physical Ethernet interfaces on the DUT
ETHERNET_PORTS = [
    "Ethernet0",   "Ethernet8",   "Ethernet16",  "Ethernet24",
    "Ethernet32",  "Ethernet40",  "Ethernet48",  "Ethernet56",
    "Ethernet64",  "Ethernet72",  "Ethernet80",  "Ethernet88",
    "Ethernet96",  "Ethernet104", "Ethernet112", "Ethernet120",
    "Ethernet128", "Ethernet136", "Ethernet144", "Ethernet152",
    "Ethernet160", "Ethernet168", "Ethernet176", "Ethernet184",
    "Ethernet192", "Ethernet200", "Ethernet208", "Ethernet216",
    "Ethernet224", "Ethernet232", "Ethernet240", "Ethernet248",
    "Ethernet256", "Ethernet264", "Ethernet272", "Ethernet280",
    "Ethernet288", "Ethernet296", "Ethernet304", "Ethernet312",
    "Ethernet320", "Ethernet328", "Ethernet336", "Ethernet344",
    "Ethernet352", "Ethernet360", "Ethernet368", "Ethernet376",
    "Ethernet384", "Ethernet392", "Ethernet400", "Ethernet408",
    "Ethernet416", "Ethernet424", "Ethernet432", "Ethernet440",
    "Ethernet448", "Ethernet456", "Ethernet464", "Ethernet472",
    "Ethernet480", "Ethernet488", "Ethernet496", "Ethernet504",
    "Ethernet512", "Ethernet513",
]

TARGET_MTU  = "9216"
RESTORE_MTU = "9100"


class TestIssue221113(AbstractTestBase):

    @classmethod
    def get_test_case_catalog(cls):
        return {
            "ISSUE-221113-001": {
                "test_function_name": cls.test_set_mtu_9216_all_interfaces,
                "description": "Set MTU 9216 on all interfaces and verify propagation to Klish, kernel, and CONFIG_DB",
            },
        }

    @classmethod
    def setup_class(cls):
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
        if hasattr(cls, "_ssh") and cls._ssh:
            cls._ssh.exit_klish()
            cls._ssh.disconnect()

    def setup(self):
        self._ssh.logger = self.logger
        self._ssh.end()

    def teardown(self):
        """Restore all interfaces to original MTU."""
        self._ssh.end()
        self._ssh.configure()
        for port in ETHERNET_PORTS:
            self._ssh.send_klish_command(f"interface {port.replace('Ethernet', 'Ethernet ')}")
            self._ssh.send_klish_command(f"mtu {RESTORE_MTU}")
            self._ssh.send_klish_command("exit")
        self._ssh.end()

    # -------------------------------------------------------------------------

    @allure.title("ISSUE-221113-001: Set MTU 9216 on all interfaces and verify propagation")
    @allure.description(
        "Configure MTU 9216 on all Ethernet interfaces via Klish, then verify the value "
        "is reflected in Klish show interface status, kernel /sys/class/net, CONFIG_DB, "
        "and Click CLI show interfaces status."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    def test_set_mtu_9216_all_interfaces(self):

        with self.allure.step_with_log("Step 1: Configure MTU 9216 on all interfaces via Klish"):
            self._ssh.configure()
            for port in ETHERNET_PORTS:
                klish_port = port.replace("Ethernet", "Ethernet ")
                self._ssh.send_klish_command(f"interface {klish_port}")
                self._ssh.send_klish_command(f"mtu {TARGET_MTU}")
                self._ssh.send_klish_command("exit")
            self._ssh.end()

        with self.allure.step_with_log("Step 2: Verify Klish show interface status (MTU = 9216)"):
            output = self._ssh.send_klish_command("show interface status", timeout=30.0)
            failed = self._check_mtu_in_status(output, TARGET_MTU)
            self.assertion.assert_equal(
                [], failed,
                f"Ports with unexpected MTU in Klish show interface status: {failed}",
            )

        # Steps 3-5 require Linux shell — exit Klish temporarily
        self._ssh.exit_klish()
        try:
            with self.allure.step_with_log("Step 3: Verify kernel MTU via /sys/class/net"):
                failed = []
                for port in ETHERNET_PORTS:
                    output = self._ssh.send_shell_command(f"cat /sys/class/net/{port}/mtu")
                    kernel_mtu = self._extract_value(output)
                    if kernel_mtu != TARGET_MTU:
                        failed.append(f"{port}: {kernel_mtu}")
                self.assertion.assert_equal(
                    [], failed,
                    f"Ports with unexpected kernel MTU: {failed}",
                )

            with self.allure.step_with_log("Step 4: Verify CONFIG_DB MTU via sonic-db-cli"):
                failed = []
                for port in ETHERNET_PORTS:
                    output = self._ssh.send_shell_command(
                        f'sonic-db-cli CONFIG_DB HGET "PORT|{port}" mtu'
                    )
                    db_mtu = self._extract_value(output)
                    if db_mtu != TARGET_MTU:
                        failed.append(f"{port}: {db_mtu}")
                self.assertion.assert_equal(
                    [], failed,
                    f"Ports with unexpected CONFIG_DB MTU: {failed}",
                )

            with self.allure.step_with_log("Step 5: Verify Click CLI show interfaces status (MTU = 9216)"):
                output = self._ssh.send_shell_command("show interfaces status", timeout=30.0)
                failed = self._check_mtu_in_status(output, TARGET_MTU)
                self.assertion.assert_equal(
                    [], failed,
                    f"Ports with unexpected MTU in Click show interfaces status: {failed}",
                )
        finally:
            self._ssh.enter_klish()

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _check_mtu_in_status(self, output: str, expected_mtu: str) -> list:
        """
        Parse 'show interface(s) status' output from either Klish or Click CLI.
        Detects the MTU column index dynamically from the header line.
        Returns a list of '<port>: <actual_mtu>' strings for any port where
        MTU does not match expected_mtu.
        """
        failed = []
        mtu_idx = None
        for line in output.splitlines():
            parts = line.split()
            if not parts:
                continue
            # Detect header to find MTU column (works for both Klish and Click)
            if mtu_idx is None and "MTU" in parts:
                mtu_idx = parts.index("MTU")
                continue
            if mtu_idx is not None and parts[0] in ETHERNET_PORTS:
                if len(parts) > mtu_idx and parts[mtu_idx] != expected_mtu:
                    failed.append(f"{parts[0]}: {parts[mtu_idx]}")
        return failed

    def _extract_value(self, output: str) -> str:
        """
        Extract the meaningful single-value response from a shell command output.
        Returns the last non-empty line that does not contain a shell prompt.
        """
        for line in reversed(output.splitlines()):
            val = line.strip()
            if val and not val.startswith("admin@") and "$" not in val:
                return val
        return ""
