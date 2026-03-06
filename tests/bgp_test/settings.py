import os
from test_framework.config.settings import ServerConfig


SERVER_ONE_CONFIG = ServerConfig(
    name=os.getenv("SERVER1_NAME", "T8164_1"),
    host=os.getenv("SERVER1_HOST", "10.135.179.247"),
    username=os.getenv("SERVER1_USERNAME", "admin"),
    password=os.getenv("SERVER1_PASSWORD", "YourPaSsWoRd"),
    port=int(os.getenv("SERVER1_PORT", "22")),
)

SERVER_TWO_CONFIG = ServerConfig(
    name=os.getenv("SERVER2_NAME", "T8164_2"),
    host=os.getenv("SERVER2_HOST", "10.135.176.52"),
    username=os.getenv("SERVER2_USERNAME", "admin"),
    password=os.getenv("SERVER2_PASSWORD", "YourPaSsWoRd"),
    port=int(os.getenv("SERVER2_PORT", "22")),
)
