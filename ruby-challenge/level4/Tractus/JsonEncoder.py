import uuid
import json
import re

class NoIndent(object):
    def __init__(self, value):
        self.value = value


class MyEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super(MyEncoder, self).__init__(*args, **kwargs)
        self.kwargs = dict(kwargs)
        del self.kwargs['indent']
        self._replacement_map = {}

    def default(self, o):
        if isinstance(o, NoIndent):
            key = uuid.uuid4().hex
            self._replacement_map[key] = json.dumps(o.value, **self.kwargs)
            return "@@%s@@" % (key,)
        else:
            return super(MyEncoder, self).default(o)
    
    def encode(self, o):
        result = super(MyEncoder, self).encode(o)
        for k, v in iter(self._replacement_map.items()):
            result = result.replace('"@@%s@@"' % (k,), v)
        return result
