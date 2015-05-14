import requests
import webob.dec


def url_forwarding_factory(global_conf, **local_conf):
    def filter(app):
        return UrlForwarding(app, global_conf, local_conf)
    return filter


class UrlForwarding(object):
    def __init__(self, app, global_conf, local_conf):
        self.app = app

        if local_conf['ip']:
            self.ip = local_conf['ip']
        else:
            self.ip = '127.0.0.1'

        if local_conf['port']:
            self.port = local_conf['port']
        else:
            self.port = 11080

    @webob.dec.wsgify
    def __call__(self, req):
        """
        parts = []
        for name, value in sorted(req.environ.items()):
            parts.append('%s: %r' % (name, value))
            req.body = '\n'.join(parts)

        req_url = 'http://' + str(self.ip) + ':' + str(self.port) \
            + '/' + '\n'.join(parts) + '\n'
        requests.request(req_url)
        """
        req_url = 'http://' + str(self.ip) + ':' + str(self.port) + '/'
        requests.get(req_url, data=req.environ)

        return req.get_response(self.app)
