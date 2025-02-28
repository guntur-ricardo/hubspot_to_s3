import logging

import attr
import requests

logger = logging.getLogger(__name__)


@attr.s(slots=True)
class HubspotAPI:
    config = attr.ib()
    secrets = attr.ib()
    _session = attr.ib()

    @_session.default
    def default_session(self):
        querystring = {}
        headers = {}

        if getattr(self.secrets, 'hubspot_hapikey'):
            querystring['hapikey'] = self.secrets.hubspot_hapikey
        elif getattr(self.secrets, 'hubspot_access_token'):
            headers = {'Authorization': f'Bearer {self.secrets.hubspot_access_token}'}

        s = requests.Session()
        s.params = querystring
        s.headers = headers

        return s

    @staticmethod
    def relative_entity_url(entity, key=None):
        v1 = {'contacts': 'contact'}
        v2 = {'companies': 'companies'}

        if entity in v1:
            rtn = f'{entity}/v1/{v1[entity]}'
        else:
            rtn = f'{entity}/v2/{v2[entity]}'

        if key is not None:
            rtn += f'/{key}'

        return rtn

    def absolute_url(self, relative):
        return f'https://api.hubapi.com/{relative}'

    def get_fqdn(self, entity, key=None):
        return self.absolute_url(self.relative_entity_url(entity, key))

    def _get(self, url, **kwargs):
        kwargs.setdefault('timeout', (3.05, 60))
        return self._session.get(url, **kwargs)

    def _post(self, url, *args, **kwargs):
        kwargs.setdefault('timeout', (3.05, 60))
        return self._session.post(url, *args, **kwargs)

    def _put(self, url, *args, **kwargs):
        kwargs.setdefault('timeout', (3.05, 60))
        return self._session.put(url, *args, **kwargs)

    def create(self, entity, data):
        logger.info(f'Attempting to create a {entity}')
        data = self._post(self.get_fqdn(entity), json=data)
        return data

    def replace(self, entity, key, data):
        logger.info(f'Attempting to replace a {entity}/{key}')
        data = self._put(self.get_fqdn(entity, key), json=data)
        return data