# test automation framework

An end-to-end automated testing framework.
This project leverages pytest, and Allure to ensure high-quality, maintainable test automation with clear reporting and modular architecture.

## Project Structure
```
/
├── .devcontainer/
│   ├── devcontainer.json
│   └── Dockerfile
├── test_framework/
│   ├── base/
│   │   └── abstract_test_base.py
│   ├── core/ (None)
│   ├── reporting/
│   │   └── allure_report_helpers.py
│   ├── utils/
│   │   ├── decorators.py
│   │   ├── assertions.py
│   │   ├── remote_http.py
│   │   ├── apv_helpers.py
│   │   ├── ssh_helpers.py
│   │   ├── cli_helpers.py
│   │   ├── playwright_helpers.py
│   │   └── logger.py
│   └── config/
│       └── settings.py (None)
├── tests/
│   ├── config/
│   │   └── settings.py
│   ├── demo_test/
│   │   ├── conftest.py
│   │   ├── settings.py
│   │   └── test_demo.py
│   └──  web_test/
│       ├── conftest.py
│       ├── settings.py
│       └── test_web_demo.py.py
├── logs/
├── artifacts/
├── reports/
│   ├── allure-results/
│   └── allure-report/
├── run_test.sh
├── Jenkinsfile
├── pytest.ini
├── pyproject.toml
├── .gitattributes
├── .gitignore
├── .dockerignore
├── requirements.txt
└── README.md
```
## Prerequisites 

1. Install Visual Studio Code
https://code.visualstudio.com/

2. Install Git Bash (for Windows users)
https://gitforwindows.org/

### Setup Options

### Option A — Using Docker
1. Install Docker Desktop
https://www.docker.com/products/docker-desktop

2. Install VSCode extension Dev Containers

3. Click on Hype-V service on Windows10/11

### Option B — Without Docker
1. Open Git Bash (Windows) or Terminal (Mac/Linux)
`pip install --no-cache-dir -r requirements.txt`

## Running Tests

To run all test cases:
`./run_test.sh`

To run a specific test case by function name:
`./run_test.sh test_case_name`

To run a group of test cases by class name:
`./run_test.sh TestDemo`

To run a group of test cases by file name:
`./run_test.sh test_demo.py`

To run multiple test cases by function names:
`./run_test.sh test_case_name test_case_name_01 test_case_name_02`

After test execution, open the Allure report at:
`http://localhost:8180`

(You can change the port number in run_test.sh)
