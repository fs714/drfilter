# Still some problems...

import time
import shutil
from configobj import ConfigObj

NOVA_API_CONF = "/etc/nova/api-paste.ini"
OS_API_SEC = "composite:openstack_compute_api_v2"
DR_FILTER_TARGET_KEY = "keystone_nolimit"
DR_FILTER_TARGET_KEY_VALUE = "compute_req_id faultwrap sizelimit " \
                             "authtoken keystonecontext drfilter " \
                             "osapi_compute_app_v2"
DR_SEC = "filter:drfilter"
DR_KEY = "paste.filter_factory"
DR_KEY_VALUE = "drfilter.urlforwarding:url_forwarding_factory"

# Backup /etc/nova/api-paste.ini
now = time.strftime('%Y%m%d%H%M%S')
target = NOVA_API_CONF + "." + now + ".bak"
shutil.copyfile(NOVA_API_CONF, target)

# Update /etc/nova/api-paste.ini
conf = ConfigObj(NOVA_API_CONF)
conf[OS_API_SEC][DR_FILTER_TARGET_KEY] = DR_FILTER_TARGET_KEY_VALUE
conf[DR_SEC] = {}
conf[DR_SEC][DR_KEY] = DR_KEY_VALUE
conf.write()

for sec in conf:
    print(sec)
    for key in conf[sec]:
        print("\t" + key + " = " + conf[sec][key])
