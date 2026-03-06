import os
from test_framework.config.settings import ServerConfig


SERVER_ONE_CONFIG = ServerConfig(
    name=os.getenv("SERVER1_NAME", "server1"),
    host=os.getenv("SERVER1_HOST", "192.168.56.11"),
    username=os.getenv("SERVER1_USERNAME", "server1"),
    password=os.getenv("SERVER1_PASSWORD", "11111111"),
    port=int(os.getenv("SERVER1_PORT", "22")),
)

SERVER_TWO_CONFIG = ServerConfig(
    name=os.getenv("SERVER2_NAME", "server2"),
    host=os.getenv("SERVER2_HOST", "192.168.56.12"),
    username=os.getenv("SERVER2_USERNAME", "server2"),
    password=os.getenv("SERVER2_PASSWORD", "11111111"),
    port=int(os.getenv("SERVER2_PORT", "22")),
)

CLIENT_ONE_CONFIG = ServerConfig(
    name=os.getenv("CLIENT1_NAME", "client1"),
    host=os.getenv("CLIENT1_HOST", "192.168.56.21"),
    username=os.getenv("CLIENT1_USERNAME", "client1"),
    password=os.getenv("CLIENT1_PASSWORD", "11111111"),
    port=int(os.getenv("CLIENT1_PORT", "22")),
)
