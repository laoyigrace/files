import datetime
import operator
import sqlalchemy

from decimal import Decimal

from oslo_db.sqlalchemy import session
from oslo_db.sqlalchemy import utils
from oslo_utils import timeutils


import billcenter_models


class CenterConnection(object):
    """Database interface."""

    def __init__(self, url):
        self._FACADE = session.EngineFacade(url, autocommit=True)

    def consume_history(self):
        sess = self._FACADE.get_session()
        q = utils.model_query(
            billcenter_models.SfConsume,
            sess)
        q = q.filter(billcenter_models.SfConsume.type == 'bill')

        return q.all()

    def delete_consume(self):
        sess = self._FACADE.get_session()
        q = utils.model_query(billcenter_models.SfConsume, sess)
        q = q.filter(billcenter_models.SfConsume.resource_id == 'tempest_test')
        row = q.delete()
        if not row:
            raise Exception('consume not found')

    def delete_flow(self):
        sess = self._FACADE.get_session()
        q = utils.model_query(billcenter_models.SfFlow, sess)
        q = q.filter(billcenter_models.SfFlow.resource_id == 'tempest_test')
        row = q.delete()
        if not row:
            raise Exception('flow not found')

    def delete_balance(self, tenant_id):
        sess = self._FACADE.get_session()
        q = utils.model_query(billcenter_models.SfBalance, sess)
        q = q.filter(billcenter_models.SfBalance.tenant_id == tenant_id)
        row = q.delete()
        if not row:
            raise Exception('tenant %s not found' % tenant_id)

    def delete_pay(self, tenant_id):
        sess = self._FACADE.get_session()
        q = utils.model_query(billcenter_models.SfPay, sess)
        q = q.filter(billcenter_models.SfPay.tenant_id == tenant_id)
        row = q.delete()
        if not row:
            raise Exception('tenant %s not found' % tenant_id)

    def get_flow(self):
        sess = self._FACADE.get_session()
        q = utils.model_query(billcenter_models.SfFlow, sess)
        q = q.filter(billcenter_models.SfFlow.resource_id == 'tempest_test')
        return q.count()
