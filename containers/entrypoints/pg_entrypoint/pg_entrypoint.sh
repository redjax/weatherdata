#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USERNAME" --dbname="$POSTGRES_DATABASE" <<-EOSQL
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOSQL
