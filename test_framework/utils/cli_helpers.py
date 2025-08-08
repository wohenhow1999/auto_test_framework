import subprocess
import logging
import shlex
from typing import Optional, Union, List


class CommandExecutionError(Exception):
    """Custom exception raised when a shell command fails."""

    def __init__(
        self, command: List[str], returncode: int, stdout: str, stderr: str
    ):
        self.command = command
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        message = (
            f"Command '{' '.join(command)}' failed with exit code {returncode}\n"
            f"stdout: {stdout.strip()}\n"
            f"stderr: {stderr.strip()}"
        )
        super().__init__(message)


class Cli:
    """
    Utility class for executing shell commands with logging and error handling.

    Designed for test automation use cases with support for:
    - Timeout control
    - Output capturing
    - Consistent logging (INFO/DEBUG)
    - Custom error reporting via CommandExecutionError

    Example:
        cli.run_command(["ls", "-l"])
        cli.run_command("ls -l")
    """

    def __init__(
        self,
        logger: Optional[Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        """
        Initializes the Cli utility with an optional logger.

        Args:
            logger (Logger | LoggerAdapter | None): Custom logger instance.
        """
        self.logger = logger or logging.getLogger(__name__)

    def run_command(
        self,
        command: Union[str, list[str]],
        timeout: Optional[int] = 30,
        capture_output: bool = True,
        check: bool = True,
        shell: bool = False,
    ) -> subprocess.CompletedProcess:
        """
        Runs a shell command with logging, timeout, and optional error handling.

        Args:
            command: Command to run (string).
            timeout: Max time before killing the process.
            capture_output: If True, captures stdout and stderr.
            check: If True, raises CommandExecutionError on failure.
            shell: Use shell mode (be cautious with user input).

        Returns:
            CompletedProcess with stdout, stderr, returncode.

        Raises:
            CommandExecutionError: If command fails and check=True.
            RuntimeError: If the command times out.
        """
        if not shell:
            if isinstance(command, str):
                command_to_execute = shlex.split(command)
            elif isinstance(command, List):
                command_to_execute = command
            else:
                raise TypeError(
                    "Command must be a string or a list of strings."
                )
        else:
            if not isinstance(command, str):
                raise TypeError("Command must be a string when shell=True.")
            command_to_execute = command

        cmd_display = (
            command_to_execute if shell else " ".join(command_to_execute)
        )
        self.logger.info(f"Running command: {cmd_display}")

        try:
            result = subprocess.run(
                command_to_execute,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                shell=shell,
                check=False,
            )

            if result.returncode == 0:
                self.logger.info(f"Command succeeded: {cmd_display}")
            else:
                self.logger.info(
                    f"Command finished with non-zero exit code: {result.returncode}"
                )

            self.logger.debug(f"[Return code]: {result.returncode}")
            if capture_output:
                self.logger.debug(f"[STDOUT]: {result.stdout.strip()}")
                self.logger.debug(f"[STDERR]: {result.stderr.strip()}")

            if check and result.returncode != 0:
                raise CommandExecutionError(
                    command=(
                        command if isinstance(command, list) else [command]
                    ),
                    returncode=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                )

            return result

        except subprocess.TimeoutExpired as e:
            self.logger.error(
                f"Command timed out after {timeout}s: {cmd_display}"
            )
            raise RuntimeError(
                f"Command timed out after {timeout}s: {cmd_display}"
            ) from e
