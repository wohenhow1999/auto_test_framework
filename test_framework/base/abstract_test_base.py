from types import FunctionType
from abc import ABC, abstractmethod
from infrastructure.utils.assertions import Assertion
from infrastructure.utils.cli_helpers import Cli
from infrastructure.utils.ssh_helpers import Ssh
from infrastructure.utils.decorators import Decorator
from infrastructure.utils.apv_helpers import Apv
from infrastructure.utils.remote_http import RemoteHttpServerManager
from infrastructure.reporting.allure_report_helpers import Allure
from infrastructure.utils.logger import logger_instance


class AbstractTestBase(ABC):
    """
    Base class for all test cases.

    Responsibilities:
    - Enforce implementation of test-level `setup` and `teardown` in child classes.
    - Provide common utilities: logger, assertion, and lifecycle hooks.
    - Automatically attach per-test logs to Allure reports.
    """

    @classmethod
    @abstractmethod
    def get_test_case_catalog(cls) -> dict:
        """
        Child test classes must implement this to define test metadata.

        Returns:
            dict: Dictionary containing test case metadata.

        Example:
            @classmethod\n
            def get_test_case_catalog(cls):\n
                return {
                    "testcase 1": {
                        "test_function_name": cls.test_slb_ip2,
                        "description": "Jamie self test about slb ip",
                        # https://google.com
                    },
                }
        """
        pass

    @abstractmethod
    def setup(self) -> None:
        """To be implemented by child classes: logic executed before each test case."""
        pass

    @abstractmethod
    def teardown(self) -> None:
        """To be implemented by child classes: logic executed after each test case."""
        pass

    def setup_method(self, method: FunctionType) -> None:
        """
        Pytest lifecycle hook executed before each test function.

        Args:
            method (FunctionType): The current test function.

        Responsibilities:
        - Prepare contextual logger for the test.
        - Initialize assertion utilities.
        - Invoke custom test setup if not skipped.
        """
        self.__prepare_logger(method)
        self.__init_utilities()

        if self._should_skip_setup(method):
            return
        self.setup()

    def teardown_method(self, method: FunctionType) -> None:
        """
        Pytest lifecycle hook executed after each test function.

        Args:
            method (FunctionType): The current test function.

        Responsibilities:
        - Invoke custom test teardown if not skipped.
        """
        if self._should_skip_teardown(method):
            return
        self.teardown()

    def __prepare_logger(self, method: FunctionType):
        """
        Prepare a context-aware logger for the current test.

        Args:
            method (FunctionType): The current test function.

        Clears previous log buffer and attaches a logger with test context.
        """
        self._method_name = method.__name__
        self.logger = logger_instance.get_logger_adapter(
            self.__class__.__name__, self._method_name
        )

    def __init_utilities(self):
        """
        Initialize shared test utilities.
        """
        self.assertion = Assertion(logger=self.logger)
        self.cli = Cli(logger=self.logger)
        self.ssh = Ssh(logger=self.logger)
        self.decorator = Decorator()
        self.allure = Allure(logger=self.logger)
        self.apv = Apv(logger=self.logger, ssh=self.ssh)
        self.http_server_manager = RemoteHttpServerManager(
            logger=self.logger, ssh=self.ssh
        )

    def _should_skip_setup(self, method: FunctionType) -> bool:
        """
        Check if the test method has the `@pytest.mark.no_setup` marker.

        Args:
            method (FunctionType): The test method.

        Returns:
            bool: True if setup should be skipped.
        """
        marks = getattr(method, "pytestmark", [])
        if any(m.name == "no_setup" for m in marks):
            self.logger.info(f"Skipping setup for {method.__name__}")
            return True
        return False

    def _should_skip_teardown(self, method: FunctionType) -> bool:
        """
        Check if the test method has the `@pytest.mark.no_teardown` marker.

        Args:
            method (FunctionType): The test method.

        Returns:
            bool: True if teardown should be skipped.
        """
        marks = getattr(method, "pytestmark", [])
        if any(m.name == "no_teardown" for m in marks):
            self.logger.info(f"Skipping teardown for {method.__name__}")
            return True
        return False
