#!/bin/bash

CONTAINER_NAME="${1:-${GENIESIM_CONTAINER_NAME:-genie_sim_${USER:-user}}}"

docker exec -it "$CONTAINER_NAME" bash
