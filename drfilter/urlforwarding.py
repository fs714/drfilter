import requests
import json
import webob.dec
import thread
import logging


def url_forwarding_factory(global_conf, **local_conf):
    def filter(app):
        return UrlForwarding(app, global_conf, local_conf)
    return filter


def post_response(req_url, env, data, headers,lib_type, timeout=1):
    logger = logging.getLogger('drfilter')
    logger.setLevel(logging.DEBUG)
    file_path='/var/log/'+lib_type+'/drfilter.log'
    fh = logging.FileHandler(file_path)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    try:
        res = requests.post(req_url, data=data, headers=headers,
                            timeout=timeout)
        logger.info('------------------------------------------')
        for key, value in sorted(env.items()):
            logger.info(key + " = " + repr(value))
        logger.info(data)
        logger.info(json.dumps(res, indent=4, sort_keys=True))
    finally:
        logger.removeHandler(fh)
        thread.exit()


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

        if 'lib_type' in local_conf:
            self.lib_type = local_conf['lib_type']
        else:
            self.lib_type = None

    @webob.dec.wsgify
    def __call__(self, req):
        res = req.get_response(self.app)
        env = req.environ
        method = env.get('REQUEST_METHOD')
        if (method == 'DELETE') or (method == 'PUT') or (method == 'POST'):
            if (env.get('HTTP_X_TENANT') != 'service'):
                if (res.content_length > 0):
                    try:
                        response = res.json
                    except: 
                        return res
                else:
                    response = {}
                if (response != {}):
                    temp=response.values()[0]
                    if (temp.has_key('code')):
                        res_code=temp['code']
                        if (res_code !=200):
                            return res
                if (str(response).find("Error")):
                    return res   
                headers = {'Content-type': 'application/json',
                               'openstack-service': self.app.__repr__()}
                forwarding_data = {}
                forwarding_data['Request'] = (self.update_env(req))
                forwarding_data['Response'] = response
                req_url = 'http://' + str(self.ip) + ':' + str(self.port) \
                        + '/v1/'+self.lib_type
                timeout = 1
                forwarding_json = json.dumps(forwarding_data, indent=4,
                                                 sort_keys=True)
                thread.start_new_thread(post_response, (req_url, env,
                                                            forwarding_json,
                                                            headers,self.lib_type,
                                                            timeout))
        return res

    def update_env(self, req):
        env = req.environ.copy()
        post_req = {}

        # Get wsgi.input
        body = env['wsgi.input']
        try:
            request_body_size = int(env.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0
        input_context = body.read(request_body_size)
        if len(input_context) > 0:
            post_req['wsgi.input'] = eval(input_context.replace('true','True').replace('false','False').replace('null','None').replace('none','None'))
        else:
            post_req['wsgi.input'] = None

        # Get url
        post_req['url'] = req.url

        # Get type
        post_req['type'] = env['REQUEST_METHOD']
        return post_req

