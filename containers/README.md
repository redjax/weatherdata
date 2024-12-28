# Containers

Docker containers for the app. Some of these containers are for a single service, like [`rabbitmq.compose.yml`](./rabbitmq/rabbitmq.compose.yml), which only runs a RabbitMQ container.

## How to run

From the root of the git repository, run `docker compose -f ./containers/container-directory/compose.yml up -d`.
