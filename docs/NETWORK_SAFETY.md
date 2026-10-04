# Network safety

This application does not contain Wi-Fi attack, packet capture, scanning, flooding, denial-of-service, or outbound API code.

The original Dockerfile used `uvicorn[standard]`, which installs optional packages that are not needed here. This corrected build uses plain `uvicorn`, disables pip's progress bar and version check, limits retries to one, and applies a 30-second timeout.

The Compose port is bound to `127.0.0.1`, so it is not exposed on the LAN by default.

To inspect before running:

```bash
grep -RniE 'socket|requests|httpx|subprocess|nmap|scapy|wifi|wireless|packet|flood|urllib' app scripts
cat Dockerfile docker-compose.yml requirements.txt
```

`urllib` will match in `app/main.py` (calls the local LLM container) and `scripts/download_model.py` (one-time model download from Hugging Face). Both are intentional; neither makes calls to external services at runtime.

To build with visible logs:

```bash
docker compose build --no-cache --progress=plain
```

To stop immediately:

```bash
docker compose down --remove-orphans
```
