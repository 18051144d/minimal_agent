#!/bin/bash

vllm serve "Qwen/Qwen3-0.6B" \
  --host "127.0.0.1" \
  --port "8001" \
  --max-model-len "10000" \
  --gpu-memory-utilization 0.2 \
  --dtype auto \
  --trust-remote-code
