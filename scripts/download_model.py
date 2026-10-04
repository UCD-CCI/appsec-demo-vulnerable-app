"""Download the workshop's small CPU-only GGUF model with progress and resume support."""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

URL = "https://huggingface.co/bartowski/SmolLM2-360M-Instruct-GGUF/resolve/main/SmolLM2-360M-Instruct-Q4_K_M.gguf?download=true"
ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "models" / "SmolLM2-360M-Instruct-Q4_K_M.gguf"
PART = DEST.with_suffix(DEST.suffix + ".part")


def main() -> int:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists() and DEST.stat().st_size > 100_000_000:
        print(f"Model already present: {DEST} ({DEST.stat().st_size / 1024 / 1024:.1f} MiB)")
        return 0

    existing = PART.stat().st_size if PART.exists() else 0
    headers = {"User-Agent": "break-ai-app-workshop/1.1"}
    if existing:
        headers["Range"] = f"bytes={existing}-"
    request = urllib.request.Request(URL, headers=headers)
    print(f"Downloading model to {DEST}")
    print("This is a one-time download. Press Ctrl+C to pause; rerun to resume.")

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            mode = "ab" if existing and response.status == 206 else "wb"
            if mode == "wb":
                existing = 0
            total_header = response.headers.get("Content-Length")
            total = existing + int(total_header) if total_header else None
            downloaded = existing
            with PART.open(mode) as output:
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    output.write(block)
                    downloaded += len(block)
                    if total:
                        print(f"\r{downloaded / 1024 / 1024:7.1f} / {total / 1024 / 1024:7.1f} MiB", end="", flush=True)
                    else:
                        print(f"\r{downloaded / 1024 / 1024:7.1f} MiB", end="", flush=True)
    except KeyboardInterrupt:
        print("\nDownload paused. Rerun this script to resume.")
        return 130
    except Exception as exc:
        print(f"\nDownload failed: {exc}", file=sys.stderr)
        return 1

    PART.replace(DEST)
    print(f"\nReady: {DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
