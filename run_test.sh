#!/bin/bash
export TZ=Asia/Taipei
timestamp=$(date +"%Y%m%d%H%M")
RESULT_DIR="reports/allure-results"
REPORT_BASE="reports/allure-report-${timestamp}"
PORT=5666

PYTEST_COMMAND="pytest -s"
NODE_IDS=""

echo ">>> Files inside container at /app:"
ls -R /app

if [ $# -eq 0 ]; then
    echo "No specific test case provided. Running all tests."
else
    echo "🔍 Searching test target(s): $*"

    for target in "$@"; do
        FOUND_MATCH=0

        # file level
        FILE_PATH=$(find tests -type f -name "${target}")
        if [[ -n "$FILE_PATH" ]]; then
            echo "✅ Found file: ${FILE_PATH}"
            NODE_IDS="${NODE_IDS} ${FILE_PATH}"
            FOUND_MATCH=1
            continue
        fi

        # class level
        while IFS= read -r file; do
            if grep -qP "^\s*class\s+${target}\b" "$file"; then
                NODE_ID="${file}::${target}"
                echo "✅ Found class: ${NODE_ID}"
                NODE_IDS="${NODE_IDS} ${NODE_ID}"
                FOUND_MATCH=1
                break
            fi

            # function level
            CURRENT_CLASS=""
            while IFS= read -r line; do
                if [[ "$line" =~ ^class[[:space:]]+([A-Za-z_][A-Za-z0-9_]*) ]]; then
                    CURRENT_CLASS="${BASH_REMATCH[1]}"
                fi

                if [[ "$line" =~ ^[[:space:]]*def[[:space:]]+${target}[[:space:]]*\( ]]; then
                    if [[ -n "$CURRENT_CLASS" ]]; then
                        NODE_ID="${file}::${CURRENT_CLASS}::${target}"
                        echo "✅ Found method in class: ${NODE_ID}"
                    else
                        NODE_ID="${file}::${target}"
                        echo "✅ Found top-level function: ${NODE_ID}"
                    fi
                    NODE_IDS="${NODE_IDS} ${NODE_ID}"
                    FOUND_MATCH=1
                    break
                fi
            done < "$file"

            if [ $FOUND_MATCH -eq 1 ]; then
                break
            fi
        done < <(find tests -type f -name "test_*.py")

        if [ $FOUND_MATCH -eq 0 ]; then
            echo "❌ Cannot find function, class, or file: ${target}"
            exit 1
        fi
    done

    PYTEST_COMMAND="${PYTEST_COMMAND} ${NODE_IDS}"
fi

eval ${PYTEST_COMMAND}
chmod -R 777 "${RESULT_DIR}"
# allure generate "${RESULT_DIR}" -o "${REPORT_BASE}" --clean
# allure open "${REPORT_BASE}" --port "${PORT}" --host 0.0.0.0