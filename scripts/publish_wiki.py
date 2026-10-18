"""Publish docs/wiki/*.md to this repository's real GitHub Wiki.

GitHub's Wiki is a separate Git repository and must be initialized once in the
web UI (Wiki tab -> Create the first page). This helper requires a local clone
with normal Git credentials configured. It never handles or stores tokens.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "wiki"
LINK_RE = re.compile(r"(\]\()(?P<target>[^()\s]+)\.md(\))")


class WikiPublishError(RuntimeError):
    """Raised when wiki publishing cannot proceed safely."""


def normalize_wiki_link(target: str) -> str:
    """Convert local Markdown file links to GitHub Wiki page slugs."""
    if target.startswith(("https://", "http://", "mailto:", "#", "data:")):
        return target
    if target.lower() == "readme.md":
        return "Home"
    return target[:-3] if target.lower().endswith(".md") else target


def render_wiki_markdown(text: str) -> str:
    """Rewrite same-directory .md links for GitHub Wiki page URLs."""
    return LINK_RE.sub(
        lambda match: match.group(1) + normalize_wiki_link(match.group("target")) + match.group(3),
        text,
    )


def parse_github_repo(remote: str) -> tuple[str, str]:
    """Extract owner/repo from standard HTTPS or SSH GitHub remotes only."""
    value = remote.strip()
    https_match = re.fullmatch(r"https://github\.com/([^/]+)/([^/]+?)(?:\.git)?", value)
    ssh_match = re.fullmatch(r"(?:git@github\.com:|ssh://git@github\.com/)([^/]+)/([^/]+?)(?:\.git)?", value)
    match = https_match or ssh_match
    if not match:
        raise WikiPublishError("Origin must be a standard github.com HTTPS or SSH repository URL.")
    owner, repository = match.groups()
    if not owner or not repository or repository.endswith(".wiki"):
        raise WikiPublishError("Origin must identify the source repository, not a Wiki remote.")
    return owner, repository


def _run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args, cwd=cwd, check=True, text=True, capture_output=True
        )
    except FileNotFoundError as exc:
        raise WikiPublishError("Git must be installed and available on PATH.") from exc
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or "").strip()
        safe = details[-800:]
        raise WikiPublishError(f"Command failed: {args[0]} (exit {exc.returncode}). {safe}") from exc


def build_pages() -> dict[str, str]:
    """Build the managed page set; keep files flat in the Wiki repository."""
    if not SOURCE_DIR.is_dir():
        raise WikiPublishError(f"Wiki source directory is missing: {SOURCE_DIR}")
    paths = sorted(SOURCE_DIR.glob("*.md"))
    if not paths:
        raise WikiPublishError("No Markdown pages were found under docs/wiki/.")
    pages: dict[str, str] = {}
    for path in paths:
        name = "Home.md" if path.name.lower() == "readme.md" else path.name
        if name in pages:
            raise WikiPublishError(f"Duplicate generated Wiki page name: {name}")
        pages[name] = render_wiki_markdown(path.read_text(encoding="utf-8"))
    if "Home.md" not in pages:
        raise WikiPublishError("docs/wiki/README.md is required to generate the Wiki Home page.")
    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync repository Markdown docs to the real GitHub Wiki.")
    parser.add_argument("--dry-run", action="store_true", help="List pages without contacting GitHub.")
    parser.add_argument("--remote", help="Optional GitHub source remote; defaults to local origin.")
    args = parser.parse_args()
    try:
        pages = build_pages()
        if args.dry_run:
            print(f"Dry run: {len(pages)} pages ready for the GitHub Wiki:")
            for name in pages:
                print(f"  {name}")
            print("No network calls or Git writes were made.")
            return 0

        remote = args.remote
        if remote is None:
            remote = _run(["git", "remote", "get-url", "origin"], cwd=ROOT).stdout.strip()
        owner, repo = parse_github_repo(remote)
        wiki_remote = f"https://github.com/{owner}/{repo}.wiki.git"

        with tempfile.TemporaryDirectory(prefix="acp-wiki-") as temp:
            wiki_dir = Path(temp) / "wiki"
            try:
                _run(["git", "clone", wiki_remote, str(wiki_dir)])
            except WikiPublishError as exc:
                raise WikiPublishError(
                    "Could not clone the Wiki. Open the repository's Wiki tab, click "
                    "'Create the first page', save it once, then rerun this command. "
                    "Make sure your Git credential helper can push to the repository. "
                    f"Underlying error: {exc}"
                ) from exc

            changed: list[str] = []
            for name, text in pages.items():
                destination = wiki_dir / name
                old = destination.read_text(encoding="utf-8") if destination.exists() else None
                if old == text:
                    continue
                destination.write_text(text, encoding="utf-8", newline="\n")
                changed.append(name)

            if not changed:
                print(f"Wiki is already up to date ({len(pages)} managed pages).")
                return 0
            _run(["git", "add", "--", *changed], cwd=wiki_dir)
            _run(["git", "commit", "-m", "docs: sync repository Wiki pages"], cwd=wiki_dir)
            _run(["git", "push", "origin", "HEAD"], cwd=wiki_dir)
            print(f"Published {len(changed)} Wiki page(s): {', '.join(changed)}")
            print("Existing pages not managed by docs/wiki/ were preserved.")
            return 0
    except WikiPublishError as exc:
        print(f"Wiki publishing stopped safely: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
