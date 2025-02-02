#!/bin/bash

## Check if "--debug" is present in the arguments
DEBUG=false
for arg in "$@"; do
    if [[ "$arg" == "--debug" ]]; then
        DEBUG=true
        break
    fi
done

## Debugging function
debug() {
    if [[ "$DEBUG" == "true" ]]; then
        echo "[DEBUG] $*"
    fi
}

## Remove "--debug" from arguments for processing
ARGS=()
for arg in "$@"; do
    if [[ "$arg" != "--debug" ]]; then
        ARGS+=("$arg")
    fi
done

function debug() {
    ## Show a message, only if a --debug parameter was
    #  passed to the script.
    #  Usage:
    #    debug "Your message to debug, with ${VARIABLES} and $? codes, etc."
    if [[ "$DEBUG" == "true" ]]; then
        echo "[DEBUG] $*"
    fi
}

CWD=$(pwd)
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT=$(cd "${THIS_DIR}/../.." && pwd)
CONTAINERS_DIR="${REPO_ROOT}/containers"
COMPOSE_FILE="dev.compose.yml"
COMPOSE_FILE_PATH="${CONTAINERS_DIR}/${COMPOSE_FILE}"

debug "CWD: $CWD"
debug "Script path: ${THIS_DIR}"
debug "Repo root path: ${REPO_ROOT}"
debug "Containers path: $CONTAINERS_DIR"
debug "Docker Compose file path: ${COMPOSE_FILE_PATH}"

function run_compose() {
    ## Helper function to run Docker Compose commands

    if [[ ! -f $COMPOSE_FILE_PATH ]]; then
        echo "[WARNING] Could not find Compose file at '$COMPOSE_FILE_PATH'"
        exit
    else
        echo "Compose file found at path: ${COMPOSE_FILE_PATH}"
    fi

    debug "Running Docker Compose command: $*"
    docker compose -f "${COMPOSE_FILE_PATH}" "$@"
}

if ! command -v docker > /dev/null 2>&1; then
    echo "[WARNING] Docker is not installed. Exiting."
    exit 1
fi

if ! command -v docker compose > /dev/null 2>&1; then
    echo "[WARNING] Docker Compose is not installed. Exiting."
    exit 1
fi

case "$1" in
    up)
        if [[ "$2" == "build" ]]; then
            echo "Building Compose stack & running containers"
            run_compose up -d --build
        else
            echo "Running Compose stack"
            run_compose up -d
        fi
        ;;
    build)
        echo "Build Compose stack"
        run_compose build
        ;;
    down)
        echo "Bring down Compose stack"
        run_compose down
        ;;
    logs)
        ## Capture everything after "logs" as container name
        CONTAINER_NAME="${ARGS[@]:1}" # Get all arguments after "logs"
        if [[ -z "$CONTAINER_NAME" ]]; then
            echo "Usage: $0 logs <container_name> [--debug]"
            exit 1
        fi
        debug "Fetching logs for container: $CONTAINER_NAME"
        run_compose logs -f "$CONTAINER_NAME"
        ;;
    restart)
        ## Capture all arguments after "restart"
        CONTAINERS=("${ARGS[@]:1}") 
        if [[ -z "${CONTAINERS[*]}" ]]; then
            echo "Usage: $0 restart {all|<container_name> ...} [--debug]"
            exit 1
        fi

        if [[ "${CONTAINERS[0]}" == "all" ]]; then
            debug "Restarting all containers"
            run_compose restart
        else
            for container in "${CONTAINERS[@]}"; do
                debug "Restarting container: $container"
                run_compose restart "$container"
            done
        fi
        ;;
    *)
        echo "Usage: $0 {logs|build|up [build]|down}"
        exit 1
        ;;
esac
