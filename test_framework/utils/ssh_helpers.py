import paramiko
import pytest
import re
import time
import logging
from typing import Optional, Union


class Ssh:
    """
    SSH utility for SONiC device automation.

    Supports two CLI contexts:
    - Linux shell (Click CLI): prompt ends with  $  e.g. admin@sonic:~$
    - Klish CLI (entered via sonic-cli): prompt is sonic# or sonic(config[-*])#

    Uses prompt-based reading instead of fixed sleep delays for reliable
    and efficient command execution regardless of device response time.

    Typical usage:
        ssh = Ssh(logger=self.logger)
        ssh.connect_shell("192.168.1.1", "admin", "password")

        # Click CLI
        output = ssh.send_shell_command("show ip route")

        # Klish
        ssh.enter_klish()
        output = ssh.send_klish_command("show version")

        ssh.configure()
        ssh.send_klish_command("interface GigabitEthernet0/1")
        ssh.end()

        ssh.exit_klish()
        ssh.disconnect()
    """

    # Prompt patterns
    _SHELL_PROMPT = re.compile(r'\$\s*$', re.MULTILINE)
    _KLISH_PROMPT = re.compile(r'^sonic[^\n]*#\s*$', re.MULTILINE)
    _ANY_PROMPT   = re.compile(r'(\$\s*$|^sonic[^\n]*#\s*$)', re.MULTILINE)

    _INVALID_PATTERNS = [
        "Invalid input",
        "Unrecognized command",
        "Unknown command",
        "% Error",
        "^",
    ]

    _POLL_INTERVAL = 0.05   # seconds between recv checks when no data available
    _RECV_BUFFER   = 4096   # bytes per recv chunk

    def __init__(
        self,
        logger: Optional[Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        self.logger = logger or logging.getLogger(__name__)
        self.client = None
        self.shell  = None

    # -------------------------------------------------------------------------
    # Connection
    # -------------------------------------------------------------------------

    def connect_shell(
        self,
        hostname: str,
        username: str,
        password: str,
        port: int = 22,
        timeout: int = 10,
    ) -> None:
        """
        Establish SSH connection and open an interactive shell.
        Waits for the initial prompt before returning, so the caller
        can immediately send commands.

        Args:
            hostname: Target host IP or domain.
            username: SSH username.
            password: SSH password.
            port:     SSH port (default 22).
            timeout:  Connection timeout in seconds (default 10).
        """
        self.logger.info(f"Connecting to {hostname}:{port} as {username}...")
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

        self.logger.info("Opening interactive shell...")
        try:
            self.shell = self.client.invoke_shell()
            if not self.shell:
                pytest.fail("invoke_shell() returned None")
        except Exception as e:
            self.logger.error(f"Failed to open shell: {e}")
            pytest.fail(f"Failed to open shell: {e}")

        # Drain welcome banner and wait for initial shell prompt
        self._read_until_prompt(timeout=timeout)
        self.logger.info("SSH shell ready.")

    # -------------------------------------------------------------------------
    # Core read engine
    # -------------------------------------------------------------------------

    def _read_until_prompt(
        self,
        prompt_re: Optional[re.Pattern] = None,
        timeout: float = 10.0,
    ) -> str:
        """
        Read from the shell channel until a known prompt is detected or timeout.
        Handles Klish pagination (--More--) automatically.

        Args:
            prompt_re: Compiled regex for the expected prompt.
                       Defaults to _ANY_PROMPT (shell $ or klish #).
            timeout:   Max seconds to wait.

        Returns:
            Full output received up to and including the prompt line.
        """
        if prompt_re is None:
            prompt_re = self._ANY_PROMPT

        output   = ""
        deadline = time.time() + timeout

        while time.time() < deadline:
            if self.shell.recv_ready():
                chunk   = self.shell.recv(self._RECV_BUFFER).decode("utf-8", errors="replace")
                output += chunk

                # Auto-handle Klish pagination
                if "--More--" in chunk:
                    self.shell.send(" ")
                    continue

                if prompt_re.search(output):
                    break
            else:
                time.sleep(self._POLL_INTERVAL)
        else:
            self.logger.warning(
                f"Prompt not detected within {timeout}s — returning partial output."
            )

        return output

    # -------------------------------------------------------------------------
    # Command execution
    # -------------------------------------------------------------------------

    def _send_command(
        self,
        command: str,
        timeout: float = 10.0,
        prompt_re: Optional[re.Pattern] = None,
        check: bool = True,
    ) -> str:
        """
        Send a command and wait for the next prompt.

        Args:
            command:   Command string to send.
            timeout:   Max seconds to wait for prompt after sending.
            prompt_re: Expected prompt pattern. Defaults to _ANY_PROMPT.
            check:     If True, calls pytest.fail on invalid command output.

        Returns:
            Command output as string.
        """
        if not self.shell:
            pytest.fail("Shell session is not established.")

        self.logger.info(f"CMD: {command}")
        self.shell.send(command + "\n")
        output = self._read_until_prompt(prompt_re=prompt_re, timeout=timeout)
        self.logger.debug(f"OUTPUT:\n{output}")

        if check and self._is_invalid_command(output):
            self.logger.error(f"Invalid command: {command}\n{output}")
            pytest.fail(f"Invalid command: {command}\nOutput:\n{output}")

        return output

    def send_shell_command(
        self,
        command: str,
        timeout: float = 10.0,
        check: bool = True,
    ) -> str:
        """
        Send a Linux shell (Click CLI) command.
        Waits for shell prompt ($).

        Args:
            command: Click CLI command.
            timeout: Max seconds to wait.
            check:   Fail on invalid command output.

        Returns:
            Command output.
        """
        return self._send_command(
            command,
            timeout=timeout,
            prompt_re=self._SHELL_PROMPT,
            check=check,
        )

    def send_klish_command(
        self,
        command: str,
        timeout: float = 10.0,
        check: bool = True,
    ) -> str:
        """
        Send a Klish CLI command (sonic# or sonic(config)# context).
        Waits for Klish prompt (#).

        Args:
            command: Klish command.
            timeout: Max seconds to wait.
            check:   Fail on invalid command output.

        Returns:
            Command output.
        """
        return self._send_command(
            command,
            timeout=timeout,
            prompt_re=self._KLISH_PROMPT,
            check=check,
        )

    # -------------------------------------------------------------------------
    # Klish mode transitions
    # -------------------------------------------------------------------------

    def enter_klish(self, timeout: float = 10.0) -> None:
        """
        Enter Klish CLI from Linux shell.
        Sends 'sonic-cli' and waits for sonic# prompt.
        """
        self.logger.info("Entering Klish CLI...")
        self._send_command(
            "sonic-cli",
            timeout=timeout,
            prompt_re=self._KLISH_PROMPT,
            check=False,
        )
        self.logger.info("Klish CLI ready.")

    def exit_klish(self, timeout: float = 10.0) -> None:
        """
        Exit Klish CLI back to Linux shell.
        Sends 'exit' and waits for shell $ prompt.
        """
        self.logger.info("Exiting Klish CLI...")
        self._send_command(
            "exit",
            timeout=timeout,
            prompt_re=self._SHELL_PROMPT,
            check=False,
        )
        self.logger.info("Returned to Linux shell.")

    def configure(self, timeout: float = 10.0) -> None:
        """
        Enter configure mode in Klish.
        sonic# -> sonic(config)#
        """
        self.logger.info("Entering configure mode...")
        self._send_command(
            "configure",
            timeout=timeout,
            prompt_re=self._KLISH_PROMPT,
            check=False,
        )

    def exit_config(self, timeout: float = 10.0) -> None:
        """
        Exit one level of configure mode.
        e.g. sonic(config-if)# -> sonic(config)# -> sonic#
        """
        self._send_command(
            "exit",
            timeout=timeout,
            prompt_re=self._KLISH_PROMPT,
            check=False,
        )

    def end(self, timeout: float = 10.0) -> None:
        """
        Return directly to sonic# from any configure depth.
        """
        self.logger.info("Ending config mode...")
        self._send_command(
            "end",
            timeout=timeout,
            prompt_re=self._KLISH_PROMPT,
            check=False,
        )

    # -------------------------------------------------------------------------
    # Utilities
    # -------------------------------------------------------------------------

    def _is_invalid_command(self, output: str) -> bool:
        """
        Detect invalid command indicators in command output.

        Args:
            output: Shell output text.

        Returns:
            True if the output suggests an invalid command.
        """
        return any(pattern in output for pattern in self._INVALID_PATTERNS)

    def disconnect(self) -> None:
        """
        Safely release all SSH resources (shell → client).
        Each step is isolated so one failure does not block the others.
        """
        self.logger.info("Closing SSH resources...")

        try:
            if self.shell:
                self.shell.close()
                self.logger.info("Shell closed.")
        except Exception as e:
            self.logger.warning(f"Failed to close shell: {e}")
        finally:
            self.shell = None

        try:
            if self.client:
                self.client.close()
                self.logger.info("Connection closed.")
        except Exception as e:
            self.logger.warning(f"Failed to close connection: {e}")
        finally:
            self.client = None

        self.logger.info("SSH resources released.")
