from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import MetaData, Integer, String, ForeignKey, Float, DateTime, Column, Table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadate: MetaData = MetaData()

class SalesIn(BaseModel):
    datetime_of_sale: datetime
    quantity_of_goods_sold: int
    product_id: int
    stores_id: int

class stores(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True)
    address = Column(String, nullable=False)


class product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True)
    product_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)


class sales(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True)
    datetime_of_sale = Column(DateTime)
    quantity_of_goods_sold = Column(Integer)
    product_id = Column(Integer, ForeignKey("product.id"))
    stores_id = Column(Integer, ForeignKey("stores.id"))


stores = Table(
    "stores",
    metadate,
    Column("id", Integer, primary_key=True),
    Column("address", String, nullable=False),
)

product = Table(
    "product",
    metadate,
    Column("id", Integer, primary_key=True),
    Column("product_name", String, nullable=False),
    Column("price", Float, nullable=False),
)

sales = Table(
    "sales",
    metadate,
    Column("id", Integer, primary_key=True),
    Column("datetime_of_sale", DateTime),
    Column("quantity_of_goods_sold", Integer),
    Column("product_id", Integer, ForeignKey("product.id")),
    Column("stores_id", Integer, ForeignKey("stores.id")),
)