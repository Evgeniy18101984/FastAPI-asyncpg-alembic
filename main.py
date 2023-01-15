import databases
from datetime import datetime
from typing import AsyncGenerator
from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DB_HOST, DB_USER, DB_NAME, DB_PASS, DB_PORT
from models.models import stores, product, SalesIn, sales

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
Base = declarative_base()
DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
database = databases.Database(DB_URL)

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app = FastAPI(
    title="Отчёт по продажам"
)

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# GET-запрос на получение всех товарных позиций

@app.get("/Product")
async def all_product(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(product).order_by(product.c.id))
    return result.all()


# GET-запрос на получение всех магазинов

@app.get("/Stores")
async def all_stores(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(stores).order_by(stores.c.id))
    return result.all()


#POST-запрос с json-телом для сохранения данных о произведенной продаже (id товара + id магазина)

@app.post("/sales/", response_model=SalesIn)
async def create_sale(sale: SalesIn):
    query = sales.insert().values(datetime_of_sale=datetime.now(), quantity_of_goods_sold=sale.quantity_of_goods_sold,
    product_id=sale.product_id, stores_id=sale.stores_id)
    last_record_id = await database.execute(query)
    return {**sale.dict(), "id": last_record_id}

#GET-запрос на получение данных по топ 10 самых доходных магазинов за месяц (id + адрес + суммарная выручка)

@app.get("/TOP-10 Stores")
async def top_stores(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(
        """
        select stores.id, stores.address, sum(quantity_of_goods_sold*price) as total_revenue from sales as sl
        join product on product.id = sl.product_id
        join stores on stores.id = sl.stores_id
        where datetime_of_sale > current_date - interval '1 months'
        group by stores.id
        order by total_revenue desc
        limit 10
        """)
    return result.all()


# GET-запрос на получение данных по топ 10 самых продаваемых товаров (id + наименование + количество проданных товаров)

@app.get("/TOP-10 Products")
async def top_products(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(
        """
        select product.id, product.product_name, sum(quantity_of_goods_sold) as products_sold from sales as sl
        join product on product.id = sl.product_id
        join stores on stores.id = sl.stores_id
        GROUP BY product.id
        order by products_sold desc
        limit 10
        """)
    return result.all()