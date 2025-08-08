from functools import wraps
import paramiko
import time
import logging
import pytest
from typing import Callable
from tests.config.settings import JumpServerConfig


class Decorator:
    """
    Provides a collection of static decorators for enhancing class methods,
    particularly focusing on network-related functionalities.

    This class centralizes reusable logic (e.g., SSH jump host handling)
    that can be applied across different connection or communication methods,
    promoting code reusability, modularity, and clean separation of concerns.
    """

    @staticmethod
    def use_jump_host(jump_config: JumpServerConfig) -> Callable:
        """
        A decorator factory for establishing SSH connections via a jump host.
        This decorator wraps a connection function, orchestrating the multi-hop
        SSH process: connecting to the jump server, creating a direct TCP/IP
        channel, and then using that channel to connect to the final target host.
        It ensures proper resource management by attaching SSH clients to the
        instance for later teardown.
        Args:
            jump_config (JumpServerConfig): Immutable configuration for the jump server,
                                            including host, username, password, and port.
        Returns:
            Callable: A decorator that wraps the target connection function.
        """

        def decorator(connect_func: Callable) -> Callable:
            @wraps(connect_func)
            def wrapper(
                self,
                hostname: str,
                username: str,
                password: str,
                port: int = 22,
                timeout: int = 10,
            ):
                logger = getattr(self, "logger", logging.getLogger(__name__))

                jump_host = jump_config.server.host
                jump_user = jump_config.server.username
                jump_pass = jump_config.server.password
                jump_port = jump_config.server.port

                logger.info(
                    f"Connecting to jump host {jump_host}:{jump_port}..."
                )
                ssh_jump = paramiko.SSHClient()
                ssh_jump.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                try:
                    ssh_jump.connect(
                        hostname=jump_host,
                        username=jump_user,
                        password=jump_pass,
                        port=jump_port,
                        timeout=timeout,
                    )
                    logger.info("SSH to jump host succeeded.")
                    # Attach the jump client to self so it can be closed during teardown.
                    self.jump_client = ssh_jump
                except Exception as e:
                    logger.error(f"SSH to jump host failed: {e}")
                    pytest.fail(f"SSH to jump host failed: {e}")

                logger.info(f"Opening tunnel to target {hostname}:{port}...")
                try:
                    jump_transport = self.jump_client.get_transport()
                    dest_addr = (hostname, port)
                    local_addr = ("", 0)
                    channel = jump_transport.open_channel(
                        "direct-tcpip", dest_addr, local_addr
                    )
                except Exception as e:
                    self.jump_client.close()
                    logger.error(f"Failed to open jump channel: {e}")
                    pytest.fail(f"Failed to open jump channel: {e}")

                logger.info(
                    f"Connecting to target host {hostname} via jump host..."
                )
                self.client = paramiko.SSHClient()
                self.client.set_missing_host_key_policy(
                    paramiko.AutoAddPolicy()
                )

                try:
                    self.client.connect(
                        hostname=hostname,
                        username=username,
                        password=password,
                        port=port,
                        timeout=timeout,
                        sock=channel,
                    )
                    logger.info("SSH to target host via jump host succeeded.")
                except Exception as e:
                    logger.error(
                        f"SSH to target host via jump host failed: {e}"
                    )
                    self.jump_client.close()
                    pytest.fail(
                        f"SSH to target host via jump host failed: {e}"
                    )

                logger.info("Attempting to open interactive SSH shell...")
                try:
                    self.shell = self.client.invoke_shell()
                    time.sleep(1)
                    if not self.shell:
                        raise Exception("invoke_shell() returned None")
                except Exception as e:
                    logger.error(
                        f"Exception occurred while opening interactive shell: {e}"
                    )
                    pytest.fail(f"Failed to start shell session: {e}")

                logger.info("SSH interactive shell established via jump host.")

            return wrapper

        return decorator
