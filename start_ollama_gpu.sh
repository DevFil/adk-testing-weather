#!/usr/bin/env bash
set -euo pipefail

# La porta 11435 evita il conflitto con l'installazione Snap sulla 11434.
export OLLAMA_HOST="127.0.0.1:11435"
export OLLAMA_MODELS="${OLLAMA_MODELS:-$HOME/.ollama/models}"
export OLLAMA_VULKAN=1

# Ollama ignora intenzionalmente le GPU integrate se questa opzione non è attiva.
export OLLAMA_IGPU_ENABLE=1

ollama_bin="${OLLAMA_BIN:-$(command -v ollama || true)}"
if [[ -z "$ollama_bin" ]]; then
  printf 'Errore: ollama non trovato nel PATH.\n' >&2
  exit 1
fi

exec "$ollama_bin" serve
