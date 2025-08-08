import re
import pytest
import allure
import time
from pathlib import Path
from _pytest.nodes import Item
from _pytest.runner import CallInfo
from _pytest.main import Session
from typing import Generator, Any, Dict
from infrastructure.utils.logger import logger_instance
from infrastructure.reporting.allure_report_helpers import Allure
from infrastructure.utils.ssh_helpers import Ssh
from infrastructure.utils.apv_helpers import Apv
from tests.config.settings import APV_SERVER_CONFIG
from tests.config.settings import META_CONFIG


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: Item, call: CallInfo
) -> Generator[Any, None, None]:
    """
    Pytest hook wrapper to capture logs after each test function call and
    attach the captured logs to the Allure report.

    Args:
        item (Item): The test item object representing the test function.
        call (CallInfo): The test call info object, includes test phase data.

    Yields:
        None: Yield control to pytest to execute the test.

    Workflow:
    - Yield control to allow pytest to execute the test function.
    - After test call phase, retrieve logs from the in-memory log stream.
    - If logs exist, attach them to the Allure report under the current test.
    - Clear the log stream buffer for the next test.

    This enables detailed per-test logging visibility within Allure reports.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        log_stream = logger_instance.test_log_stream
        log_contents = log_stream.getvalue()
        if log_contents:
            allure.attach(
                log_contents,
                name="Test Log",
                attachment_type=allure.attachment_type.TEXT,
            )

        log_stream.truncate(0)
        log_stream.seek(0)

@pytest.fixture(scope="class")
def baseline_fixture(request) -> Generator[Any, None, None]:
    """
    Prepares a baseline snapshot for the specified feature (e.g., SLB, VLAN).

    This class-scoped fixture connects via SSH and saves the default feature config
    for later comparison.

    Args:
        request: Pytest request object, providing test context and parameter.

    Example:

        Because it requires a parameter, use with @pytest.mark.parametrize and indirect=True:\n
        @pytest.mark.parametrize("baseline_fixture", ["slb"], indirect=True)\n
        @pytest.mark.usefixtures("baseline_fixture")\n
        class TestSlb(AbstractTestBase):\n
            ...

    Note:
        This is a more advanced pytest pattern and might be unfamiliar to some developers.

    Raises:
        RuntimeError on SSH or command failure.
    """
    feature_name = request.param
    logger = logger_instance.get_logger_adapter(request.cls.__name__, "setup_class")
    request.cls.logger = logger

    logger.info(f"Fetching the {feature_name} baseline...")
    ssh = Ssh()
    ssh.connect_shell_via_jump(
        hostname=APV_SERVER_CONFIG.server.host,
        username=APV_SERVER_CONFIG.server.username,
        password=APV_SERVER_CONFIG.server.password,
        port=APV_SERVER_CONFIG.server.port
    )

    apv = Apv(ssh=ssh)
    apv.enable_mode()

    try:
        default_slb_status = ssh.send_command_in_shell(f"show {feature_name} all", full_output=True)
    except Exception as e:
        logger.error(f"Failed to fetch default status for feature '{feature_name}': {e}")
        pytest.fail(f"Failed to fetch default config for {feature_name}: {e}")

    output_dir = Path("artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)
    baseline_path = output_dir / f"{feature_name}_baseline.txt"
    with open(baseline_path, "w", encoding="utf-8") as f:
        f.write(default_slb_status)

    logger.info(f"[baseline_fixture] Saved baseline snapshot for '{feature_name}' to: {baseline_path}")

    yield

def __parse_dut_info_to_dict(dut_info: str) -> dict:
    """
    Parse multi-line DUT info into a key-value dictionary
    """
    result = {}
    current_key = None

    for line in dut_info.splitlines():
        if not line.strip():
            continue

        if ":" in line and re.match(r"^\s*\S.*?:", line):
            parts = line.split(":", 1)
            current_key = parts[0].strip()
            result[current_key] = parts[1].strip()
        elif current_key:
            result[current_key] += " " + line.strip()

    return result

def __extract_dut_info(dut_info: str) -> str:
    """
    Extract DUT info block between "Host name" and "License Key"
    """
    pattern = r"(Host name\s*:.*?License Key\s*:.*?)(?:\n|$)"
    match = re.search(pattern, dut_info, re.DOTALL)
    if match:
        dut_info = match.group(1).strip()
    else:
        return "DUT info block not found"
    return __parse_dut_info_to_dict(dut_info)

def __extract_arrayos_info(raw_dut_info: str) -> dict:
    """
    Extract "ArrayOS Rel.<version>" and return as a single-entry dict
    """
    match = re.search(
        r"ArrayOS\s+Rel\.(APV\.\d+\.\d+\.\d+\.\d+)", raw_dut_info
    )
    if match:
        os_info = f"ArrayOS Rel.{match.group(1)}"

        parts = os_info.split(" ", 1)
    if len(parts) == 2:
        return {parts[0]: parts[1]}
    else:
        return {os_info: ""}

def pytest_sessionstart(session: Session) -> None:
    """
    Pytest hook called once before all tests start.

    This hook is used to:
    1. Establish an SSH connection to the DUT via a jump host.
    2. Run the "show version" command to retrieve raw device info.
    3. Parse the raw info into structured dictionaries (OS info and DUT info).
    4. Merge the parsed info dictionaries.
    5. Generate Allure environment properties file with the merged info.
    6. Disconnect the SSH session.

    Args:
        session (Session): The pytest test session object representing the entire test run.

    Returns:
        None
    """
    # ssh = Ssh()
    # ssh.connect_shell_via_jump(
    #     hostname=APV_SERVER_CONFIG.server.host,
    #     username=APV_SERVER_CONFIG.server.username,
    #     password=APV_SERVER_CONFIG.server.password,
    #     port=APV_SERVER_CONFIG.server.port
    # )
    # raw_dut_info = ssh.send_command_in_shell("show version")
    # parsed_os_info = __extract_arrayos_info(raw_dut_info)
    # parsed_dut_info = __extract_dut_info(raw_dut_info)
    # merged = parsed_os_info | parsed_dut_info
    # Allure.generate_environment_properties(env_info=merged)
    # ssh.disconnect()

def pytest_sessionfinish(session: Session, exitstatus: int) -> None:
    """
    Pytest hook called once after all tests finish.

    This hook is used to generate and write Allure executor metadata
    after the entire test session completes.

    Args:
        session (Session): The pytest test session object representing the entire test run.
        exitstatus (int): The exit status code of the test run (0 for success, non-zero for failures).

    Returns:
        None
    """
    Allure.generate_executor_info(name=META_CONFIG.test_executor)
