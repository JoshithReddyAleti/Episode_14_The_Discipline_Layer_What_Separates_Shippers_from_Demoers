# Security Policy

## Reporting vulnerabilities

If you find a security issue in Episode 14 examples, utilities, or infrastructure references, please **do not** open a public issue.

Instead, contact the maintainer directly via LinkedIn: https://www.linkedin.com/in/joshith-reddy-aleti-b6a888244/

## Scope

This repository contains educational material. It is not intended for direct production use without adaptation. The infrastructure references (Terraform, K8s) are starting points, not hardened production configs.

## Content covering vulnerabilities

Part C of this episode covers LLM security including prompt injection, jailbreaking, exfiltration, and supply chain issues. The content is intended for **defenders**. All attack examples are for educational understanding to enable defense.

If any example inadvertently enables real-world harm, contact us to have it revised or removed.

## Third-party dependencies

Utilities and examples depend on standard Python libraries. Security-sensitive integrations (Garak, PyRIT, etc.) should be reviewed independently before use.
