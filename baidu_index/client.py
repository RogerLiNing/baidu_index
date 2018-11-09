# -*- coding: utf-8 -*-
"""
    baidu_index.client
    ~~~~~~~~~
    This module is intended to help send http request and get back the data.
    :copyright: © 2018 by Roger Lee
    :email: 704482843@qq.com
    :license: Apache, see LICENSE for more details.
"""


import requests
from baidu_index.utils import decode_index_multi


class Client:
    """
    This client is intended to send http request to
    http://index.baidu.com/baidu-index-mobile/#/ and
    return the index data

    :param BDUSS: the BDUSS in the cookie which is the request authentication
    :param cookie_str: the cookie string you can copy directly from the browser
    """

    def __init__(self, BDUSS=None, cookie_str=None):
        self._cookie_str = cookie_str
        self._bduss = BDUSS
        self.cookies = {}
        self._parse_cookie()
        self.session = requests.Session()

    def search(self, keywords, startdate, enddate):
        """
        This method will call 2 methods: self._get_encrypt_index and self._get_decode_ptbk
        _get_encrypt_index will call API to send keywords and get back the encrypted index data
        _get_decode_ptbk will call API to get back the data that need to decrypt the encrypted index data

        :param keywords: a string or a list of strings, max list size is 3
        :param startdate: start query date
        :param enddate: end query date
        :return:
        """
        if not isinstance(keywords, (str, list)):
            raise Exception(
                "parameter 'keywords' only takes one string or a list of strings with length no more than 3")
        if isinstance(keywords, list):
            if len(keywords) > 3:
                raise Exception("Only allow to query 3 keywords at one time")
        result = self._get_encrypt_index(keywords, startdate, enddate)
        if result == False or result is None:
            return []
        uniqueid = result['uniqid']
        decode_data = self._get_decode_ptbk(uniqueid)
        index_result = decode_index_multi(result, decode_data)

        return index_result

    def _parse_cookie(self):
        """
        This method will handle the cookie string and generate a cookie
        which can be available cross the entire object
        :return: None
        """
        if self._cookie_str:
            cookies = {}
            kvs = self._cookie_str.split(";")
            for k in kvs:
                ks = k.split("=", 1)
                cookies[ks[0]] = ks[1]
            self.cookies = cookies
        elif self._bduss:
            self.cookies = {"BDUSS": self._bduss}

    def _get_request_headers(self):
        """
        This method will return a commonly used header for
        all the API call to index.baidu.com
        :return: dict of headers
        """
        headers = {"Accept": "application / json, text / plain, * / *",
                   "Accept - Encoding": "gzip, deflate",
                   "Accept - Language": "zh - CN, zh;q = 0.9",
                   "Connection": "keep - alive",
                   "Content - Type": "application / x - www - form - urlencoded;charset = UTF - 8",
                   "Host": "index.baidu.com",
                   "Referer": "http://index.baidu.com/baidu-index-mobile/",
                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36 X - Requested - With: XMLHttpRequest"
                   }
        return headers

    def _get_encrypt_index(self, keywords, startdate, enddate):
        """
        This method will call the API to query index

        :param keywords: one string or a list of strings with length no more than 3
        :param startdate: start query date
        :param enddate: end query date
        :return: a result dict
        """
        params = {
            "region": 0,
            "startdate": startdate,
            "enddate": enddate
        }

        if isinstance(keywords, str):
            params['wordlist[0]'] = keywords
        else:
            for i, k in enumerate(keywords):
                params[f'wordlist[{i}]'] = k

        api = "http://index.baidu.com/Interface/Newwordgraph/getIndex"

        response = requests.get(api, headers=self._get_request_headers(), params=params, cookies=self.cookies)

        try:
            if response.status_code == 200:
                if response.json()['status'] == 0:
                    return response.json()
                elif response.json()['status'] == 1:
                    return False
        except Exception as e:
            print(f"Error from {__class__.__name__}._get_encrypt_index:", str(e))

    def _get_decode_ptbk(self, uniqueid):
        """
        This method will take a uniqueid that pull back by the
        self._get_encrypt_index method and send http request to get
        the data that is used to decrypt the encrypted index data

        :param uniqueid: a string
        :return: dict
        """
        api = "http://index.baidu.com/Interface/api/ptbk?uniqid=" + uniqueid
        response = requests.get(api, headers=self._get_request_headers(), cookies=self.cookies)

        if response.status_code == 200:
            if response.json()['status'] == 0:
                return response.json()
