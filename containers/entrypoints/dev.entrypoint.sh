#!/bin/bash

## Ensure app dir permissions
echo "Setting owner of /project, /weatherdata"
chown -R appuser:appuser /project /weatherdata

if [[ $? -ne 0 ]]; then
    echo "[ERROR] An error occurred during Docker entrypoint startup."
    exit $?
else
    echo "Docker init script finished, starting container."
    ## Continue with Docker command execution
    exec "$@"
fi
