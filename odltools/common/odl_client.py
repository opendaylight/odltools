# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging

from requests import sessions

logger = logging.getLogger('common.odl_client')


class OpenDaylightRestClient(object):

    def __init__(self, url, username, password, timeout):
        super(OpenDaylightRestClient, self).__init__()
        self.url = url
        self.timeout = timeout
        self.session = sessions.Session()
        self.session.auth = (username, password)

    def get(self, urlpath='', data=None):
        return self.request('get', urlpath, data)

    def put(self, urlpath='', data=None):
        return self.request('put', urlpath, data)

    def delete(self, urlpath='', data=None):
        return self.request('delete', urlpath, data)

    def request(self, method, urlpath='', data=None):
        headers = {'Content-Type': 'application/json'}
        url = '/'.join([self.url, urlpath])
        logging.debug(
            "Sending METHOD (%(method)s) URL (%(url)s) JSON (%(data)s)",
            {'method': method, 'url': url, 'data': data})
        return self.session.request(
            method, url=url, headers=headers, data=data, timeout=self.timeout)
