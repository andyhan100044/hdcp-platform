from typing import List, Optional
import strawberry
from strawberry.types import Info
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.stock import StockPrice
from app.models.iot import SensorReading
from app.models.ecommerce import ProductPrice
from app.models.carbon import CarbonCreditProject

# GraphQL Types
@strawberry.type
class StockPriceType:
    id: str
    symbol: str
    price: float
    volume: int
    change: float
    change_percent: float
    timestamp: datetime
    source: str

@strawberry.type
class SensorReadingType:
    id: str
    sensor_id: str
    location: str
    temperature: float
    humidity: float
    battery: int
    signal: int
    status: str
    timestamp: datetime

@strawberry.type
class ProductPriceType:
    id: str
    product_id: str
    product_name: str
    price: float
    currency: str
    availability: str
    source: str
    timestamp: datetime

@strawberry.type
class CarbonCreditProjectType:
    id: str
    project_id: str
    project_name: str
    standard: str
    location: str
    project_type: str
    total_credits: int
    co2_offset: float
    forest_area: Optional[float] = None
    communities: Optional[int] = None

@strawberry.type
class Query:
    @strawberry.field
    async def stocks(self, info: Info, symbol: Optional[str] = None, limit: Optional[int] = 50) -> List[StockPriceType]:
        db: AsyncSession = info.context["db"]
        query = select(StockPrice)

        if symbol:
            query = query.where(StockPrice.symbol == symbol.upper())

        query = query.limit(limit)
        result = await db.execute(query)
        stocks = result.scalars().all()

        return [
            StockPriceType(
                id=str(stock.id),
                symbol=stock.symbol,
                price=float(stock.price),
                volume=stock.volume,
                change=float(stock.change),
                change_percent=float(stock.change_percent),
                timestamp=stock.timestamp,
                source=stock.source
            )
            for stock in stocks
        ]

    @strawberry.field
    async def sensors(self, info: Info, location: Optional[str] = None, status: Optional[str] = None, limit: Optional[int] = 50) -> List[SensorReadingType]:
        db: AsyncSession = info.context["db"]
        query = select(SensorReading)

        if location:
            query = query.where(SensorReading.location.ilike(f"%{location}%"))

        if status:
            query = query.where(SensorReading.status == status)

        query = query.limit(limit)
        result = await db.execute(query)
        sensors = result.scalars().all()

        return [
            SensorReadingType(
                id=str(sensor.id),
                sensor_id=sensor.sensor_id,
                location=sensor.location,
                temperature=float(sensor.temperature),
                humidity=float(sensor.humidity),
                battery=sensor.battery,
                signal=sensor.signal,
                status=sensor.status,
                timestamp=sensor.timestamp
            )
            for sensor in sensors
        ]

    @strawberry.field
    async def products(self, info: Info, product_name: Optional[str] = None, availability: Optional[str] = None, limit: Optional[int] = 50) -> List[ProductPriceType]:
        db: AsyncSession = info.context["db"]
        query = select(ProductPrice)

        if product_name:
            query = query.where(ProductPrice.product_name.ilike(f"%{product_name}%"))

        if availability:
            query = query.where(ProductPrice.availability == availability)

        query = query.limit(limit)
        result = await db.execute(query)
        products = result.scalars().all()

        return [
            ProductPriceType(
                id=str(product.id),
                product_id=product.product_id,
                product_name=product.product_name,
                price=float(product.price),
                currency=product.currency,
                availability=product.availability,
                source=product.source,
                timestamp=product.timestamp
            )
            for product in products
        ]

    @strawberry.field
    async def carbon_credits(self, info: Info, standard: Optional[str] = None, project_type: Optional[str] = None, limit: Optional[int] = 50) -> List[CarbonCreditProjectType]:
        db: AsyncSession = info.context["db"]
        query = select(CarbonCreditProject)

        if standard:
            query = query.where(CarbonCreditProject.standard == standard)

        if project_type:
            query = query.where(CarbonCreditProject.project_type.ilike(f"%{project_type}%"))

        query = query.limit(limit)
        result = await db.execute(query)
        projects = result.scalars().all()

        return [
            CarbonCreditProjectType(
                id=str(project.id),
                project_id=project.project_id,
                project_name=project.project_name,
                standard=project.standard,
                location=project.location,
                project_type=project.project_type,
                total_credits=int(project.total_credits),
                co2_offset=float(project.co2_offset),
                forest_area=float(project.forest_area) if project.forest_area else None,
                communities=int(project.communities) if project.communities else None
            )
            for project in projects
        ]

    @strawberry.field
    async def stats(self, info: Info) -> dict:
        db: AsyncSession = info.context["db"]

        stocks_count = await db.execute(select(StockPrice))
        sensors_count = await db.execute(select(SensorReading))
        products_count = await db.execute(select(ProductPrice))
        carbon_count = await db.execute(select(CarbonCreditProject))

        return {
            "total_stocks": len(stocks_count.scalars().all()),
            "total_sensors": len(sensors_count.scalars().all()),
            "total_products": len(products_count.scalars().all()),
            "total_carbon_projects": len(carbon_count.scalars().all())
        }

# Input Types for Mutations
@strawberry.input
class StockPriceInput:
    symbol: str
    price: float
    volume: int
    change: float
    change_percent: float
    source: str

@strawberry.input
class SensorReadingInput:
    sensor_id: str
    location: str
    temperature: float
    humidity: float
    battery: int
    signal: int
    status: str

@strawberry.input
class ProductPriceInput:
    product_id: str
    product_name: str
    price: float
    currency: str
    availability: str
    source: str

@strawberry.input
class CarbonCreditProjectInput:
    project_id: str
    project_name: str
    standard: str
    location: str
    project_type: str
    total_credits: int
    co2_offset: float
    forest_area: Optional[float] = None
    communities: Optional[int] = None

@strawberry.type
class Mutation:
    @strawberry.field
    async def create_stock(self, info: Info, input: StockPriceInput) -> StockPriceType:
        from app.models.stock import StockPrice
        db: AsyncSession = info.context["db"]

        stock = StockPrice(
            symbol=input.symbol.upper(),
            price=input.price,
            volume=input.volume,
            change=input.change,
            change_percent=input.change_percent,
            source=input.source
        )

        db.add(stock)
        await db.commit()
        await db.refresh(stock)

        return StockPriceType(
            id=str(stock.id),
            symbol=stock.symbol,
            price=float(stock.price),
            volume=stock.volume,
            change=float(stock.change),
            change_percent=float(stock.change_percent),
            timestamp=stock.timestamp,
            source=stock.source
        )

    @strawberry.field
    async def create_sensor(self, info: Info, input: SensorReadingInput) -> SensorReadingType:
        from app.models.iot import SensorReading
        db: AsyncSession = info.context["db"]

        sensor = SensorReading(
            sensor_id=input.sensor_id,
            location=input.location,
            temperature=input.temperature,
            humidity=input.humidity,
            battery=input.battery,
            signal=input.signal,
            status=input.status
        )

        db.add(sensor)
        await db.commit()
        await db.refresh(sensor)

        return SensorReadingType(
            id=str(sensor.id),
            sensor_id=sensor.sensor_id,
            location=sensor.location,
            temperature=float(sensor.temperature),
            humidity=float(sensor.humidity),
            battery=sensor.battery,
            signal=sensor.signal,
            status=sensor.status,
            timestamp=sensor.timestamp
        )

# Create schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
