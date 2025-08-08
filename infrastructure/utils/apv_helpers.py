import logging
import pytest
from typing import Optional, Union, Any
from infrastructure.utils.ssh_helpers import Ssh


class Apv:
    """
    A utility class for managing and interacting with APV (Array Networks) devices over SSH.

    Attributes:
        ssh (Ssh): SSH utility instance used for remote interactions.
        logger (Logger): Logger instance for internal debug and info output.
    """

    def __init__(
        self,
        logger: Optional[Union[logging.Logger, logging.LoggerAdapter]] = None,
        ssh: Optional[Ssh] = None,
    ):
        """
        Initializes the Apv utility.

        This manager is responsible for controlling HTTP servers on remote machines via SSH.
        An existing SSH session can be injected to share connection state across components.

        Args:
            logger (Logger | LoggerAdapter | None): Optional custom logger instance for logging internal operations.
            ssh (Ssh | None): Optional existing Ssh instance. If not provided, a new Ssh object will be created.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.ssh = ssh or Ssh(logger=self.logger)

    def get_prompt(self, delay: float = 1.0) -> str:
        """
        Sends an empty command to get the current terminal prompt.

        Returns:
            str: Current prompt (e.g., 'AN#', 'AN(config)#')
        """
        output = self.ssh.send_command_in_shell("", delay=delay, check=False)

        lines = output.strip().splitlines()
        if not lines:
            self.logger.warning(
                "No prompt detected in shell output, lines = {lines}."
            )
            pytest.fail("No prompt detected in shell output.")

        prompt = lines[-1].strip()
        self.logger.debug(f"Detected prompt: {prompt}")
        return prompt

    def config_terminal_mode(self, mode: bool = True, is_force: bool = False) -> None:
        """
        Enters or exits configuration terminal mode.

        Args:
            mode (bool): If True, enter config mode; if False, exit config mode.
        """
        current_prompt = self.get_prompt()

        if mode:
            if "config" in current_prompt:
                self.logger.info("Already in config mode.")
                return

            self.logger.info("Entering config terminal mode...")
            if is_force:
                self.ssh.send_command_in_shell("c t force", delay=4)
            else:
                self.ssh.send_command_in_shell("c t")

            new_prompt = self.get_prompt()
            if "config" not in new_prompt:
                self.logger.warning(
                    f"Failed to enter config mode. Current prompt: {new_prompt}"
                )
                pytest.fail(
                    f"Failed to enter config mode. Current prompt: {new_prompt}"
                )
            else:
                self.logger.info(
                    f"Entered config mode successfully: {new_prompt}"
                )

        else:
            if "config" not in current_prompt:
                self.logger.info("Not in config mode. No need to exit.")
                return

            self.logger.info("Exiting config terminal mode...")
            self.ssh.send_command_in_shell("exit", delay=2)

            new_prompt = self.get_prompt()
            if "config" in new_prompt:
                self.logger.warning(
                    f"Still in config mode after exit. Current prompt: {new_prompt}"
                )
                pytest.fail(
                    f"Still in config mode after exit. Current prompt: {new_prompt}"
                )
            else:
                self.logger.info(
                    f"Exited config mode successfully: {new_prompt}"
                )

    def enable_mode(self, mode: bool = True) -> None:
        """
        Enters enable mode.

        Args:
            mode (bool): Always True in current design. Meant for future extensibility.
        """
        current_prompt = self.get_prompt()

        if current_prompt.endswith("#"):
            self.logger.info("Already in enable mode.")
            return

        self.logger.info("Entering enable mode...")
        self.ssh.send_command_in_shell("enable")
        self.ssh.send_command_in_shell("\n")

        new_prompt = self.get_prompt()
        if not new_prompt.endswith("#"):
            self.logger.warning(
                f"Failed to enter enable mode. Current prompt: {new_prompt}"
            )
            pytest.fail(
                f"Failed to enter enable mode. Current prompt: {new_prompt}"
            )
        else:
            self.logger.info(f"Entered enable mode successfully: {new_prompt}")

    def write_memory(self) -> None:
        """
        Save all configuration.
        """
        self.ssh.send_command_in_shell("write memory")
