import logging
import pytest
from typing import Optional, Union
from infrastructure.utils.ssh_helpers import Ssh


class RemoteHttpServerManager:
    """
    Manages HTTP server operations on a remote machine over SSH.

    Designed for use in test automation scenarios where dynamic setup and teardown
    of lightweight HTTP servers is required to verify connectivity, routing, load balancing,
    or service availability in distributed systems.

    Attributes:
        ssh (Ssh): An instance of the SSH wrapper class used to execute remote shell commands.
        logger (Logger | LoggerAdapter): Logger used to emit informational and debug logs.
    """

    HTTP_SERVER_COMMAND = "python3 -m http.server"

    def __init__(
        self,
        logger: Optional[Union[logging.Logger, logging.LoggerAdapter]] = None,
        ssh: Optional[Ssh] = None,
    ):
        """
        Initializes the RemoteHttpServerManager utility.

        This manager is responsible for controlling HTTP servers on remote machines via SSH.
        An existing SSH session can be injected to share connection state across components.

        Args:
            logger (Logger | LoggerAdapter | None): Optional custom logger instance for logging internal operations.
            ssh (Ssh | None): Optional existing Ssh instance. If not provided, a new Ssh object will be created.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.ssh = ssh or Ssh(logger=self.logger)

    def close_http_server(
        self,
        server_port: int = 8000,
    ) -> bool:
        """
        Attempt to terminate any running HTTP server process on the specified port.
    
        This method remotely connects to the server via SSH and uses `pkill` to stop
        any background HTTP server process (started via `python3 -m http.server`)
        that matches the given port. If the termination succeeds, it returns True.
        Otherwise, logs the error and returns False.
    
        Args:
            server_port (int): The port on which the HTTP server is expected to run.
                               Default is 8000.
    
        Returns:
            bool: True if the server was successfully terminated, False if an exception occurred.
        """
        try:
            self.logger.info(
                f"Attempting to close any existing HTTP server on port {server_port}..."
            )
            self.ssh.send_command_in_shell(
                f'pkill -f "{self.HTTP_SERVER_COMMAND} {server_port}"'
            )
            return True
    
        except Exception as e:
            self.logger.error(f"Failed to close HTTP server: {e}")
            return False

    def prepare_http_server(
        self,
        server_name: str,
        server_port: int = 8000,
        log_path: str = "/tmp/http_server.log",
    ) -> bool:
        """
        Prepare the remote server for HTTP service:
        - Set index.html with server identifier
        - Kill any existing HTTP server
        - Clear existing log file
        - Launch new HTTP server in background using nohup

        Args:
            server_name (str): Identifier for the current HTTP server
            server_port (int): Port for http.server (default: 8000)
            log_path (str): Path to the log file to reset

        Returns:
            bool: True if server is successfully launched, False otherwise.
        """
        try:
            self.logger.info(
                f"Preparing HTTP server for '{server_name}' on port {server_port}..."
            )

            self.logger.info("Creating index.html with server identity...")
            self.ssh.send_command_in_shell(
                f'echo "Hello from {server_name}" > ~/index.html'
            )

            self.close_http_server(server_port=8000)

            self.logger.info(
                f"Clearing existing HTTP server log at: {log_path} ..."
            )
            self.ssh.send_command_in_shell(f'echo "" > {log_path}')

            self.logger.info("Launching new HTTP server in background...")
            launch_cmd = (
                f"nohup {self.HTTP_SERVER_COMMAND} {server_port} "
                f"--directory ~ > {log_path} 2>&1 &"
            )
            self.ssh.send_command_in_shell(launch_cmd)

            self.logger.info(
                f"HTTP server started successfully on port {server_port}. Logs at: {log_path}"
            )
            self.logger.info(
                "Remote HTTP server environment prepared successfully."
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to prepare HTTP server: {e}")
            return False
            

    def get_server_log(
        self,
        server_name: str,
        lines: int = 10,
        log_path: str = "/tmp/http_server.log",
    ) -> None:
        """
        Retrieve and log the last N lines from a remote server's log file.

        Connects to the remote server via SSH, reads the tail of the specified log file,
        and logs the result for debugging or monitoring purposes.

        Args:
            server_name (str): A human-readable name or label for the server.
            lines (int): Number of lines to fetch from the end of the log file. Default is 10.
            log_path (str): Full path to the remote server's log file. Default is '/tmp/http_server.log'.

        Returns:
            None
        """
        log = self.ssh.send_command_in_shell(f"tail -n {lines} {log_path}")
        self.logger.info(f"{server_name}'s log:\n{log}")
