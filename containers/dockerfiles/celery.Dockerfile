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
        curl \
        ca-certificates \
        software-properties-common \
        apt-transport-https \
        sudo \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

## Create container user
RUN groupadd -g 1001 appuser \
    && useradd -m -u 1001 -g appuser appuser \
    && echo "appuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN mkdir -p /project /weatherdata/db /weatherdata/logs

RUN chown -R appuser:appuser /project /weatherdata \
    && chmod -R 777 /weatherdata/db

FROM base AS stage

WORKDIR /project
USER appuser

COPY --from=base /weatherdata /weatherdata

COPY pyproject.toml uv.lock README.md ./
COPY containers/entrypoints/dev.entrypoint.sh /usr/local/bin/docker-entrypoint.sh

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
COPY --from=stage /usr/local/bin/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

USER root
RUN chown -R appuser:appuser /project /weatherdata \
    && chmod -R 777 /weatherdata/db

ENTRYPOINT [ "sudo", "/usr/local/bin/docker-entrypoint.sh" ]

WORKDIR /project
USER appuser

CMD ["uv", "run", "scripts/celery/start_celery.py", "-m", "beat"]

FROM build AS celery_worker

COPY --from=build /project /project
COPY --from=build /weatherdata /weatherdata
COPY --from=stage /usr/local/bin/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

USER root
# RUN chown appuser:appuser /usr/local/bin/docker-entrypoint.sh \
#     && chmod u+x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT [ "sudo", "/usr/local/bin/docker-entrypoint.sh" ]

WORKDIR /project
USER appuser

CMD ["uv", "run", "scripts/celery/start_celery.py", "-m", "worker"]
