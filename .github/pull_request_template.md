## Summary
Describe the change and the threat/model assumptions it affects.

## Validation
- [ ] Unit tests pass
- [ ] Lint/static analysis pass
- [ ] New failure cases have regression tests
- [ ] No credentials, model weights, user data or fetched media are included
- [ ] Network-related changes validate redirects, IP ranges, timeouts and size limits
- [ ] Publishing remains disabled in CI

## Security and compatibility
- [ ] Tenant authorization and data isolation are preserved
- [ ] Dependencies/actions are reviewed and pinned where applicable
- [ ] Configuration changes are documented
- [ ] Remaining risks and manual deployment steps are stated
