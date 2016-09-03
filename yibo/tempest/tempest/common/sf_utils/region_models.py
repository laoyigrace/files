from oslo_db.sqlalchemy import models
from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import String, Text
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.ext.declarative import declarative_base

BASE = declarative_base()


class RegionPolicy(BASE, models.ModelBase):
    __tablename__ = 'policy'
    meter = Column(String(255), primary_key=True)
    price = Column(DECIMAL(48, 20), nullable=False)
    enabled = Column(Boolean, nullable=False)
    description = Column(Text)


class RegionBalance(BASE, models.ModelBase):
    __tablename__ = 'balance'
    tenant_id = Column(String(255), primary_key=True)
    balance = Column(DECIMAL(32, 8), nullable=False)
    free_account_balance = Column(DECIMAL(32, 8), nullable=False)
    base_account_balance = Column(DECIMAL(32, 8), nullable=False)
    deficit_time = Column(DateTime)

