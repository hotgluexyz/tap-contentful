"""Stream type classes for tap-contentful."""

from __future__ import annotations

from typing import ClassVar

from hotglue_singer_sdk import typing as th
from typing_extensions import override

from tap_contentful.client import ContentfulStream

# Entry `fields` keys depend on each space's content types, so the nested
# objects are passed through as-is.
ANY_OBJECT = th.CustomType({"type": ["object", "null"]})


class EntriesStream(ContentfulStream):
    """Published entries of every content type (``GET /entries``)."""

    name = "entries"
    path = "/entries"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "updated_at"
    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Copied from sys.id"),
        th.Property("updated_at", th.DateTimeType, description="Copied from sys.updatedAt"),
        th.Property("sys", ANY_OBJECT),
        th.Property("fields", ANY_OBJECT),
        th.Property("metadata", ANY_OBJECT),
    ).to_dict()

    @override
    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        """Lift the key and bookmark fields out of ``sys`` to the top level."""
        row["id"] = row["sys"]["id"]
        row["updated_at"] = row["sys"]["updatedAt"]
        return row
