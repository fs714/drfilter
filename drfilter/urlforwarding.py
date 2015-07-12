import requests
import re
import json
import webob.dec


def url_forwarding_factory(global_conf, **local_conf):
    def filter(app):
        return UrlForwarding(app, global_conf, local_conf)
    return filter


class UrlForwarding(object):
    def __init__(self, app, global_conf, local_conf):
        self.app = app

        if 'ip' in local_conf:
            self.ip = local_conf['ip']
        else:
            self.ip = '127.0.0.1'

        if 'port' in local_conf:
            self.port = local_conf['port']
        else:
            self.port = 10080

    @webob.dec.wsgify
    def __call__(self, req):
        req_url = 'http://' + str(self.ip) + ':' + str(self.port) + '/'
        headers = {'Content-type': 'application/json',
                   'openstack-service': self.app.__repr__()}
        forwarding_data = {}
        forwarding_data['Request'] = self.update_env(req)

        res = req.get_response(self.app)
        forwarding_data['Response'] = res.json

        try:
            requests.post(req_url, data=json.dumps(forwarding_data),
                          headers=headers, timeout=1)
        finally:
            return res

    def update_env(self, req):
        env = req.environ.copy()

        for name, value in sorted(env.items()):
            if self.has_object_address(str(value)):
                del env[name]

        env['wsgi.input'] = req.body
        return env

    def has_object_address(self, value):
        pattern = re.compile(r'.*0x[0-9a-f]{12}')
        match = pattern.match(value)
        if match:
            return True
        else:
            return False
