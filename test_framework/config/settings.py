from dataclasses import dataclass


@dataclass(frozen=True)
class ServerConfig:
    """
    Immutable connection parameters for a single server.

    Used as the base configuration block across all test suites.
    """

    name: str
    host: str
    username: str
    password: str
    port: int = 22
