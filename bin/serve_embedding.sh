#!/bin/bash

vllm serve "jinaai/jina-code-embeddings-1.5b" \
  --host "127.0.0.1" \
  --port "8000" \
  --max-model-len 2000 \
  --gpu-memory-utilization 0.2 \
  --dtype auto \
  --trust-remote-code
