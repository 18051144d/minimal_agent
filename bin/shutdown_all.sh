#!/bin/bash
PID_DIR="./pids"
PORTS=(8000 8001 6333 6334)

echo "[shutdown_all] Shutting down services..."

for pid_file in ${PID_DIR}/*.pid; do
  [ -e "$pid_file" ] || continue
  pid=$(cat "$pid_file")
  if ps -p "$pid" > /dev/null 2>&1; then
    echo "[shutdown_all] Killing $(basename "$pid_file" .pid) (PID $pid)"
    kill "$pid"
    wait "$pid" 2>/dev/null
  else
    echo "[shutdown_all] Process from $(basename "$pid_file") not running—skipping"
  fi
  rm -f "$pid_file"
done

for port in "${PORTS[@]}"; do
  pid_on_port=$(lsof -ti :"$port" 2>/dev/null)
  if [ -n "$pid_on_port" ]; then
    if [ "$(ps -o user= -p "$pid_on_port")" == "$(whoami)" ]; then
      echo "[shutdown_all] Port $port still used by our user, killing PID $pid_on_port"
      kill "$pid_on_port" 2>/dev/null || true
    else
      echo "[shutdown_all] Port $port in use by another user, skipping"
    fi
  fi
done

echo "[shutdown_all] All services stopped."