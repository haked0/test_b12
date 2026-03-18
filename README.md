# B12 Application Submission

This repository submits an application to B12 using a Python script executed by GitHub Actions.

## What it does

The workflow runs a Python script that:

- Builds a JSON payload with:
  - `name`
  - `email`
  - `resume_link`
  - `repository_link`
  - `action_run_link`
  - `timestamp`
- Canonicalizes the JSON by:
  - sorting keys alphabetically
  - using compact separators
  - encoding as UTF-8
- Signs the raw JSON bytes using HMAC-SHA256
- Sends the payload to:

`https://b12.io/apply/submission`

## Files

```text
.github/workflows/submit-application.yml
submit_application.py
README.md
