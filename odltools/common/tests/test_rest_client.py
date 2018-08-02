# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import unittest

import requests

from odltools import logg
from odltools.common import rest_client
import requests_mock

MOCK_URL = "http://test.com"
MOCK_TEXT = "Success"


class TestRestClient(unittest.TestCase):
    def setUp(self):
        logg.Logger(logging.INFO, logging.DEBUG)

    def test_get(self):
        with requests_mock.Mocker() as mrequests:
            mrequests.register_uri('GET', MOCK_URL, text=MOCK_TEXT)
            restclient = rest_client.RestClient(MOCK_URL)
            response = restclient.get()
            content = response.content.decode(response.encoding)
            self.assertEqual(content, MOCK_TEXT)
            mrequests.register_uri('GET', MOCK_URL, exc=requests.exceptions.ConnectTimeout)
            restclient = rest_client.RestClient(MOCK_URL)
            with self.assertRaises(requests.exceptions.ConnectionError):
                restclient.get()


if __name__ == '__main__':
    unittest.main()
