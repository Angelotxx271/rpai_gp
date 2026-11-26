# Security Policy

This repository (`Angelotxx271/rpai_gp`) is **public**. All secrets, API keys, IE programme documents, real student thesis work, and the advisor-spike answer key stay outside the repository (either in Railway environment variables or in the git-excluded `private/` directory).

## Automated Controls

- **GitHub Secret Scanning & Push Protection:** enabled on this repository.
- **GitHub Dependabot:** vulnerability alerts, automated security updates, and weekly dependency PRs configured in [`.github/dependabot.yml`](.github/dependabot.yml) across Python (`pip`), Node (`npm`), Docker base images, and GitHub Actions.
- **GitHub CodeQL:** static analysis for Python and JavaScript via [`.github/workflows/codeql.yml`](.github/workflows/codeql.yml).
- **CI Security Workflow ([`.github/workflows/security.yml`](.github/workflows/security.yml)):** runs full-history `gitleaks`, tracked-file privacy/secret hygiene checks, Bandit SAST, `pip-audit`, and `npm audit` on pushes and pull requests to `main`.
- **Full Audit Record:** see [`evidence-log/security-audit.md`](evidence-log/security-audit.md) for the recorded git-history secret scan, historical remediation log, service boundaries, untrusted-input defences, and human-approval controls.

## Reporting a Vulnerability or Secret Exposure

If you spot an exposed secret, leaked personal data, or a security bug in any service (`prototype/tfgpt/`, `tfgpt-landing/`, `tfgpt-pilot/`):

1. **Do not** open a public issue containing the secret or personal data.
2. Contact the repository owner (`@Angelotxx271`) privately so the credential can be rotated immediately and the deployment rolled back per [`specs/tech-stack.md`](specs/tech-stack.md) (*How to undo a bad change*).
