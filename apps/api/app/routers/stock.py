"""
Stock Price Router
API endpoints for stock price monitoring
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.stock import StockPrice, StockIndicator
from app.schemas.stock import (
    StockPriceCreate,
    StockPriceResponse,
    StockPriceUpdate,
    StockSummary,
    StockHistoryRequest,
    StockIndicatorResponse
)
from app.schemas.response import PaginatedResponse, SuccessResponse

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.post("/", response_model=StockPriceResponse)
async def create_stock_price(
    data: StockPriceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new stock price record"""
    # TODO: Implement price validation
    # TODO: Check for duplicate entries
    # TODO: Calculate price change automatically

    from app.services.crud import CRUDService
    service = CRUDService(StockPrice, db)
    stock = await service.create(data)
    return stock


@router.get("/{symbol}", response_model=StockPriceResponse)
async def get_stock_price(
    symbol: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the latest stock price for a symbol"""
    from sqlalchemy import select, desc
    query = (
        select(StockPrice)
        .where(StockPrice.symbol == symbol)
        .order_by(desc(StockPrice.timestamp))
        .limit(1)
    )

    from sqlalchemy import exc
    try:
        from sqlalchemy import Result
        result: Result = await db.execute(query)
        stock = result.scalar_one_or_none()

        if not stock:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
        return stock
    except exc.SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/history", response_model=List[StockPriceResponse])
async def get_stock_history(
    symbol: str,
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records"),
    db: AsyncSession = Depends(get_db)
):
    """Get historical stock prices"""
    from sqlalchemy import select, desc

    query = select(StockPrice).where(StockPrice.symbol == symbol)

    if start_date:
        query = query.where(StockPrice.timestamp >= start_date)
    if end_date:
        query = query.where(StockPrice.timestamp <= end_date)

    query = query.order_by(desc(StockPrice.timestamp)).limit(limit)

    from sqlalchemy import exc, Result
    try:
        result: Result = await db.execute(query)
        return result.scalars().all()
    except exc.SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=PaginatedResponse[StockPriceResponse])
async def list_stock_prices(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    db: AsyncSession = Depends(get_db)
):
    """List stock prices with pagination and filtering"""
    from sqlalchemy import select, func, exc, Result

    try:
        # Build base query
        query = select(StockPrice)

        # Apply filters
        if symbol:
            query = query.where(StockPrice.symbol == symbol)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result: Result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        # Execute query
        result: Result = await db.execute(query)
        stocks = result.scalars().all()

        return PaginatedResponse.create(
            data=stocks,
            page=page,
            page_size=size,
            total=total
        )
    except exc.SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{symbol}", response_model=StockPriceResponse)
async def update_stock_price(
    symbol: str,
    data: StockPriceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a stock price record"""
    # First get the latest record
    from sqlalchemy import select, desc, Result
    query = (
        select(StockPrice)
        .where(StockPrice.symbol == symbol)
        .order_by(desc(StockPrice.timestamp))
        .limit(1)
    )

    result: Result = await db.execute(query)
    stock = result.scalar_one_or_none()

    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")

    # Update the record
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(stock, field, value)

    await db.commit()
    await db.refresh(stock)
    return stock


@router.delete("/{symbol}", response_model=SuccessResponse)
async def delete_stock_price(
    symbol: str,
    timestamp: Optional[datetime] = Query(None, description="Specific timestamp to delete"),
    db: AsyncSession = Depends(get_db)
):
    """Delete a stock price record"""
    from sqlalchemy import select, exc, Result

    try:
        query = select(StockPrice).where(StockPrice.symbol == symbol)

        if timestamp:
            query = query.where(StockPrice.timestamp == timestamp)
        else:
            # Delete all records for this symbol
            pass

        result: Result = await db.execute(query)
        stocks = result.scalars().all()

        if not stocks:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")

        for stock in stocks:
            await db.delete(stock)

        await db.commit()

        return SuccessResponse(message=f"Deleted {len(stocks)} stock price record(s)")
    except exc.SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/summary", response_model=StockSummary)
@benchmark_query("stock_summary")
@cached("stock_summary", expire=60, key_func=lambda symbol: symbol.lower())
async def get_stock_summary(
    symbol: str,
    db: AsyncSession = Depends(get_db)
):
    """Get stock summary with current price and statistics - Optimized with caching"""
    from app.core.performance import QueryOptimizer

    try:
        # Use optimized query with single database round trip
        result = await QueryOptimizer.optimize_stock_summary_query(db, symbol)

        if not result:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")

        return StockSummary(
            symbol=symbol,
            current_price=result["current_price"],
            price_change=result["price_change"],
            price_change_percent=result["price_change_percent"],
            volume=result["volume"],
            market_cap=None,  # TODO: Add market cap calculation
            high_52w=result["high_52w"],
            low_52w=result["low_52w"],
            last_updated=result["last_updated"]
        )
    except exc.SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/indicators", response_model=List[StockIndicatorResponse])
async def get_stock_indicators(
    symbol: str,
    indicator_type: Optional[str] = Query(None, description="Filter by indicator type"),
    limit: int = Query(50, ge=1, le=200, description="Number of records"),
    db: AsyncSession = Depends(get_db)
):
    """Get technical indicators for a stock"""
    from sqlalchemy import select, desc, exc, Result

    try:
        query = select(StockIndicator).where(StockIndicator.symbol == symbol)

        if indicator_type:
            query = query.where(StockIndicator.indicator_type == indicator_type)

        query = query.order_by(desc(StockIndicator.timestamp)).limit(limit)

        result: Result = await db.execute(query)
        return result.scalars().all()
    except exc.SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
