import paramiko
import pytest
import time
import logging
from typing import Optional, Union
from infrastructure.utils.decorators import Decorator
from tests.config.settings import JUMP_SERVER_CONFIG


class Ssh:
    """
    SSH utility class for managing remote interactive shell sessions.

    This class provides methods to establish SSH connections, open interactive shells,
    send commands, and cleanly close sessions. It is designed to integrate with pytest
    and support structured logging, making it suitable for automated testing environments
    such as network device configuration and validation.

    Example usage:
        ssh = Ssh()
        ssh.connect_shell(hostname="192.168.1.1", username="admin", password="pass")
        output = ssh.send_command_in_shell("show version")
        ssh.disconnect()
    """

    def __init__(
        self,
        logger: Optional[Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        """
        Initializes the Ssh utility with an optional logger.

        Args:
            logger (Logger | LoggerAdapter | None): Custom logger instance.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.client = None
        self.shell = None
        self.jump_client = None

    def connect_shell(
        self,
        hostname: str,
        username: str,
        password: str,
        port: int = 22,
        timeout: int = 10,
    ) -> None:
        """
        Establishes an SSH connection and opens an interactive shell session.

        This method logs into a remote host and invokes an interactive shell,
        enabling multi-command sessions (e.g., network device CLI interaction).

        Args:
            hostname (str): Target host IP or domain.
            username (str): SSH username.
            password (str): SSH password.
            port (int): SSH port (default: 22).
            timeout (int): Timeout in seconds for the connection attempt (default: 10).

        Raises:
            pytest.fail: If the connection or shell session fails.
        """
        self.logger.info(f"Connecting to {hostname}:{port} as {username}")
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(
                hostname=hostname,
                username=username,
                password=password,
                port=port,
                timeout=timeout,
            )
        except Exception as e:
            self.logger.error(f"SSH connection to {hostname} failed: {e}")
            pytest.fail(f"SSH connection failed: {e}")

        self.logger.info(f"Attempting to open interactive SSH shell...")
        try:
            self.shell = self.client.invoke_shell()
            time.sleep(1)
            if not self.shell:
                self.logger.error(
                    "invoke_shell() returned None — unable to start shell session"
                )
                pytest.fail(
                    "invoke_shell() returned None — unable to start shell session"
                )
        except Exception as e:
            self.logger.error(
                f"Exception occurred while opening interactive shell: {e}"
            )
            pytest.fail(f"Failed to start shell session: {e}")

        self.logger.info("SSH interactive shell established.")

    @Decorator.use_jump_host(jump_config=JUMP_SERVER_CONFIG)
    def connect_shell_via_jump(
        self, hostname, username, password, port=22, timeout=10
    ):
        """
        Initiates a shell connection to a target host via a jump server.

        This method primarily serves as an API endpoint. Its behavior is fully
        managed by a decorator, making its body intentionally empty.
        """
        pass

    def send_command_in_shell(
        self,
        command: str,
        delay: float = 1.0,
        check: bool = True,
        full_output: bool = False,
        pagination_prompt: str = "More",
        max_pages: int = 10
    ) -> str:
        """
        Sends a command to the interactive shell session.

        This method simulates CLI interaction. If full_output is True,
        it will automatically handle paginated output by detecting '--More--'
        and sending additional newlines until the full output is received.

        Args:
            command (str): The CLI command to send.
            delay (float): Delay between sends and reads (in seconds).
            check (bool): Whether to check for invalid command output.
            full_output (bool): If True, auto-handle pagination like '--More--'.
            pagination_prompt (str): Pagination prompt to detect (default: 'More').
            max_pages (int): Maximum allowed paginated screens to avoid infinite loops.

        Returns:
            str: Full output from the remote shell.

        Raises:
            pytest.fail: If no shell session is currently established or command is invalid.
            RuntimeError: If pagination exceeds max_pages.
        """
        if not self.shell:
            pytest.fail("Shell session is not established")

        self.logger.info(f"Sending command: {command}")
        self.shell.send(command + "\n")
        time.sleep(delay)

        output = ""
        result = self.shell.recv(100000).decode("utf-8")
        output += result
        self.logger.info(f"[Shell Output for '{command}']:\n{result}")

        if full_output:
            count = 0
            while pagination_prompt in result:
                if count > max_pages:
                    pytest.fail("Exceeded max pagination limit while reading CLI output.")
                self.shell.send(" ")
                time.sleep(delay)
                result = self.shell.recv(100000).decode("utf-8")
                output += result
                count += 1
                self.logger.debug(f"[Pagination {count}] More output:\n{result}")

        if check and self._is_invalid_command(output):
            self.logger.error(f"Invalid command detected: {command}")
            pytest.fail(
                f"Command failed:\n" f"{command}\n" f"Output:\n" f"{output}"
            )

        return output

    def _is_invalid_command(self, output: str) -> bool:
        """
        Detects invalid command based on shell output heuristics.

        Args:
            output (str): Shell output text.

        Returns:
            bool: True if output suggests an invalid command.
        """
        invalid_patterns = [
            "Invalid input",
            "Unrecognized command",
            "^",
            "Unknown command",
        ]
        return any(keyword in output for keyword in invalid_patterns)

    def disconnect(self) -> None:
        """
        Safely disconnects all SSH-related resources.

        This method is used to clean up the SSH connections established via
        the jump host. It ensures that resources are properly released in
        the correct order:

            1. Close the interactive shell session (if any).
            2. Close the SSH connection to the target host.
            3. Close the SSH connection to the jump host.

        Each shutdown step is wrapped in its own try/except block to ensure
        that failure in one does not prevent others from executing.

        This method is typically called after each test or before reconnecting
        to a new target host via jump server.
        """
        self.logger.info("Closing SSH resources...")

        try:
            if hasattr(self, "shell") and self.shell:
                self.shell.close()
                self.logger.info("Interactive shell closed.")
        except Exception as e:
            self.logger.warning(f"Faile to close shell: {e}")
        finally:
            self.shell = None

        try:
            if hasattr(self, "client") and self.client:
                self.client.close()
                self.logger.info("Target host connection closed.")
        except Exception as e:
            self.logger.warning(f"Failed to close target host connection: {e}")
        finally:
            self.client = None

        try:
            if hasattr(self, "jump_client") and self.jump_client:
                self.jump_client.close()
                self.logger.info("Jump host connection closed.")
        except Exception as e:
            self.logger.warning(f"Failed to close jump host connection: {e}")
        finally:
            self.jump_client = None

        self.logger.info("All SSH resources have been released.")