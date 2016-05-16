
from functools import partial
import importlib
import types

from aeon.utils.probe import probe
from aeon.nxos.connector import NxosConnector as Connector
from aeon.nxos import exceptions as NxosExc


__all__ = ['NxosDevice']


class NxosDevice(object):
    DEFAULT_PROBE_TIMEOUT = 3

    def __init__(self, target, **kwargs):
        """
        :param target: hostname or ipaddr of target device
        :param kwargs:
            'user' : login user-name, defaults to "admin"
            'passwd': login password, defaults to "admin
        """
        self.target = target

        user = kwargs.get('user', 'admin')
        passwd = kwargs.get('passwd', 'admin')

        self.api = Connector(hostname=self.target, user=user, passwd=passwd)

        self.facts = {}

        if 'no_probe' not in kwargs:
            self.probe(**kwargs)

        if 'no_gather_facts' not in kwargs:
            self.gather_facts()

    def probe(self, **kwargs):
        timeout = kwargs.get('timeout') or self.DEFAULT_PROBE_TIMEOUT
        ok, elapsed = probe(self.target, protocol=self.api.proto, timeout=timeout)
        if not ok:
            raise NxosExc.ProbeError()

    def close(self):
        # nothing to do for close at this time, yo!
        pass

    def gather_facts(self):
        exec_show = partial(self.api.exec_opcmd, resp_fmt='json')

        facts = self.facts

        facts['vendor'] = 'cisco'
        facts['os'] = 'nxos'

        got = exec_show('show hostname')
        facts['fqdn'] = got['hostname']
        facts['hostname'], _, facts['domain_name'] = facts['fqdn'].partition('.')

        got = exec_show('show hardware')
        facts['os_version'] = got['kickstart_ver_str']
        facts['chassis_id'] = got['chassis_id']
        facts['virtual'] = bool('NX-OSv' in facts['chassis_id'])

        row = got['TABLE_slot']['ROW_slot']['TABLE_slot_info']['ROW_slot_info'][0]
        facts['serial_number'] = row['serial_num']
        facts['hw_model'] = row['model_num']
        facts['hw_part_number'] = row['part_num']
        facts['hw_part_version'] = row['part_revision']
        facts['hw_version'] = row['hw_ver']

    def __getattr__(self, item):
        # ##
        # ## this is rather perhaps being a bit "too clever", but I sometimes
        # ## can't help myself ;-P
        # ##

        # if the named addon module does not exist, this will raise
        # an ImportError.  We might want to catch this and handle differently

        mod = importlib.import_module('.addons.%s' % item, package=__package__)

        def wrapper(*vargs, **kvargs):
            cls = getattr(mod, item.capitalize())
            self.__dict__[item] = cls(self, *vargs, **kvargs)

        return wrapper
