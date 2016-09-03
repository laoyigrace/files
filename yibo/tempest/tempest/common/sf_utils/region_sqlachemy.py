import datetime
import operator
import sqlalchemy

from decimal import Decimal

from oslo_db.sqlalchemy import session
from oslo_db.sqlalchemy import utils

import region_models


class RegionConnection(object):
    """Database interface."""

    def __init__(self, url):
        self._FACADE = session.EngineFacade(url, autocommit=True)

    def region_policy_get(self):
        sess = self._FACADE.get_session()
        ret = sess.query(region_models.RegionPolicy).all()
        return ret

    def region_policy_delete(self, meters):
        sess = self._FACADE.get_session()
        with sess.begin():
            for meter in meters:
                if meter == 'enable':
                    raise Exception('Can not delete enable')
                q = utils.model_query(
                    region_models.RegionPolicy,
                    sess)
                q = q.filter(region_models.RegionPolicy.meter == meter)
                r = q.delete()
                if not r:
                    raise Exception('%s not found' % meter)

    def region_balance_get(self, tenant_id):
        sess = self._FACADE.get_session()
        q = utils.model_query(
            region_models.RegionBalance,
            sess)
        q = q.filter(region_models.RegionBalance.tenant_id == tenant_id)
        return q.first()

    def region_balance_delete(self, tenant_id):
        sess = self._FACADE.get_session()
        q = utils.model_query(region_models.RegionBalance, sess)
        q = q.filter(region_models.RegionBalance.tenant_id == tenant_id)
        row = q.delete()
        if not row:
            raise Exception('tenant %s not found' % tenant_id)
