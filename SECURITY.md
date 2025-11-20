# Security Policy

## Supported Versions

We take security seriously and strive to keep our application secure. The following versions are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| Latest (main)   | :white_check_mark: |
| Development (dev) | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly. We appreciate your efforts to help keep our project secure.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by:

1. **GitHub Security Advisories** (Preferred)
   - Go to the [Security tab](../../security/advisories) of this repository
   - Click "Report a vulnerability"
   - Fill out the form with details

2. **Email** (Alternative)
   - Contact the maintainers directly (check repository settings for contact info)
   - Include detailed information about the vulnerability

### What to Include

Please include the following information in your report:

- **Description**: A clear description of the vulnerability
- **Impact**: What could an attacker accomplish?
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Affected Components**: Which part of the application is affected (frontend, backend, etc.)
- **Suggested Fix**: If you have one, please share your thoughts
- **CVE Information**: If applicable, reference any related CVEs

### What to Expect

- **Acknowledgment**: We'll acknowledge receipt of your report within 48 hours
- **Updates**: We'll keep you informed about our progress
- **Timeline**: We aim to release fixes for critical vulnerabilities within 7 days
- **Credit**: If you wish, we'll publicly credit you for the discovery once the issue is resolved

## Security Measures

This project implements several security measures:

- **Automated Scanning**:
  - Trivy container vulnerability scanning (MEDIUM+ severity enforcement)
  - Dependabot dependency alerts
  - npm audit / pip-audit for dependency vulnerabilities
  - Bandit static analysis for Python code
  - TruffleHog secret scanning

- **CI/CD Security**:
  - Automated security checks on all PRs
  - Code quality and linting enforcement
  - Test coverage monitoring

- **Container Security**:
  - Distroless base images (minimal attack surface)
  - Multi-stage builds (no build tools in production)
  - Regular base image updates

## Security Best Practices

When contributing to this project, please:

- Never commit secrets, API keys, or credentials
- Keep dependencies up to date
- Follow secure coding practices
- Write tests for security-critical code
- Review security scan results before merging

## Dependency Updates

We regularly update dependencies to address security vulnerabilities:

- **Dependabot**: Automatically creates PRs for vulnerable dependencies
- **Trivy**: Scans container images for known vulnerabilities
- **Manual Review**: Security updates are prioritized and reviewed promptly

## Questions?

If you have questions about security but don't have a vulnerability to report, feel free to open a regular GitHub issue or discussion.

Thank you for helping keep this project secure!
