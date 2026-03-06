> **Author**: Jacky 辛介宇
> **Role**: Developer & Maintainer
> **Contact**: wohenhow1999@gmail.com

# Test Automation Framework

A pytest-based test automation framework designed for L2/L3 network switch validation (SONiC).
Integrates Allure reporting, SSH device control, CLI execution, and web automation with a clean layered architecture.

---

## Project Structure

```
/
├── .devcontainer/
│   ├── devcontainer.json
│   └── Dockerfile
├── test_framework/                 # Framework core — do not modify per test
│   ├── base/
│   │   └── abstract_test_base.py  # Base class for all test classes
│   ├── reporting/
│   │   └── allure_report_helpers.py
│   ├── utils/
│   │   ├── assertions.py          # Assertion utilities with logging
│   │   ├── ssh_helpers.py         # SSH / SONiC device control
│   │   ├── cli_helpers.py         # Local shell command execution
│   │   ├── playwright_helpers.py  # Web browser automation
│   │   └── logger.py              # Centralized logger
│   └── config/
│       └── settings.py            # Shared config dataclasses (ServerConfig)
├── tests/
│   ├── conftest.py                # Shared pytest hooks (Allure log attachment)
│   ├── config/
│   │   └── settings.py            # Global test metadata (executor name, etc.)
│   ├── demo_test/
│   │   ├── settings.py
│   │   └── test_demo.py
│   ├── api_test/
│   │   ├── settings.py
│   │   └── test_api_demo.py
│   ├── web_test/
│   │   ├── settings.py
│   │   └── test_web_demo.py
│   └── bgp_test/
│       └── settings.py
├── logs/
├── reports/
│   ├── allure-results/
│   └── allure-report/
├── Jenkinsfile
├── pytest.ini
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Architecture

### Layered Design

```
tests/                  <- Test suites (one folder per feature)
    conftest.py         <- Shared hooks applied to all test folders
    <suite>/
        settings.py     <- Device configs for this suite
        test_*.py       <- Test cases

test_framework/         <- Framework core (stable, rarely changed)
    base/               <- AbstractTestBase lifecycle management
    utils/              <- SSH, CLI, Playwright, Assertions, Logger
    reporting/          <- Allure helpers
    config/             <- Shared dataclasses
```

### AbstractTestBase

All test classes inherit from `AbstractTestBase`, which provides:

- **Lifecycle hooks**: `setup_method` / `teardown_method` with `@pytest.mark.no_setup` / `@pytest.mark.no_teardown` skip markers
- **Lazy utilities via `cached_property`**: `self.ssh`, `self.cli`, `self.assertion`, `self.allure`, `self.playwright` — only instantiated when accessed
- **Automatic resource cleanup**: `playwright` and `ssh` are automatically closed after each test
- **Per-test logger**: Each test method gets a context-aware logger (`ClassName.method_name()`)

```python
class TestBgp(AbstractTestBase):

    @classmethod
    def get_test_case_catalog(cls):
        return {
            "TC-001": {"test_function_name": cls.test_bgp_neighbor, "description": "..."},
        }

    def setup(self):
        self.ssh.connect_shell(
            SERVER_ONE_CONFIG.host,
            SERVER_ONE_CONFIG.username,
            SERVER_ONE_CONFIG.password,
        )

    def teardown(self):
        pass  # ssh.disconnect() is called automatically by the framework

    def test_bgp_neighbor(self):
        with self.allure.step_with_log("Enter Klish and check BGP neighbors"):
            self.ssh.enter_klish()
            output = self.ssh.send_klish_command("show bgp summary")
            self.assertion.assert_in("Established", output)
```

---

## SSH Module — SONiC Device Control

Designed for SONiC switches with two CLI contexts:

| Context | Prompt | Helper method |
|---------|--------|---------------|
| Linux shell (Click CLI) | `admin@sonic:~$` | `send_shell_command()` |
| Klish CLI | `sonic#` | `send_klish_command()` |
| Klish config mode | `sonic(config)#` | `send_klish_command()` |

Uses **prompt-based reading** (not fixed `sleep`) — reads continuously until the device prompt appears, making tests fast and reliable regardless of device response time.

### SSH API

```python
# Connection
ssh.connect_shell(hostname, username, password, port=22, timeout=10)
ssh.disconnect()

# Click CLI (Linux shell)
output = ssh.send_shell_command("show ip route")

# Klish
ssh.enter_klish()
output = ssh.send_klish_command("show version")

# Config mode
ssh.configure()
ssh.send_klish_command("interface GigabitEthernet0/1")
ssh.send_klish_command("ip address 10.0.0.1/30")
ssh.exit_config()   # one level up
ssh.end()           # back to sonic# directly

ssh.exit_klish()
```

---

## Device Configuration

Each test suite defines its own `settings.py` using `ServerConfig` from the framework.
Values are loaded from environment variables with fallback defaults for local development.

```python
# tests/bgp_test/settings.py
import os
from test_framework.config.settings import ServerConfig

SERVER_ONE_CONFIG = ServerConfig(
    name=os.getenv("SERVER1_NAME", "T8164_1"),
    host=os.getenv("SERVER1_HOST", "10.135.179.247"),
    username=os.getenv("SERVER1_USERNAME", "admin"),
    password=os.getenv("SERVER1_PASSWORD", "YourPaSsWoRd"),
    port=int(os.getenv("SERVER1_PORT", "22")),
)
```

---

## Prerequisites

1. Install Visual Studio Code — https://code.visualstudio.com/
2. Install Git Bash (Windows users) — https://gitforwindows.org/

### Option A — Docker (Recommended)

1. Install Docker Desktop — https://www.docker.com/products/docker-desktop
2. Install VSCode extension **Dev Containers**
3. Enable Hyper-V on Windows 10/11
4. Open project in Dev Container

### Option B — Local

```bash
pip install --no-cache-dir -r requirements.txt
```

---

## Running Tests

```bash
# All tests
./run_test.sh

# By function name
./run_test.sh test_bgp_neighbor

# By class name
./run_test.sh TestBgp

# By file name
./run_test.sh test_bgp.py

# Multiple functions
./run_test.sh test_case_a test_case_b
```

Allure report available at `http://localhost:8180` after execution.
(Port can be changed in `run_test.sh`)

---

## Demo Results

**[Click here to open the demo Allure Report](https://wohenhow1999.github.io/allure_demo_report/)**
