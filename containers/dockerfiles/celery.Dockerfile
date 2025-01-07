ARG UV_BASE=${UV_IMAGE_VER:-0.5.9}
ARG PYTHON_BASE=${PYTHON_IMG_VER:-3.12-slim}

FROM ghcr.io/astral-sh/uv:${UV_BASE} AS uv
FROM python:${PYTHON_BASE} AS base

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        build-essential \
        iputils-ping \
        libmemcached-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

## Create container user
RUN groupadd -g 1001 appuser \
    && useradd -m -u 1001 -g appuser appuser

RUN mkdir -p /project /weatherdata \
    && chown -R appuser:appuser /project \
    && chown -R appuser:appuser /weatherdata

FROM base AS stage

WORKDIR /project
USER appuser

COPY --from=base /weatherdata /weatherdata

COPY pyproject.toml uv.lock README.md ./

## Copy monorepo domains
COPY applications/ applications/
COPY packages/ packages/
COPY scripts/ scripts/
COPY src/ src/

FROM stage AS build

COPY --from=stage /project /project
COPY --from=stage /weatherdata /weatherdata
COPY --from=uv /uv /usr/bin/uv

WORKDIR /project
USER appuser

## Build project in container
RUN uv sync --all-extras \
    && uv build

FROM build AS celery_beat

COPY --from=build /project /project
COPY --from=build /weatherdata /weatherdata
COPY --from=uv /uv /usr/bin/uv

WORKDIR /project
USER appuser

CMD ["uv", "run", "scripts/celery/start_celery.py", "-m", "beat"]

FROM build AS celery_worker

COPY --from=build /project /project
COPY --from=uv /uv /usr/bin/uv

WORKDIR /project
USER appuser

CMD ["uv", "run", "scripts/celery/start_celery.py", "-m", "worker"]
