import pytest
import allure
from _pytest.nodes import Item
from _pytest.runner import CallInfo
from _pytest.main import Session
from typing import Generator, Any
from test_framework.utils.logger import logger_instance
from test_framework.reporting.allure_report_helpers import Allure
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

def pytest_sessionstart(session: Session) -> None:
    """
    Pytest hook called once before all tests start.

    Args:
        session (Session): The pytest test session object representing the entire test run.

    Returns:
        None
    """
    pass

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
