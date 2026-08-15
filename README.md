# Agente ADK con Qwen locale

Semplice agente realizzato con **Google Agent Development Kit (ADK)** e
**Qwen3.5-4B**, eseguito localmente tramite **Ollama**.

L'agente dispone di due tool Python:

- `get_weather`: recupera da Open-Meteo condizioni attuali e previsioni per le
  prossime 12 ore;
- `get_room_air_quality`: recupera da Kaiterra CO₂, PM2.5, PM10, TVOC,
  temperatura e umidità della stanza.

## Requisiti

- Linux oppure macOS;
- Python 3.10 o successivo;
- Ollama;
- circa 4 GB di spazio per il modello.

Il progetto è stato testato sulle seguenti piattaforme:
- Ubuntu 22.04.5 LTS con Python 3.13, Ollama 0.32.6 e
Qwen3.5-4B su un AMD Ryzen 7 PRO 7840U con Radeon 780M.
- MacOS Sequoia 15.7.1 con Python 3.13.7, Ollama  0.32.13 e Qwen3.5-4B su un Macbook Air M1.

## 1. Installare Ollama

### Linux / macOS

Seguire la [guida ufficiale per Linux](https://docs.ollama.com/linux) oppure
eseguire l'installer ufficiale:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verificare l'installazione:

```bash
ollama --version
```


Su Apple Silicon Ollama seleziona automaticamente la GPU tramite **Metal**. Non
bisogna usare `start_ollama_gpu.sh`, `OLLAMA_VULKAN` o
`OLLAMA_IGPU_ENABLE`: queste opzioni appartengono alla configurazione Linux AMD.

## 2. Creare l'ambiente Python

Dalla cartella principale del progetto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

L'ambiente va riattivato in ogni nuovo terminale:

```bash
source .venv/bin/activate
```

## 3. Configurare le variabili d'ambiente

Creare il file locale `.env` dal modello fornito:

```bash
cp .env.example .env
```

Contenuto principale:

```dotenv
OPENAI_API_BASE=http://127.0.0.1:11435/v1
OPENAI_API_KEY=ollama
MODEL_ID=qwen3.5:4b
KAITERRA_KIOSK_ID=inserire_il_proprio_kiosk_id
ROOM_TIMEZONE=Europe/Rome
```

`KAITERRA_KIOSK_ID` è la parte identificativa dell'endpoint Kaiterra:

```text
https://kiosk.kaiterra.com/v4/KAITERRA_KIOSK_ID/data
```

Se non si dispone
di un sensore Kaiterra, il tool meteo continua a funzionare, mentre quello della
stanza restituisce un errore di configurazione controllato.

***All'interno della configurazione è stato temporaneamente mantenuto l'ID del mio sensore per permettere di testare le funzionalità dell'agente.***

## 4. Avviare Qwen

Scegliere **una sola** delle modalità seguenti e lasciare aperto il terminale
che esegue Ollama.

### Modalità A: GPU AMD integrata tramite Vulkan

Questa è la configurazione usata sulla Radeon 780M:

```bash
./start_ollama_gpu.sh
```

Lo script abilita il backend Vulkan sperimentale e le GPU integrate, quindi
espone Ollama su `127.0.0.1:11435`.

In un secondo terminale scaricare il modello:

```bash
OLLAMA_HOST=127.0.0.1:11435 ollama pull qwen3.5:4b
```

Verificare il funzionamento:

```bash
OLLAMA_HOST=127.0.0.1:11435 ollama run qwen3.5:4b "Rispondi soltanto: GPU attiva"
OLLAMA_HOST=127.0.0.1:11435 ollama ps
```

La configurazione `.env` deve usare:

```dotenv
OPENAI_API_BASE=http://127.0.0.1:11435/v1
```

### Modalità B: solo CPU

Per forzare l'esecuzione sulla CPU:

```bash
./start_ollama_cpu.sh
```

Il server CPU usa `127.0.0.1:11436`. In un secondo terminale:

```bash
OLLAMA_HOST=127.0.0.1:11436 ollama pull qwen3.5:4b
OLLAMA_HOST=127.0.0.1:11436 ollama run qwen3.5:4b "Rispondi soltanto: CPU attiva"
OLLAMA_HOST=127.0.0.1:11436 ollama ps
```

La colonna `PROCESSOR` deve mostrare `100% CPU`.

In questo caso modificare `.env`:

```dotenv
OPENAI_API_BASE=http://127.0.0.1:11436/v1
```

### Modalità C: macOS con Apple Silicon

Avviare normalmente l'app Ollama. Il server locale usa la porta predefinita
`11434` e Metal viene selezionato automaticamente:

```bash
ollama pull qwen3.5:4b
ollama run qwen3.5:4b "Rispondi soltanto: Metal attivo"
ollama ps
```

Configurare `.env` con la porta standard di Ollama:

```dotenv
OPENAI_API_BASE=http://127.0.0.1:11434/v1
OPENAI_API_KEY=ollama
MODEL_ID=qwen3.5:4b
```

Da questo punto, installazione Python, `agent_demo.py` e ADK Web funzionano con
gli stessi comandi usati su Linux.


## 5. Avviare l'agente da terminale

Con Ollama già attivo nella modalità scelta:

```bash
source .venv/bin/activate
python agent_demo.py
```

Esempi:

```text
Che tempo fa a Verona?
Pioverà nelle prossime 12 ore a Milano?
Qual è la temperatura nella mia stanza?
Mostrami le misurazioni di CO2 e PM2.5.
```

## 6. Avviare ADK Web
ADK fornisce una comoda interfaccia web per testare l'agente e vedere in modo grafico le chiamate ai vari tools o agenti che lo compongono.
Per avviarlo, incolla il seguente comando all radice del progetto:

```bash
source .venv/bin/activate
adk web \
  --host 127.0.0.1 \
  --port 8000 \
  --allow_origins http://localhost:8000 \
  --allow_origins http://127.0.0.1:8000 \
  --session_service_uri memory:// \
  --artifact_service_uri memory:// \
  --memory_service_uri memory:// \
  .
```

Aprire <http://127.0.0.1:8000> e selezionare `weather_agent`.

## Risoluzione dei problemi

### `Failed to create session` in ADK Web

Aprire esattamente <http://127.0.0.1:8000> e verificare che il comando
contenga entrambe le opzioni `--allow_origins` mostrate sopra.
Se ancora non funziona, settare --allow_origins '*' nel comando di avvio dell'interfacci ADK.

### ADK non riesce a collegarsi a Ollama

Verificare che la porta indicata in `.env` corrisponda al server avviato:

```bash
curl http://127.0.0.1:11435/api/tags
# oppure, per la CPU:
curl http://127.0.0.1:11436/api/tags
# su Mac:
curl http://127.0.0.1:11434/api/tags
```
