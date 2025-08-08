import os
import json
import allure
import logging
from io import StringIO
from contextlib import contextmanager
from typing import Optional, Union
from infrastructure.utils.logger import logger_instance


class Allure:
    """
    Utility class for generating metadata files used by Allure reports.

    All methods are stateless and operate directly on the file system.
    """

    def __init__(
        self,
        logger: Optional[Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        """
        Initializes the Assertion utility with an optional logger.

        Args:
            logger (Logger | LoggerAdapter | None): Custom logger instance.
        """
        self.logger = logger or logging.getLogger(__name__)

    @staticmethod
    def generate_executor_info(
        report_dir: str = "reports/allure-results",
        name: str = "CI Test",
        type_: str = "pytest",
        url: str = "",
        build_order: int = 1,
        build_name: str = "",
        build_url: str = "",
        report_url: str = "",
    ):
        """
        Generate the Allure `executor.json` metadata file.

        Writes execution context info (e.g. CI name, build URL, report URL)
        to `executor.json` under the given Allure results directory. This
        metadata will appear in the Allure report's "Executor" section.

        Args:
            report_dir (str): Path to the Allure results directory.
            name (str): Executor name (e.g., "GitHub Actions", "Local Run").
            type_ (str): Executor type (e.g., "pytest", "jenkins").
            url (str): URL of the CI tool or executor homepage.
            build_order (int): Build order or ID (for CI tracking).
            build_name (str): Build label (e.g., version or branch).
            build_url (str): CI system build detail page URL.
            report_url (str): Public URL to the generated Allure report.

        Returns:
            None
        """
        executor_info = {
            "name": name,
            "type": type_,
            "url": url,
            "buildOrder": build_order,
            "buildName": build_name,
            "buildUrl": build_url,
            "reportUrl": report_url,
        }

        os.makedirs(report_dir, exist_ok=True)

        executor_file = os.path.join(report_dir, "executor.json")
        with open(executor_file, "w") as f:
            json.dump(executor_info, f, indent=4)

    @staticmethod
    def generate_environment_properties(
        report_dir: str = "reports/allure-results",
        env_info: Optional[dict] = None,
    ) -> None:
        """
        Generate an Allure-compatible environment.properties file to include
        environment metadata in the test report.

        This file helps Allure UI display custom environment information such as
        OS version, test environment, browser version, or any other relevant data.

        Args:
            report_dir (str): Directory path where the environment.properties file
                will be created. Defaults to "reports/allure-results".
            env_info (Optional[dict]): A dictionary containing environment keys and
                their corresponding values to be recorded in the properties file.

        Returns:
            None: This method writes directly to a file and does not return a value.
        """
        os.makedirs(report_dir, exist_ok=True)

        env_file_path = os.path.join(report_dir, "environment.properties")
        with open(env_file_path, "w", encoding="utf-8") as f:
            for key, value in env_info.items():
                if isinstance(value, str):
                    value = " ".join(value.split())

                safe_key = key.strip().replace(" ", "_").replace("=", "-")
                safe_value = value.replace("\n", " ").replace("=", ":")

                f.write(f"{safe_key}={safe_value}\n")

    @contextmanager
    def step_with_log(self, title: str):
        """
        Allure step wrapper that auto-attaches logs from logger_instance
        to this step block.
        """
        with allure.step(title):
            try:
                yield
            finally:
                log_stream = logger_instance.step_log_stream
                log_content = log_stream.getvalue()
                if log_content:
                    allure.attach(
                        log_content,
                        name=f"Log of step: {title}",
                        attachment_type=allure.attachment_type.TEXT,
                    )

                log_stream.truncate(0)
                log_stream.seek(0)
