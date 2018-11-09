# -*- coding: utf-8 -*-
"""
    baidu_index.utils
    ~~~~~~~~~
    This module is intended to help decrypt the index data.
    :copyright: © 2018 by Roger Lee
    :email: 704482843@qq.com
    :license: Apache, see LICENSE for more details.
"""

# builtins
from datetime import datetime, timedelta


def ptbk(json_data):
    """
    This method will take the json data and convert the data into
    something that is used to decrypt a decrypted index data

    :param data: {"status": 0, "data": "hU,8olLEe6gQ4Yz+2,39.67%14058-"}
    :return: a string
    """
    x = list(json_data["data"])
    b = {}
    _ = 0
    while _ < int(len(x) / 2):
        m_len = int(len(x) / 2) + _
        b[x[_]] = x[m_len]
        _ += 1

    return b


def get_dates(period_str):
    """
    :param period_str: 20181020|20181026
    :return: ['2018-10-20', '2018-10-21', '2018-10-22', '2018-10-23', '2018-10-24', '2018-10-25', '2018-10-26']
    """
    start, end = period_str.split("|")

    return get_date_from_range(start, end)


def get_date_from_range(start_date, end_date):
    # generate a list of date range base on start date and end date
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d") + timedelta(days=1)
    date_generated = [start + timedelta(days=x) for x in range(0, (end - start).days)]
    return [date.strftime("%Y-%m-%d") for date in date_generated]


def decode_index_multi(json_data, ptbk_json_data):
    """
    This method will decrypt the encrypted index data based on the
    given decrypted code

    :param data: c = {"status":0,"uniqid":"5bd407f7d69d24.70987148","data":[{"key":"python","index":[{"period":"20181020|20181026","_all":"6gQ86,686Uo,Ug448,UgQY4,Ug4gU,U8LY8,U6UUo","_pc":"oUoY,Y8Eg,6Y86o,6Eo4g,6YQg6,6ELYY,64Y4L","_wise":"gE88,gE44,LU8g,L686,L4Q6,4oo4,48E8"}]}]}
    :param ptbk_json_data: data: {"status": 0, "data": "hU,8olLEe6gQ4Yz+2,39.67%14058-"}
    :return: [{'key': 'python', 'index': [{'period': '20181020|20181026', '_all': '6gQ86,686Uo,Ug448,UgQY4,Ug4gU,U8LY8,U6UUo', '_pc': 'oUoY,Y8Eg,6Y86o,6Eo4g,6YQg6,6ELYY,64Y4L', '_wise': 'gE88,gE44,LU8g,L686,L4Q6,4oo4,48E8', 'all': '14031,13129,24553,24085,24542,23683,21229', 'pc': '9298,8374,18319,17954,18041,17688,15856', 'wise': '4733,4755,6234,6131,6501,5995,5373'}]}]
    """
    b = ptbk(ptbk_json_data)
    data = json_data['data']
    data_len = len(data)
    for i in range(0, data_len):
        if data[i] and data[i].get('index') and data[i].get('index')[0]:
            """
            {'key': 'python', 'index': [{'period': '20181020|20181026', '_all': '6gQ86,686Uo,Ug448,UgQY4,Ug4gU,U8LY8,U6UUo', '_pc': 'oUoY,Y8Eg,6Y86o,6Eo4g,6YQg6,6ELYY,64Y4L', '_wise': 'gE88,gE44,LU8g,L686,L4Q6,4oo4,48E8'}]}
            """
            # split all
            M = list(data[i]['index'][0]["_all"]) if data[i]['index'][0]["_all"] else []
            # split pc
            I = list(data[i]['index'][0]["_pc"]) if data[i]['index'][0]["_pc"] else []
            # split wise
            C = list(data[i]['index'][0]["_wise"]) if data[i]['index'][0]["_wise"] else []

            # all
            S = []
            # pc
            k = []
            # wise
            T = []

            A = 0
            while A < len(M):
                try:
                    if M[A]:
                        S.append(b[M[A]])
                except IndexError:
                    pass
                try:
                    if I[A]:
                        k.append(b[I[A]])
                except IndexError:
                    pass
                try:
                    if C[A]:
                        T.append(b[C[A]])
                except IndexError:
                    pass

                A += 1

            # rejoin the data after decrypted
            data[i]['index'][0]["all"] = "".join(S)
            data[i]['index'][0]["pc"] = "".join(k)
            data[i]['index'][0]["wise"] = "".join(T)

    t_data = []
    for i, d in enumerate(data):
        index_data = {}
        index_data['keyword'] = d['key']
        index_data['all'] = dict(zip(get_dates(d["index"][0]["period"]), d["index"][0]["all"].split(",")))
        index_data['pc'] = dict(zip(get_dates(d["index"][0]["period"]), d["index"][0]["pc"].split(",")))
        index_data['mobile'] = dict(zip(get_dates(d["index"][0]["period"]), d["index"][0]["wise"].split(",")))
        index_data['uniqid'] = json_data['uniqid']
        t_data.append(index_data)

    return t_data
