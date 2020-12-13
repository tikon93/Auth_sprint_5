#!/bin/bash
set -e

POSTGRES="psql --username ${POSTGRES_USER}"

echo "Creating database role: ${ETL_DB_USER}"

$POSTGRES <<-EOSQL
CREATE USER ${ETL_DB_USER} WITH SUPERUSER PASSWORD '${ETL_DB_PASSWORD}';
EOSQL