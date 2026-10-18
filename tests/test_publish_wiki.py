from pathlib import Path
import pytest

from scripts.publish_wiki import WikiPublishError, build_pages, normalize_wiki_link, parse_github_repo, render_wiki_markdown


def test_source_readme_maps_to_home_page():
    pages = build_pages()
    assert "Home.md" in pages
    assert len(pages) >= 9


def test_relative_markdown_links_become_wiki_slugs():
    assert normalize_wiki_link("languages.md") == "languages"
    assert normalize_wiki_link("README.md") == "Home"
    assert normalize_wiki_link("https://example.org/page.md") == "https://example.org/page.md"
    assert render_wiki_markdown("[Languages](languages.md)") == "[Languages](languages)"


@pytest.mark.parametrize("remote,expected", [
    ("https://github.com/owner/repo.git", ("owner", "repo")),
    ("https://github.com/owner/repo", ("owner", "repo")),
    ("git@github.com:owner/repo.git", ("owner", "repo")),
    ("ssh://git@github.com/owner/repo.git", ("owner", "repo")),
])
def test_parses_github_origin(remote, expected):
    assert parse_github_repo(remote) == expected


@pytest.mark.parametrize("remote", [
    "https://evil.example/owner/repo.git",
    "https://github.com/owner/repo.wiki.git",
    "file:///tmp/repo",
    "",
])
def test_rejects_non_source_or_unsafe_git_remotes(remote):
    with pytest.raises(WikiPublishError):
        parse_github_repo(remote)
