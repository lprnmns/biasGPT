"""Declarative base and mixins for ORM models."""

from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    """Declarative base with shared metadata and JSON mapping."""

    metadata = MetaData()
    type_annotation_map = {
        Dict[str, Any]: JSON,
        List[Dict[str, Any]]: JSON,
        list: JSON,
        dict: JSON,
    }


__all__ = ["Base"]
