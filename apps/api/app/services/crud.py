"""
Generic CRUD Service
Reusable CRUD operations for all models
"""
from typing import TypeVar, Type, Generic, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.engine import Result

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class CRUDService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic CRUD service for database operations
    Can be inherited by specific services
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, data: CreateSchemaType) -> ModelType:
        """
        Create a new record
        """
        db_obj = self.model(**data.dict() if hasattr(data, 'dict') else data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get(self, id: int) -> Optional[ModelType]:
        """
        Get a record by ID
        """
        query = select(self.model).where(self.model.id == id)
        result: Result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get multiple records with optional filtering
        """
        query = select(self.model)

        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)

        query = query.offset(skip).limit(limit)
        result: Result = await self.db.execute(query)
        return result.scalars().all()

    async def update(
        self,
        id: int,
        data: UpdateSchemaType
    ) -> Optional[ModelType]:
        """
        Update a record
        """
        query = select(self.model).where(self.model.id == id)
        result: Result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()

        if not db_obj:
            return None

        update_data = data.dict(exclude_unset=True) if hasattr(data, 'dict') else data
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        """
        Delete a record
        """
        query = select(self.model).where(self.model.id == id)
        result: Result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()

        if not db_obj:
            return False

        await self.db.delete(db_obj)
        await self.db.commit()
        return True

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records
        """
        query = select(self.model)

        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)

        result: Result = await self.db.execute(query)
        return len(result.scalars().all())

    async def exists(self, filters: Dict[str, Any]) -> bool:
        """
        Check if a record exists
        """
        query = select(self.model)

        for field, value in filters.items():
            query = query.where(getattr(self.model, field) == value)

        result: Result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
