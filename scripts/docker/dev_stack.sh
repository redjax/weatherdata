#!/bin/bash
set -euo pipefail

## Defaults: all overlays ON except db_init
INCLUDE_CELERY=true
INCLUDE_ALEMBIC=true
INCLUDE_DB=true
INCLUDE_MESSAGING=true
INCLUDE_DB_INIT=false
DEBUG=false

if ! command -v docker &>/dev/null; then
    echo "[ERROR] Docker is not installed. Exiting."
    exit 1
fi

if ! command -v docker compose &>/dev/null; then
    echo "[ERROR] Docker Compose is not installed. Exiting."
    exit 1
fi

function print_help {
    echo "Usage: $0 [--no-celery] [--no-alembic] [--no-db] [--no-messaging] [--db-init]"
    echo ""
    echo "Options:"
    echo "  --no-celery       Disable Celery"
    echo "  --no-alembic      Disable Alembic"
    echo "  --no-db           Disable Postgres"
    echo "  --no-messaging    Disable RabbitMQ"
    echo "  --db-init         Include DB init script"
    echo ""
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-celery)
            INCLUDE_CELERY=false
            ;;
        --no-alembic)
            INCLUDE_ALEMBIC=false
            ;;
        --no-db)
            INCLUDE_DB=false
            ;;
        --no-messaging)
            INCLUDE_MESSAGING=false
            ;;
        --db-init)
            INCLUDE_DB_INIT=true
            ;;
        --debug)
            DEBUG=true
            ;;
        -h|--help)
            print_help
            exit 0
        *)
            echo "Unknown option: $1"
            print_help

            exit 1
            ;;
    esac
    shift
done

## Base compose files (relative to repo root)
COMPOSE_ARGS="-f containers/compose.yml"

if $INCLUDE_CELERY; then
    COMPOSE_ARGS+=" -f containers/overlays/celery-beat.yml -f containers/overlays/celery-worker.yml"
fi
if $INCLUDE_ALEMBIC; then
    COMPOSE_ARGS+=" -f containers/overlays/alembic-migrate.yml"
fi
if $INCLUDE_DB; then
    COMPOSE_ARGS+=" -f containers/overlays/postgres.yml"
fi
if $INCLUDE_MESSAGING; then
    COMPOSE_ARGS+=" -f containers/overlays/redis.yml -f containers/overlays/redis-commander.yml -f containers/overlays/rabbitmq.yml"
fi
if $INCLUDE_DB_INIT; then
    COMPOSE_ARGS+=" -f containers/overlays/db_init.yml"
fi

export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-devstack}"

## Ensure we run from repo root no matter where this script is called from
cd "$(git rev-parse --show-toplevel)"

## Launch stack
docker compose $COMPOSE_ARGS --env-file containers/.env up
