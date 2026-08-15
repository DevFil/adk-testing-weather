#!/usr/bin/env bash
set -euo pipefail

# Una porta separata permette di provare la CPU senza modificare il server GPU.
export OLLAMA_HOST="127.0.0.1:11436"
export OLLAMA_MODELS="${OLLAMA_MODELS:-$HOME/.ollama/models}"
export OLLAMA_LLM_LIBRARY=cpu
export OLLAMA_NO_CLOUD=1

# Impedisce al backend Vulkan di selezionare una GPU eventualmente disponibile.
export GGML_VK_VISIBLE_DEVICES=-1
unset OLLAMA_VULKAN
unset OLLAMA_IGPU_ENABLE

ollama_bin="${OLLAMA_BIN:-$(command -v ollama || true)}"
if [[ -z "$ollama_bin" ]]; then
  printf 'Errore: ollama non trovato nel PATH.\n' >&2
  exit 1
fi

exec "$ollama_bin" serve
