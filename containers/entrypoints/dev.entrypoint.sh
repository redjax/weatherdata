#!/bin/bash

## Ensure app dir permissions
chown -R appuser:appuser /project /weatherdata # \
    # && chmod -R 700 /weatherdata/db \
    # && chmod -R 700 /weatherdata/logs

if [[ $? -ne 0 ]]; then
    echo "[ERROR] An error occurred during Docker entrypoint startup."
    exit $?
else
    echo "Starting container."
    ## Continue with Docker command execution
    exec "$@"
fi
