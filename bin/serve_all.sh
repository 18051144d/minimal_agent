#!/bin/bash
set -e

LOG_DIR="./logs"
PID_DIR="./pids"
mkdir -p "$LOG_DIR" "$PID_DIR"

echo "[serve_all] Starting all services..."

# Start embedding server
bash ./bin/serve_embedding.sh >"${LOG_DIR}/embedding.log" 2>&1 &
echo $! >"${PID_DIR}/embedding.pid"
echo "[serve_all] Embedding server started with PID $(cat ${PID_DIR}/embedding.pid)"

# Start Qdrant server
bash ./bin/serve_qdrant.sh >"${LOG_DIR}/qdrant.log" 2>&1 &
echo $! >"${PID_DIR}/qdrant.pid"
echo "[serve_all] Qdrant server started with PID $(cat ${PID_DIR}/qdrant.pid)"

# Start SLM server
bash ./bin/serve_slm.sh >"${LOG_DIR}/slm.log" 2>&1 &
echo $! >"${PID_DIR}/slm.pid"
echo "[serve_all] SLM server started with PID $(cat ${PID_DIR}/slm.pid)"

echo "[serve_all] All services running. Logs are in '${LOG_DIR}/'."
