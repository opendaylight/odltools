# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import os

from requests import sessions

logger = logging.getLogger('common.rest_client')


class RestClient(object):

    def __init__(self, url, timeout=5, username=None, password=None):
        super(RestClient, self).__init__()
        self.url = url
        self.timeout = timeout
        self.session = sessions.Session()
        if username is not None and password is not None:
            self.session.auth = (username, password)

    def get(self, urlpath='', data=None, stream=False):
        return self.request('get', urlpath, data, stream)

    def put(self, urlpath='', data=None, stream=False):
        return self.request('put', urlpath, data, stream)

    def delete(self, urlpath='', data=None, stream=False):
        return self.request('delete', urlpath, data, stream)

    def write_file(self, response, urlpath, path):
        base = os.path.basename(urlpath)
        root, ext = os.path.splitext(base)
        local_filename = "{}/{}".format(path, root)
        logger.debug("write_file: urlpath: {}, local_filename: {}".format(urlpath, local_filename))
        with open(local_filename, "wb") as fp:
            for chunk in response.iter_content(chunk_size=1024):
                fp.write(chunk)

    def request(self, method, urlpath='', data=None, stream=False):
        headers = {'Content-Type': 'application/json'}
        url = '/'.join([self.url, urlpath])
        logger.debug("Sending METHOD: {}, URL: {}, JSON: {}, STREAM: {}"
                     .format(method, url, data, stream))
        return self.session.request(
            method, url=url, headers=headers, data=data, timeout=self.timeout, stream=stream)
