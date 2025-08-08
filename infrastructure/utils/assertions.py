import logging
import pytest
from typing import Optional, Union, Any


class Assertion:
    """
    Assertion utility class to encapsulate common test assertions
    with integrated logging and pytest failure reporting.

    This class supports structured assertion checks with rich debug logs
    and integrates seamlessly with pytest and Allure reporting.
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

    def assert_equal(
        self, actual_value: Any, expected_value: Any, error_message: str = ""
    ) -> None:
        """
        Assert that two values are equal.

        Args:
            actual_value (Any): The actual result value.
            expected_value (Any): The expected value to compare against.
            error_message (str, optional): Custom message to include on failure.

        Raises:
            pytest.fail: If values are not equal.
        """
        self.logger.debug(
            f"[assert_equal] Comparing actual={repr(actual_value)} with expected={repr(expected_value)}"
        )

        if actual_value != expected_value:
            full_error_message = (
                f"{error_message}\n" if error_message else ""
            ) + (
                f"Assertion Failed: Values are not equal\n"
                f"Expected: {repr(expected_value)}\n"
                f"Actual  : {repr(actual_value)}"
            )

            self.logger.error(full_error_message)
            pytest.fail(full_error_message)

        self.logger.info("Assertion Passed: Values are equal")

    def assert_not_equal(
        self, actual_value: Any, expected_value: Any, error_message: str = ""
    ) -> None:
        """
        Assert that two values are not equal.

        Args:
            actual_value (Any): The actual result value.
            expected_value (Any): The value that should not match.
            error_message (str, optional): Custom message to include on failure.

        Raises:
            pytest.fail: If values are equal.
        """
        self.logger.debug(
            f"[assert_not_equal] Comparing actual={repr(actual_value)} with expected={repr(expected_value)}"
        )

        if actual_value == expected_value:
            full_error_message = (
                f"{error_message}\n" if error_message else ""
            ) + (
                f"Assertion Failed: Values are equal\n"
                f"Expected: {repr(expected_value)}\n"
                f"Actual  : {repr(actual_value)}"
            )

            self.logger.error(full_error_message)
            pytest.fail(full_error_message)

        self.logger.info("Assertion Passed: Values are not equal")

    def assert_true(self, condition: Any, error_message: str = "") -> None:
        """
        Assert that a condition evaluates to True.

        Args:
            condition (Any): A boolean-like value expected to be truthy.
            error_message (str, optional): Custom message to include on failure.

        Raises:
            pytest.fail: If condition is False.
        """
        self.logger.debug(
            f"[assert_true] Checking condition={repr(condition)}"
        )

        if not condition:
            full_error_message = (
                f"{error_message}\n" if error_message else ""
            ) + "Assertion Failed: Condition is not True"
            self.logger.error(full_error_message)
            pytest.fail(full_error_message)

        self.logger.info("Assertion Passed: Condition is True")

    def assert_false(self, condition: Any, error_message: str = "") -> None:
        """
        Assert that a condition evaluates to False.

        Args:
            condition (Any): A boolean-like value expected to be falsy.
            error_message (str, optional): Custom message to include on failure.

        Raises:
            pytest.fail: If condition is True.
        """
        self.logger.debug(
            f"[assert_true] Checking condition={repr(condition)}"
        )

        if condition:
            full_error_message = (
                f"{error_message}\n" if error_message else ""
            ) + "Assertion Failed: Condition is not False"
            self.logger.error(full_error_message)
            pytest.fail(full_error_message)

        self.logger.info("Assertion Passed: Condition is False")

    def assert_in(
        self, member: Any, container: Any, error_message: str = ""
    ) -> None:
        """
        Assert that a member exists in a container.

        Args:
            member (Any): The value expected to be present.
            container (Any): A container supporting `in`.
            error_message (str, optional): Custom message to include on failure.

        Raises:
            pytest.fail: If member is not in container.
        """
        self.logger.debug(
            f"[assert_in] Checking if {repr(member)} in {repr(container)}"
        )

        if member not in container:
            full_error_message = (
                (f"{error_message}\n" if error_message else "")
                + f"Assertion Failed: {repr(member)} not found in {repr(container)}"
            )
            self.logger.error(full_error_message)
            pytest.fail(full_error_message)

        self.logger.info(
            f"Assertion Passed: {repr(member)} is in {repr(container)}"
        )

    def assert_not_in(
        self, member: Any, container: Any, error_message: str = ""
    ) -> None:
        """
        Assert that a member does not exist in a container.

        Args:
            member (Any): The value expected to be absent.
            container (Any): A container supporting `in`.
            error_message (str, optional): Custom message to include on failure.

        Raises:
            pytest.fail: If member is found in container.
        """
        self.logger.debug(
            f"[assert_not_in] Checking if {repr(member)} not in {repr(container)}"
        )

        if member in container:
            full_error_message = (
                (f"{error_message}\n" if error_message else "")
                + f"Assertion Failed: {repr(member)} unexpectedly found in {repr(container)}"
            )
            self.logger.error(full_error_message)
            pytest.fail(full_error_message)

        self.logger.info(
            f"Assertion Passed: {repr(member)} is not in {repr(container)}"
        )

    def assert_is_none(self, value: Any, error_message: str = "") -> None:
        """
        Assert that a value is None.

        Args:
            value (Any): The value expected to be None.
            error_message (str, optional): Custom message to include on failure.

        Raises:
            pytest.fail: If value is not None.
        """
        self.logger.debug(
            f"[assert_is_none] Checking if value is None: {repr(value)}"
        )

        if value is not None:
            full_error_message = (
                f"{error_message}\n" if error_message else ""
            ) + f"Assertion Failed: Expected None but got {repr(value)}"
            self.logger.error(full_error_message)
            pytest.fail(full_error_message)

        self.logger.info("Assertion Passed: Value is None")

    def assert_is_not_none(self, value: Any, error_message: str = "") -> None:
        """
        Assert that a value is not None.

        Args:
            value (Any): The value expected to be not None.
            error_message (str, optional): Custom message to include on failure.

        Raises:
            pytest.fail: If value is None.
        """
        self.logger.debug(
            f"[assert_is_not_none] Checking if value is not None: {repr(value)}"
        )

        if value is None:
            full_error_message = (
                f"{error_message}\n" if error_message else ""
            ) + "Assertion Failed: Value is unexpectedly None"
            self.logger.error(full_error_message)
            pytest.fail(full_error_message)

        self.logger.info("Assertion Passed: Value is not None")
