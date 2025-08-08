from dataclasses import dataclass
import os


@dataclass(frozen=True)
class MetaConfig:
    """
    Immutable metadata configuration for test context.

    Stores static information about who or what is executing the tests.
    Useful for Allure report metadata like executor name, build info, etc.
    """

    test_executor: str

    @classmethod
    def load_config(cls) -> "MetaConfig":
        """
        Load test metadata configuration.

        Returns:
            MetaConfig: An object containing test executor info.
        """
        test_executor = "Jacky2522561"
        return cls(test_executor)


@dataclass(frozen=True)
class ServerConfig:
    """
    Immutable single server configuration.

    Represents basic connection parameters for a single server,
    including name, host, username, password, and port.
    Useful as a reusable building block for specific test configurations.
    """

    name: str
    host: str
    username: str
    password: str
    port: 22


@dataclass(frozen=True)
class JumpServerConfig:
    """
    Immutable jump server configuration for test context.

    Used when a jump server is required to access internal network resources.
    Provides an isolated ServerConfig for the jump server.
    """

    server: ServerConfig

    @classmethod
    def load_config(cls) -> "JumpServerConfig":
        """
        Load jump server configuration from environment variables with defaults.

        Returns:
            JumpServerConfig: A configuration object containing jump server info.
        """

        def load_server(prefix: str) -> "ServerConfig":
            return ServerConfig(
                name=os.getenv(f"{prefix}_NAME", "GD"),
                host=os.getenv(f"{prefix}_HOST", "192.168.10.73"),
                username=os.getenv(f"{prefix}_USERNAME", "auto100"),
                password=os.getenv(f"{prefix}_PASSWORD", "11111111"),
                port=int(os.getenv(f"{prefix}_PORT", "22")),
            )

        return cls(server=load_server("JUMP_SERVER"))


@dataclass(frozen=True)
class APVServerConfig:
    """
    Immutable APV server configuration for test context.

    Represents the connection information required to reach an APV device.
    Often used in L4/L7 or load balancer integration tests.
    """

    server: ServerConfig

    @classmethod
    def load_config(cls) -> "APVServerConfig":
        """
        Load APV server configuration from environment variables with defaults.

        Returns:
            APVServerConfig: A configuration object containing APV server info.
        """

        def load_server(prefix: str) -> "ServerConfig":
            return ServerConfig(
                name=os.getenv(f"{prefix}_NAME", "APV"),
                host=os.getenv(f"{prefix}_HOST", "192.168.56.51"),
                username=os.getenv(f"{prefix}_USERNAME", "array"),
                password=os.getenv(f"{prefix}_PASSWORD", "admin"),
                port=int(os.getenv(f"{prefix}_PORT", "22")),
            )

        return cls(server=load_server("APV"))


@dataclass(frozen=True)
class ServerOneConfig:
    """
    Immutable configuration for Server 1 in test topology.
    """

    server: ServerConfig

    @classmethod
    def load_config(cls) -> "ServerOneConfig":
        """
        Load Server 1 configuration from environment variables with defaults.

        Returns:
            ServerOneConfig: A configuration object containing server1 info.
        """

        def load_server(prefix: str) -> "ServerConfig":
            return ServerConfig(
                name=os.getenv(f"{prefix}_NAME", "server1"),
                host=os.getenv(f"{prefix}_HOST", "192.168.56.11"),
                username=os.getenv(f"{prefix}_USERNAME", "server1"),
                password=os.getenv(f"{prefix}_PASSWORD", "11111111"),
                port=int(os.getenv(f"{prefix}_PORT", "22")),
            )

        return cls(server=load_server("SERVER1"))


@dataclass(frozen=True)
class ServerTwoConfig:
    """
    Immutable configuration for Server 2 in test topology.
    """

    server: ServerConfig

    @classmethod
    def load_config(cls) -> "ServerTwoConfig":
        """
        Load Server 2 configuration from environment variables with defaults.

        Returns:
            ServerTwoConfig: A configuration object containing server2 info.
        """

        def load_server(prefix: str) -> "ServerConfig":
            return ServerConfig(
                name=os.getenv(f"{prefix}_NAME", "server2"),
                host=os.getenv(f"{prefix}_HOST", "192.168.56.12"),
                username=os.getenv(f"{prefix}_USERNAME", "server2"),
                password=os.getenv(f"{prefix}_PASSWORD", "11111111"),
                port=int(os.getenv(f"{prefix}_PORT", "22")),
            )

        return cls(server=load_server("SERVER2"))


@dataclass(frozen=True)
class ClientOneConfig:
    """
    Immutable configuration for Client 1 in test topology.
    """

    server: ServerConfig

    @classmethod
    def load_config(cls) -> "ClientOneConfig":
        """
        Load Client 1 configuration from environment variables with defaults.

        Returns:
            ClientOneConfig: A configuration object containing client1 info.
        """

        def load_server(prefix: str) -> "ServerConfig":
            return ServerConfig(
                name=os.getenv(f"{prefix}_NAME", "client1"),
                host=os.getenv(f"{prefix}_HOST", "192.168.56.21"),
                username=os.getenv(f"{prefix}_USERNAME", "client1"),
                password=os.getenv(f"{prefix}_PASSWORD", "11111111"),
                port=int(os.getenv(f"{prefix}_PORT", "22")),
            )

        return cls(server=load_server("CLIENT1"))


# global singleton
META_CONFIG = MetaConfig.load_config()
JUMP_SERVER_CONFIG = JumpServerConfig.load_config()
APV_SERVER_CONFIG = APVServerConfig.load_config()
SERVER_ONE_CONFIG = ServerOneConfig.load_config()
SERVER_TWO_CONFIG = ServerTwoConfig.load_config()
CLIENT_ONE_CONFIG = ClientOneConfig.load_config()
