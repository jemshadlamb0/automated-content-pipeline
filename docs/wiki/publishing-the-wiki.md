# Publishing the actual GitHub Wiki

The Markdown files in this folder are the source-of-truth documentation in the code repository. GitHub's Wiki tab uses a separate Git repository, so adding these files to the code repo alone does not create pages in that tab.

## One-time initialization
1. Open the repository's Wiki tab.
2. Click Create the first page.
3. Name it Home and save it once. This initializes GitHub's separate Wiki repository. The sync script will replace that starter content with the maintained Home page.
4. Ensure your local Git installation is authenticated to GitHub through Git Credential Manager or another normal Git credential helper. Do not put tokens into the script or repository.

## Sync the pages
From a local clone of the code repository, run a dry run first:

~~~bash
python scripts/publish_wiki.py --dry-run
~~~

Then publish:

~~~bash
python scripts/publish_wiki.py
~~~

The script derives the Wiki remote from the local origin URL, writes the Markdown files from docs/wiki/ into the Wiki repository, converts local Markdown links to Wiki page slugs, commits only changed managed pages and pushes. Pages not managed by docs/wiki/ are preserved. If the Wiki is not initialized or Git credentials do not allow writing, it stops with an actionable error.

## Safety and limitations
- The script never receives or stores your password/token; Git uses the credential helper configured on your machine.
- Review the dry-run page list before pushing.
- Do not execute it in an untrusted checkout or with unexpected Git remotes.
- The Wiki sync script does not change repository settings or branch protection.
- To update the code documentation, change docs/wiki/ and submit the usual pull request first, then sync the Wiki from the resulting trusted main branch.
