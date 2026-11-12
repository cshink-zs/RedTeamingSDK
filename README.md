# RedTeamingSDK

Triggers a Zscaler AI Red Teaming test run: it fetches the probes currently
enabled for a given AI app, then starts a new test run against all of them.

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
