# Containers

The Docker Compose stack for the app. The `dev.compose.yml` file spins up a local redis + redis-commander + rabbitmq stack, but does not run the Python app.

## How to run

### Local dev environment

From the root of the git repository, run `docker compose -f ./containers/dev.compose.yml up -d`.
