---
title: Local LLM
date: 2026-06-23 00:02:08
category:
tags:
---

### LM Studio 

**qwen3.5-9b**

params: 
context length: 16K
Gpu offload: 32
Cpu pool size: 10
Evaluation Batch Size: 2048
Physical Batch size: 128
Max concurrent Predictions: 2

### VS Code
** Continue **

config.yaml
```yaml
name: Main Config
version: 1.0.0
schema: v1
models:
  - name: qwen
    provider: openai
    model: qwen2.5-coder-14b-instruct
    apiBase: http://127.0.0.1:1234/v1
    apiKey: dummy

    requestOptions:
      timeout: 300000

    roles:
      - chat
      - autocomplete
      - apply

  - name: nomic-embed-text
    provider: openai
    model: text-embedding-nomic-embed-text-v2-moe
    apiBase: http://127.0.0.1:1234/v1
    apiKey: dummy
    roles:
      - embed

context:
  - provider: codebase
  - provider: file
  - provider: folder
  - provider: repo-map
```
