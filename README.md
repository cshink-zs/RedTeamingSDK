# RedTeamingSDK

Triggers a Zscaler AI Red Teaming test run: it fetches the probes currently
enabled for a given AI app, then starts a new test run against all of them.

Designed to be dropped into a CI/CD pipeline as a single step (either running
the Docker image or the script directly) so a red teaming scan runs
automatically, e.g. after deploying a new version of an AI app.

## How it works

1. Exchanges your OAuth client credentials for an access token
   (`OAUTH_TOKEN_URL`).
2. Calls the probe-settings API for `TARGET_ID` and collects the `probeId` of
   every probe with `enabled: true`.
3. Triggers a new test run (`TEST_RUN_NAME`) against those probe IDs.

## Configuration

Set these as environment variables (e.g. in a local `.env` file):

| Variable               | Description                                                                                                                  |
|------------------------|--------------------------------------------------------------------------------------------------------------------------|
| `OAUTH_CLIENT_ID`      | API client ID, created in Zscaler with the `redteaming admin` scope                                                      |
| `OAUTH_CLIENT_SECRET`  | API client secret for the same client                                                                                    |
| `OAUTH_TOKEN_URL`      | Token endpoint, e.g. `https://[yourtenantid].zslogin.net/oauth2/v1/token` (substitute your tenant name)                  |
| `TARGET_ID`            | The ID of the AI app configured in Red Teaming                                                                           |
| `TEST_RUN_NAME`        | Name to assign to the triggered test run                                                                                 |

`.env` is gitignored — never commit real credentials.

## Running locally

```bash
pip install -r requirements.txt
python main.py
```

## Running with Docker

```bash
docker compose up --build
```

This builds the image (which also installs the bundled
`zscaler-root-ca.crt` so TLS interception by Zscaler doesn't break outbound
HTTPS calls) and runs the script with the environment variables from `.env`.

Alternatively, with plain Docker:

```bash
docker build -t redteamingsdk .
docker run --env-file .env redteamingsdk
```

## Running the prebuilt image (no build required)

A prebuilt image is published at `cshink837/trigger_test_run:latest`. Just
supply the environment variables from a local `.env` file:

```bash
docker run --env-file .env cshink837/trigger_test_run:latest
```

## Using it in a CI/CD pipeline

In CI, store `OAUTH_CLIENT_ID`, `OAUTH_CLIENT_SECRET`, `OAUTH_TOKEN_URL`,
`TARGET_ID`, and `TEST_RUN_NAME` as secrets/masked variables in the
pipeline's settings — don't check them into the repo. Each example below
runs the prebuilt image (`cshink837/trigger_test_run:latest`), so no build
step is needed.

### GitHub Actions

Add the values under **Settings → Secrets and variables → Actions**. A ready
to use workflow is included at
[`.github/workflows/red-teaming-scan.yml`](.github/workflows/red-teaming-scan.yml):

```yaml
name: AI Red Teaming scan

on:
  workflow_dispatch:
  push:
    branches: [main]

jobs:
  trigger-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger red teaming test run
        run: |
          docker run --rm \
            -e OAUTH_CLIENT_ID="${{ secrets.OAUTH_CLIENT_ID }}" \
            -e OAUTH_CLIENT_SECRET="${{ secrets.OAUTH_CLIENT_SECRET }}" \
            -e OAUTH_TOKEN_URL="${{ secrets.OAUTH_TOKEN_URL }}" \
            -e TARGET_ID="${{ secrets.TARGET_ID }}" \
            -e TEST_RUN_NAME="${{ github.run_id }}" \
            cshink837/trigger_test_run:latest
```

This runs the image with plain `docker run` on the (Docker-preinstalled)
`ubuntu-latest` runner, rather than as a job-level `container:`. Job-level
containers don't keep running after the image's own `CMD` finishes, so a
later step trying to `exec` into it (e.g. a separate `run: python main.py`
step) would fail with "container is not running" — `docker run` avoids that
by executing the whole thing as a single, self-contained step.

### GitLab CI

Add the values under **Settings → CI/CD → Variables** (masked and
protected), then reference them from a job that uses the image directly:

```yaml
trigger-scan:
  image: cshink837/trigger_test_run:latest
  stage: test
  variables:
    TEST_RUN_NAME: "$CI_PIPELINE_ID"
  script:
    - python main.py
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

`OAUTH_CLIENT_ID`, `OAUTH_CLIENT_SECRET`, `OAUTH_TOKEN_URL`, and `TARGET_ID`
come from the CI/CD variables configured in the project settings and are
automatically exposed as environment variables inside the job.
