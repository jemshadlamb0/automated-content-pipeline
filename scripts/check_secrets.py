"""Best-effort secret-pattern scanner for tracked source files.

This is a guardrail, not a substitute for dedicated secret scanning or
credential rotation. It fails CI when common token/key patterns are found.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_PATTERNS = (
    ("Telegram bot token", re.compile(r"(?<![A-Za-z0-9_])\d{8,12}:[A-Za-z0-9_-]{30,}(?![A-Za-z0-9_])")),
    ("Hugging Face token", re.compile(r"(?<![A-Za-z0-9_])hf_[A-Za-z0-9]{20,}(?![A-Za-z0-9_])")),
    ("GitHub token", re.compile(r"(?<![A-Za-z0-9_])gh[pousr]_[A-Za-z0-9_]{25,}(?![A-Za-z0-9_])")),
    ("Google API key", re.compile(r"(?<![A-Za-z0-9_])AIza[0-9A-Za-z_-]{30,}(?![A-Za-z0-9_])")),
    ("Private key material", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
)
_BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".gz", ".woff", ".woff2", ".ttf", ".otf"}


def detect_secrets(text: str) -> list[str]:
    """Return names of detected patterns, never the sensitive match."""
    return [label for label, pattern in _PATTERNS if pattern.search(text)]


def tracked_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [Path(item.decode("utf-8", errors="surrogateescape")) for item in result.stdout.split(b"\0") if item]


def scan_paths(paths: list[Path]) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    for path in paths:
        if path.suffix.lower() in _BINARY_SUFFIXES or not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        findings.extend((str(path), label) for label in detect_secrets(content))
    return findings


def main() -> int:
    try:
        paths = tracked_paths()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Secret scan could not enumerate tracked files: {exc}", file=sys.stderr)
        return 2
    findings = scan_paths(paths)
    if findings:
        for path, label in findings:
            print(f"Potential {label} detected in {path}. Remove it and rotate the credential.")
        return 1
    print(f"Secret-pattern scan passed ({len(paths)} tracked paths checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
