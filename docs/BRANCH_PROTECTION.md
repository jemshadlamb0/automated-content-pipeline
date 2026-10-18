# Configure main branch protection

Repository branch-protection rules are GitHub repository settings. Committing a YAML file cannot switch them on. The linked GitHub integration can write repository files but does not expose the branch-protection mutation operation, so an administrator must enable these settings once in the UI.

## Create the rule
1. Open the repository and choose Settings.
2. Under Code and automation, choose Branches.
3. Select Add branch protection rule.
4. Set the branch name pattern to main.
5. Enable Require a pull request before merging.
6. Do not require an approving review if you are the sole maintainer; GitHub does not count your own approval as independent review. Add one required approval only when another trusted reviewer will be available.
7. Enable Require status checks to pass before merging.
8. Select both current job checks from this repository:
   - test-and-static-analysis
   - dependency-and-static-checks
9. Enable Require conversation resolution before merging.
10. Keep force pushes and branch deletion disabled.
11. Enable Do not allow bypassing the above settings if you want restrictions to apply to administrators too.
12. Save the rule.

GitHub may only offer a check in the list after that check has run recently. If a check is not shown, confirm the current CI/security workflows have passed on main, reload the settings page and select the exact job names above.

## Verify
Open Settings → Branches and confirm a rule matching main exists. Then make a small documentation-only branch and pull request. Verify both checks run and GitHub refuses to merge until required checks pass.

Official guide: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule
