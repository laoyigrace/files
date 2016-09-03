# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 Piston Cloud Computing, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
SQLAlchemy models for cplog data.
"""

from oslo_db.sqlalchemy import models
from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.ext.declarative import declarative_base

BASE = declarative_base()


class SfConfig(BASE, models.ModelBase):
    __tablename__ = 'config'
    id = Column(String(255), primary_key=True)
    setup_time = Column(DateTime, nullable=False)
    last_time = Column(DateTime, nullable=False)
    last_state = Column(String(255), nullable=False)
    enabled = Column(Boolean, nullable=False)
    lock_host = Column(String(255), nullable=True)
    lock_time = Column(DateTime, nullable=True)


class SfBalance(BASE, models.ModelBase):
    __tablename__ = 'balance'
    tenant_id = Column(String(255), primary_key=True)
    balance = Column(DECIMAL(32, 8), nullable=False)
    free_account_balance = Column(DECIMAL(32, 8), nullable=False)
    base_account_balance = Column(DECIMAL(32, 8), nullable=False)
    deficit_time = Column(DateTime)


class SfConsume(BASE, models.ModelBase):
    __tablename__ = 'consume'
    date = Column(String(32), primary_key=True)
    tenant_id = Column(String(255), primary_key=True, index=True)
    type = Column(String(64), primary_key=True)
    resource_id = Column(String(255), primary_key=True)
    status = Column(String(64), primary_key=True)
    cost = Column(DECIMAL(32, 8), nullable=False)
    run_time = Column(Integer, nullable=False)


class SfFlow(BASE, models.ModelBase):
    __tablename__ = 'flow'
    region = Column(String(32), primary_key=True)
    datetime = Column(DateTime, primary_key=True)
    tenant_id = Column(String(255), primary_key=True)
    type = Column(String(64), primary_key=True)
    resource_id = Column(String(255), primary_key=True)
    resource_name = Column(String(255))
    status = Column(String(64), primary_key=True)
    cost = Column(DECIMAL(32, 8), nullable=False)
    detail = Column(String(1024))
    version = Column(Integer, nullable=False)


class SfPay(BASE, models.ModelBase):
    __tablename__ = 'pay'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)
    base_account_pay = Column(DECIMAL(32, 8), nullable=False)
    free_account_pay = Column(DECIMAL(32, 8), nullable=False)
    balance = Column(DECIMAL(32, 8), nullable=False)
    free_account_balance = Column(DECIMAL(32, 8), nullable=False)
    base_account_balance = Column(DECIMAL(32, 8), nullable=False)
    time = Column(DateTime, nullable=False)
    remarks = Column(String(255))
    mode = Column(String(255))
    author = Column(String(255))








