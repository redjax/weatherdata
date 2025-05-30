ARG UV_BASE=${UV_IMAGE_VER:-0.6.3}
ARG PYTHON_BASE=${PYTHON_IMG_VER:-3.11-slim}

FROM ghcr.io/astral-sh/uv:${UV_BASE} AS uv
FROM python:${PYTHON_BASE} AS base

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
    build-essential \
    iputils-ping \
    libmemcached-dev \
    zlib1g-dev \
    curl \
    ca-certificates \
    software-properties-common \
    apt-transport-https \
    sudo \
    postgresql \
    python3-psycopg2 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN mkdir -p /project /weatherdata/db /weatherdata/logs

## Staging
FROM base AS stage

WORKDIR /project

COPY --from=base /weatherdata /weatherdata

COPY pyproject.toml uv.lock README.md ./

## Copy monorepo domains
COPY applications/ applications/
COPY migrations/ migrations/
COPY packages/ packages/
COPY scripts/ scripts/

## Build
FROM stage AS build

COPY --from=stage /project /project
COPY --from=stage /weatherdata /weatherdata
COPY --from=uv /uv /usr/bin/uv

WORKDIR /project

## Build project in container
RUN uv sync --all-extras \
    && uv build

## DB migrations
FROM build AS alembic_migrate

COPY --from=build /project /project
COPY --from=build /weatherdata /weatherdata
COPY --from=uv /uv /usr/bin/uv

WORKDIR /project

RUN uv pip install alembic
CMD ["/bin/bash", "-c", "uv run alembic stamp head ; uv run alembic upgrade head"]

## Celery Beat
FROM build AS celery_beat

COPY --from=build /project /project
COPY --from=build /weatherdata /weatherdata
COPY --from=uv /uv /usr/bin/uv

WORKDIR /project

CMD ["uv", "run", "scripts/celery/start_celery.py", "-m", "beat"]

## Celery Worker

FROM build AS celery_worker

COPY --from=build /project /project
COPY --from=build /weatherdata /weatherdata
COPY --from=uv /uv /usr/bin/uv

WORKDIR /project

CMD ["uv", "run", "scripts/celery/start_celery.py", "-m", "worker"]
