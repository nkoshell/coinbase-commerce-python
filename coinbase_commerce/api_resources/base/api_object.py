import json

from coinbase_commerce import util


class APIObject(dict):
    """
    Generic class used to represent a JSON response from the Coinbase API.
    """

    def __init__(self, api_client=None, data=None):
        super().__init__()
        data = data or {}
        self._api_client = getattr(self, '_api_client', api_client)
        self._unsaved_values = set()
        self._passing_values = set()
        self.refresh_from(**data)

    def refresh_from(self, **kwargs):
        # update fields with new data if any
        removed = set(self.keys()) - set(kwargs)
        self._passing_values = self._passing_values | removed
        self._unsaved_values = set()
        self.clear()
        self._passing_values = self._passing_values - set(kwargs)
        # perform conversion for nested data
        for k, v in kwargs.items():
            converted_value = util.convert_to_api_object(v, api_client=self._api_client)
            super().__setitem__(k, converted_value)

    # do not include private and protected fields into json serialization
    def __setattr__(self, k, v):
        if k[0] == '_' or k in self.__dict__:
            return super().__setattr__(k, v)
        self[k] = v
        return None

    def __getattr__(self, k):
        if k[0] == '_':
            raise AttributeError(k)
        try:
            return self[k]
        except KeyError as err:
            raise AttributeError(*err.args)

    def __delattr__(self, k):
        if k[0] == '_' or k in self.__dict__:
            return super().__delattr__(k)
        else:
            del self[k]

    def __str__(self):
        try:
            return json.dumps(self, sort_keys=True, indent=2)
        except TypeError:
            return '(invalid JSON)'

    def __repr__(self):
        return '<{} id={}> Serialized: {}'.format(type(self).__name__,
                                                  self.get('id', 'No ID'),
                                                  str(self))