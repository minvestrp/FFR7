## Description

This PR includes changes related to CI: running tests with pytest, generating `junit.xml` and `coverage.xml` artifacts, and adding a UI improvement for admin token creation.

Please include a short description of the changes and any relevant notes for reviewers.

---

## Checklist
- [ ] Tests added / updated
- [ ] CI passes (GitHub Actions)
- [ ] Documentation updated where applicable

---

## CI Artifacts
On successful runs, CI will upload `pytest-artifacts` containing:
- `pytest.log` — console output
- `junit.xml` — JUnit XML test report
- `coverage.xml` — coverage report in Cobertura/XML format

Reviewers: please check these artifacts on the Actions run if needed.
