# Security Policy

## Supported Versions

The following versions of Aetheris are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 2.6.x   | :white_check_mark: |
| 2.5.x   | :white_check_mark: |
| 2.4.x   | :x:                |
| < 2.4   | :x:                |

## Reporting a Vulnerability

We take the security of Aetheris seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@allowebs.com**

You can also use GitHub's private vulnerability reporting:
1. Go to the [Security tab](https://github.com/adryserage/aetheris/security)
2. Click "Report a vulnerability"
3. Fill in the details

### What to Include

Please include the following information in your report:
- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline

- **Initial Response**: Within 48 hours of report submission
- **Status Update**: Within 7 days with an assessment of the vulnerability
- **Resolution**: Security patches are typically released within 30 days for verified vulnerabilities

### What to Expect

- A confirmation of receipt within 48 hours
- Regular updates on the status of your report
- Credit in the release notes (if desired) once the issue is fixed
- A CVE ID assignment for significant vulnerabilities

### Safe Harbor

We consider security research conducted in good faith to be authorized. We will not pursue legal action against researchers who:
- Make a good faith effort to avoid privacy violations, destruction of data, and interruption of services
- Only interact with accounts they own or with explicit permission of the account holder
- Do not exploit a vulnerability beyond what is necessary to demonstrate it

## Security Best Practices for Users

### API Keys
- Never commit API keys to version control
- Use environment variables or `.env` files
- Rotate API keys regularly

### Running Aetheris
- Keep Aetheris updated to the latest version
- Review analysis output before sharing publicly
- Use `--exclude` to skip sensitive files

### Reporting Output
- Sanitize analysis reports before sharing
- Remove any accidentally exposed credentials
- Use `--no-secrets` flag when available

## Known Security Considerations

### AI Provider Communication
- All communication with AI providers (Gemini, OpenAI, Claude) uses HTTPS
- API keys are never logged or stored in analysis output
- Code snippets sent to AI providers should not contain secrets

### Local Storage
- Statistics and cache files are stored in user-accessible directories
- No sensitive data is persisted locally by default
- Use file system permissions to protect `.aetheris/` directory

## Acknowledgments

We would like to thank the following individuals for responsibly disclosing security issues:

*None yet - be the first!*
