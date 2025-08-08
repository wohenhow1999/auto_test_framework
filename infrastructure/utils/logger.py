import logging
import os
import time
from io import StringIO


class Logger:
    """
    Centralized logging utility for pytest-based tests.

    Responsibilities:
    - Creates and configures a single logger instance (`pytest_logger`)
    - Adds three handlers:
        1. FileHandler: outputs logs to timestamped log file
        2. StreamHandler (StringIO): in-memory stream for Allure report attachment
        3. StreamHandler (stdout): prints logs to terminal during test runs
    - Exposes logger and in-memory stream via @property
    - Provides LoggerAdapter with `test_func` context for per-test log labeling
    """

    def __init__(self):
        """
        Initialize the logger and configure its handlers (file, stream, allure).
        """
        self._test_log_stream = StringIO()
        self._step_log_stream = StringIO()
        self._logger = logging.getLogger("pytest_logger")
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False

        if not self._logger.handlers:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            os.makedirs("logs", exist_ok=True)
            log_file = os.path.join("logs", f"pytest_{timestamp}.log")

            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(test_func)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            file_handler = logging.FileHandler(
                log_file, mode="w", encoding="utf-8"
            )
            file_handler.setFormatter(formatter)

            test_handler = logging.StreamHandler(self._test_log_stream)
            test_handler.setFormatter(formatter)

            step_handler = logging.StreamHandler(self._step_log_stream)
            step_handler.setFormatter(formatter)

            terminal_handler = logging.StreamHandler()
            terminal_handler.setFormatter(formatter)

            log_handlers = [
                file_handler,
                test_handler,
                step_handler,
                terminal_handler,
            ]
            for handler in log_handlers:
                self._logger.addHandler(handler)

    @property
    def logger(self) -> logging.Logger:
        """
        Returns:
            logging.Logger: The core logger instance.
        """
        return self._logger

    @property
    def test_log_stream(self) -> StringIO:
        """
        Returns:
            StringIO: The log stream used for full test log (pytest hook).
        """
        return self._test_log_stream

    @property
    def step_log_stream(self) -> StringIO:
        """
        Returns:
            StringIO: The log stream used for per-step log (step_with_log).
        """
        return self._step_log_stream

    def get_logger_adapter(
        self, class_name: str, func_name: str
    ) -> logging.LoggerAdapter:
        """
        Returns a LoggerAdapter that injects class.method into all log records.

        Args:
            class_name (str): Name of the test class.
            func_name (str): Name of the test method.

        Returns:
            logging.LoggerAdapter: Contextual logger adapter.
        """
        test_func_label = f"{class_name}.{func_name}()"
        return logging.LoggerAdapter(
            self._logger, {"test_func": test_func_label}
        )


logger_instance = Logger()
