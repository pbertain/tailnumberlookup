#!/bin/bash

#RUN_IP="127.0.0.1"
RUN_IP="0.0.0.0"
RUN_PORT="49080"

BASE_DIR="/var/bertain-cdn/faa-aircraft-lookup"
BIN_DIR="${BASE_DIR}/bin"
CONFIG_DIR="${BASE_DIR}/config"
UVICORN="/usr/local/bin/uvicorn"
SERVER="faa_lookup_openapi_server"

cd ${BASE_DIR}

export FAA_DB_PASSWORD=$(cat ${CONFIG_DIR}/.db_password)
${UVICORN} ${SERVER}:app --host ${RUN_IP} --port ${RUN_PORT} --reload

#uvicorn faa_lookup_openapi_server:app --host 127.0.0.1 --port 49080 --reload
