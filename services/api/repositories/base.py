"""Common repository helpers for async SQLAlchemy operations."""

from __future__ import annotations

from typing import Any, Generic, Iterable, Optional, Sequence, TypeVar

from sqlalchemy import Select, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic repository providing CRUD helpers for a mapped model."""

    model: type[T]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, **filters: Any) -> Optional[T]:
        stmt = select(self.model).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, *, limit: Optional[int] = None, offset: int = 0, filters: Optional[dict[str, Any]] = None) -> Sequence[T]:
        stmt: Select[Any] = select(self.model)
        if filters:
            stmt = stmt.filter_by(**filters)
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, **data: Any) -> T:
        instance = self.model(**data)  # type: ignore[call-arg]
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, filters: dict[str, Any], values: dict[str, Any]) -> int:
        stmt = (
            update(self.model)
            .filter_by(**filters)
            .values(**values)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0

    async def delete(self, **filters: Any) -> int:
        stmt = delete(self.model).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.rowcount or 0

    async def exists(self, **filters: Any) -> bool:
        stmt = select(self.model).filter_by(**filters).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def refresh(self, instance: T, attrs: Optional[Iterable[InstrumentedAttribute[Any]]] = None) -> None:
        await self.session.refresh(instance, attribute_names=list(attrs) if attrs else None)
