HOW TO USE!
1 put /drfilter/drfilter document in /usr/lib/python2.7/xxxxxpackages

2 change /etc/nova/api-paste.ini 
  [composite:openstack_compute_api_v2]
  use = call:nova.api.auth:pipeline_factory
  noauth = compute_req_id faultwrap sizelimit noauth ratelimit osapi_compute_app_v2
  keystone = compute_req_id faultwrap sizelimit authtoken keystonecontext ratelimit osapi_compute_app_v2
  keystone_nolimit = compute_req_id faultwrap sizelimit authtoken keystonecontext drfilter osapi_compute_app_v2
  ...
  [filter:drfilter]
  paste.filter_factory = drfilter.urlforwarding:url_forwarding_factor
  lib_type=nova

3 change /etc/neutron/api-paste.ini
  [composite:neutronapi_v2_0]
  use = call:neutron.auth:pipeline_factory 
  noauth = request_id catch_errors extensions neutronapiapp_v2_0
  keystone = request_id catch_errors authtoken keystonecontext extensions drfilter neutronapiapp_v2_0
  ...
  [filter:drfilter]
  paste.filter_factory = drfilter.urlforwarding:url_forwarding_factor
  lib_type=neutron

4 change /etc/glance/glance-api-paste.ini
  [pipeline:glance-api-keystone+cachemanagement]
  pipeline = versionnegotiation osprofiler authtoken context cache cachemanage drfilter rootapp
  ...
  [filter:drfilter]
  paste.filter_factory = drfilter.urlforwarding:url_forwarding_factor
  lib_type=glance

5 restart openstack