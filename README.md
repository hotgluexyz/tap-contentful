# tap-contentful

A [Singer](https://www.singer.io/) tap that extracts data from **Contentful**. It is built with [hotglue-singer-sdk](https://github.com/hotgluexyz/HotglueSingerSDK) and speaks the standard Singer message protocol on stdout, so you can pair it with any compatible target.

## Features

- Port of the deprecated [hotglue/tap-contentful](https://gitlab.com/hotglue/tap-contentful) (tap-kit) to the Hotglue Singer SDK, with the same config keys.
- Reads the [Content Delivery API](https://www.contentful.com/developers/docs/references/content-delivery-api/) with a **Bearer** token.
- Incremental sync on `sys.updatedAt` (the deprecated tap always did a full sync).

### Streams

| Stream | Endpoint | Primary key | Replication key |
| ------ | -------- | ----------- | --------------- |
| `entries` | `GET /spaces/{space_id}/environments/{environment}/entries` | `id` (copied from `sys.id`) | `updated_at` (copied from `sys.updatedAt`) |

Each record keeps the API's `sys`, `fields`, and `metadata` objects unchanged. `fields` depends on each content type, so it is passed through without a fixed schema.

Requests page with `skip`/`limit` (1000 per page, the API maximum), ordered by `sys.updatedAt,sys.id`, and filter with `sys.updatedAt[gte]` from the bookmark or `start_date`. On HTTP 429 the tap waits for `X-Contentful-RateLimit-Reset` seconds before the SDK retries.

The Content Delivery API returns published entries only; deleted or unpublished entries are not reported.

## Requirements

- Python **3.10+** (see `requires-python` in `pyproject.toml`).

## Installation

1. **Clone** this repository and `cd` into the project directory.
2. **Create `config.json`** in the project root with your credentials and settings (see [Configuration](#configuration) for the fields and an example).
3. **Create a virtual environment** and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, use `.venv\Scripts\activate` instead of `source .venv/bin/activate`.

4. **Install the package** in editable mode:

```bash
pip install -e .
```

5. **Run the tap** (with the venv still activated):

```bash
tap-contentful --help
```

## Configuration

| Setting | Type | Required | Default | Description |
| ------- | ---- | -------- | ------- | ----------- |
| `access_token` | string (sensitive) | yes | — | Content Delivery API access token. |
| `space_id` | string | yes | — | ID of the space to extract. |
| `environment` | string | no | `master` | Environment ID within the space. |
| `start_date` | string (datetime) | no | `2000-01-01T00:00:00Z` | Only sync entries updated at or after this time. |
| `api_url` | string | no | `https://cdn.contentful.com` | API host, e.g. `https://cdn.eu.contentful.com` for EU spaces. |

Run `tap-contentful --about` (or `tap-contentful --about --format=markdown`) for the authoritative schema for your installed version.

### Example `config.json`

```json
{
  "access_token": "YOUR_CDA_TOKEN",
  "space_id": "YOUR_SPACE_ID",
  "start_date": "2000-01-01T00:00:00Z"
}
```

Do not commit real credentials. Prefer environment variables or a secrets manager in production.

### Environment-based config

You can load settings from the process environment using `--config=ENV` (the SDK merges env into config). Env names follow the tap’s setting keys (see `tap-contentful --about`).

## Usage

With your virtual environment **activated** and `config.json` in place:

Discover stream catalog:

```bash
tap-contentful --config config.json --discover > catalog.json
```

Run a sync (with optional state):

```bash
tap-contentful --config config.json --catalog catalog.json --state state.json
```

Pipe to any Singer target:

```bash
tap-contentful --config config.json --catalog catalog.json | target-jsonl
```

Inspect built-in settings and stream metadata:

```bash
tap-contentful --about
```

## API / documentation

- Content Delivery API: https://www.contentful.com/developers/docs/references/content-delivery-api/
- Authentication: https://www.contentful.com/developers/docs/references/authentication/
- Rate limits: https://www.contentful.com/developers/docs/technical-limits/


## License
MIT — see `LICENSE` and `pyproject.toml`.
