"""HTTP API client (REST), including ContentfulStream base class."""

from __future__ import annotations

import time
from typing import Any

import requests
from hotglue_singer_sdk.authenticators import BearerTokenAuthenticator
from hotglue_singer_sdk.streams import RESTStream
from typing_extensions import override

# Content Delivery API maximum page size.
PAGE_SIZE = 1000


class ContentfulStream(RESTStream):
    """Contentful Content Delivery API stream class.

    Collection endpoints return ``{"total", "skip", "limit", "items"}`` and page
    with ``skip`` / ``limit``.
    """

    records_jsonpath = "$.items[*]"

    @override
    @property
    def url_base(self) -> str:
        """Return the space environment root, e.g. ``.../spaces/{id}/environments/master``."""
        api_url = self.config.get("api_url", "https://cdn.contentful.com").rstrip("/")
        environment = self.config.get("environment", "master")
        return f"{api_url}/spaces/{self.config['space_id']}/environments/{environment}"

    @override
    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Send the Content Delivery API token as ``Authorization: Bearer``."""
        return BearerTokenAuthenticator(stream=self, token=self.config["access_token"])

    @override
    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Any | None,
    ) -> Any | None:
        """Return the next ``skip`` offset, or None once ``total`` is reached."""
        body = response.json()
        next_skip = body["skip"] + len(body["items"])
        if not body["items"] or next_skip >= body["total"]:
            return None
        return next_skip

    @override
    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Page with skip/limit, oldest update first so bookmarks only move forward."""
        params: dict[str, Any] = {
            "limit": PAGE_SIZE,
            "skip": next_page_token or 0,
            # sys.id breaks ties so skip-based paging is stable.
            "order": "sys.updatedAt,sys.id",
        }
        start = self.get_starting_timestamp(context)
        if start:
            params["sys.updatedAt[gte]"] = start.isoformat()
        return params

    @override
    def validate_response(self, response: requests.Response) -> None:
        """Wait for Contentful's rate-limit window before the SDK retries a 429."""
        if response.status_code == 429:
            reset = response.headers.get("X-Contentful-RateLimit-Reset")
            if reset:
                self.logger.warning("Rate limited by Contentful; waiting %ss", reset)
                time.sleep(float(reset))
        super().validate_response(response)
