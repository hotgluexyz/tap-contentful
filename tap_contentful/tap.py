"""Contentful tap class."""

from __future__ import annotations

from hotglue_singer_sdk import Stream, Tap
from hotglue_singer_sdk import typing as th  # JSON schema typing helpers
from typing_extensions import override

from tap_contentful.streams import (
    EntriesStream,
)

STREAM_TYPES = [
    EntriesStream,
]


class TapContentful(Tap):
    """Singer tap for Contentful."""

    name = "tap-contentful"

    # Setting names match the deprecated gitlab.com/hotglue/tap-contentful config.
    config_jsonschema = th.PropertiesList(
        th.Property(
            "access_token",
            th.StringType,
            required=True,
            description="Contentful Content Delivery API access token",
        ),
        th.Property(
            "space_id",
            th.StringType,
            required=True,
            description="ID of the Contentful space to extract",
        ),
        th.Property(
            "environment",
            th.StringType,
            description="Contentful environment ID",
            default="master",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Only sync entries updated at or after this time",
            default="2000-01-01T00:00:00Z",
        ),
        th.Property(
            "api_url",
            th.StringType,
            description="Base URL for the Contentful API",
            default="https://cdn.contentful.com",
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapContentful.cli()
