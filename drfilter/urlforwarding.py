import requests
import re
import json
import webob.dec
import thread
import pdb
import logging
import os


def url_forwarding_factory(global_conf, **local_conf):
    def filter(app):
        return UrlForwarding(app, global_conf, local_conf)
    return filter


def post_response(req_url, data,headers, timeout=1):
    mylog = logging.getLogger('mylog')
    mylog.setLevel(logging.DEBUG)
    fh=logging.FileHandler('/home/eshufan/project/drfilter/drfilter/logging.log')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    mylog.addHandler(fh)
    try:
        res=requests.post(req_url, data=data,headers=headers, timeout=timeout)
        mylog.info('----------------------------------------------------------')
        mylog.info(data)
        mylog.info(res)
        mylog.info('----------------------------------------------------------')
    finally:
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
        if (res.content_length > 0):
            response=res.json
        else:
            response={}
        if (not response.has_key('badRequest')):
            env = req.environ.copy()
            method=env.get('REQUEST_METHOD')
            if (method=='DELETE') or (method=='PUT') or (method=='POST'):
                if (env.get('HTTP_X_TENANT') != 'service'):
                    headers = {'Content-type': 'application/json',
                               'openstack-service': self.app.__repr__()}
                    forwarding_data = {}
                    forwarding_data['Request'] = (self.update_env(req))
                    forwarding_data['Response'] = response
                    req_url = 'http://' + str(self.ip) + ':' + str(self.port) + '/v1/'+self.lib_type
                    timeout=1
                    thread.start_new_thread(post_response,(req_url,json.dumps(forwarding_data),
                                        headers, timeout))
        return res

    def update_env(self, req):
        env = req.environ.copy()
        post_req={}

        #get wsgi.input
        body=env['wsgi.input']
        try:  
           request_body_size = int(env.get('CONTENT_LENGTH', 0))  
        except (ValueError):  
           request_body_size = 0 
        inputcontext=body.read(request_body_size)
        if len(inputcontext)>0:
           post_req['wsgi.input']=eval(inputcontext)
        else:
           post_req['wsgi.input']= None

        # get url
        post_req['url']=req.url                     
        
        #get type
        post_req['type']=env['REQUEST_METHOD']
        return post_req


