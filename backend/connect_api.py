import sys
import ssl
import os
from urllib import request, parse, error
from http import HTTPStatus
import base64
import json
from pprint import pprint

from dotenv import load_dotenv
from fastapi import requests

from connect_response import ConnectResponse
load_dotenv()

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


HOST = os.getenv("CONNECT_API_HOST")
ACCEPT = os.getenv("CONNECT_API_ACCEPT")
CLIENT_ID = os.getenv("CONNECT_API_CLIENT_ID")
SECRET = os.getenv("CONNECT_API_SECRET")


def authentication(device: str, password: str) -> ConnectResponse:
    # --------------------------------------------------------------------------------
    # 1. Authentication
    AUTH_URI = 'https://' + HOST + '/api/1/printing/oauth2/auth/token?subject=printer'
    DEVICE = device

    auth = base64.b64encode((CLIENT_ID + ':' + SECRET).encode()).decode()

    query_param = {
        'grant_type': 'password',
        'username': DEVICE,
        'password': password,
    }
    query_string = parse.urlencode(query_param)

    headers = {
        'Authorization': 'Basic ' + auth,
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
    }

    req, res, body, err_str = '', '', '', ''
    try:
        req = request.Request(AUTH_URI, data=query_string.encode(
            'utf-8'), headers=headers, method='POST')
        with request.urlopen(req, context=ssl_context) as res:
            body = res.read()
    except error.HTTPError as err:
        err_str = str(err.code) + ':' + err.reason + ':' + str(err.read())
    except error.URLError as err:
        err_str = err.reason

    pprint('1. Authentication: ---------------------------------')
    pprint(AUTH_URI)
    pprint(query_string)
    if res == '':
        pprint(err_str)
    else:
        pprint(str(res.status) + ':' + res.reason)
        pprint(json.loads(body))

    if err_str != '' or res.status != HTTPStatus.OK:
        sys.exit(1)

    json_file = 'auth_info.json'
    with open(json_file, 'w') as f:
        json.dump(body.decode('utf-8'), f)
    print(f'JSON 파일 {json_file}에 저장되었습니다.')

    return json.loads(body)


def create_print_job(subject_id, access_token, copies):
    # --------------------------------------------------------------------------------
    # 2. Create print job

    job_uri = 'https://' + HOST + '/api/1/printing/printers/' + subject_id + '/jobs'

    data_param = {
        'job_name': 'SampleJoba',
        'print_mode': 'document',
        'print_setting': {
            'media_size': 'ms_a4',
            'media_type': 'mt_plainpaper',
            'borderless': False,
            'print_quality': 'normal',
            'source': 'auto',
            'color_mode': 'color',
            'copies': copies,
        }
    }
    data = json.dumps(data_param)

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json;charset=utf-8'
    }

    req, res, body, err_str = '', '', '', ''
    try:
        req = request.Request(job_uri, data=data.encode('utf-8'), headers=headers, method='POST')
        with request.urlopen(req, context=ssl_context) as res:
            body = res.read()
    except error.HTTPError as err:
        err_str = str(err.code) + ':' + err.reason + ':' + str(err.read())
    except error.URLError as err:
        err_str = err.reason

    pprint('2. Create print job: -------------------------------')
    pprint(job_uri)
    pprint(data)
    if res == '':
        pprint(err_str)
    else:
        pprint(str(res.status) + ':' + res.reason)
        pprint(json.loads(body))

    if err_str != '' or res.status != HTTPStatus.CREATED:
        sys.exit(1)

    return json.loads(body)


def upload_print_file(job_id, base_uri):
    # --------------------------------------------------------------------------------
    # 3. Upload print file
    local_file_path = 'file_to_print.html'

    _, ext = os.path.splitext(local_file_path)
    file_name = '1' + ext
    upload_uri = base_uri + '&File=' + file_name

    headers = {
        'Content-Length': str(os.path.getsize(local_file_path)),
        'Content-Type': 'application/octet-stream'
    }

    req, res, body, err_str = '', '', '', ''
    try:
        with open(local_file_path, 'rb') as f:
            req = request.Request(upload_uri, data=f, headers=headers, method='POST')
            with request.urlopen(req, context=ssl_context) as res:
                body = res.read()
    except error.HTTPError as err:
        err_str = str(err.code) + ':' + err.reason + ':' + str(err.read())
    except error.URLError as err:
        err_str = err.reason

    pprint('3. Upload print file: ------------------------------')
    pprint(base_uri)
    if res == '':
        pprint(err_str)
    else:
        pprint(str(res.status) + ':' + res.reason)

    if err_str != '' or res.status != HTTPStatus.OK:
        sys.exit(1)

    return body


def execute_print(subject_id, access_token, job_id):
    # --------------------------------------------------------------------------------
    # 4. Execute print

    print_uri = 'https://' + HOST + '/api/1/printing/printers/' + subject_id + '/jobs/' + job_id + '/print'
    data = ''

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json; charset=utf-8'
    }

    req, res, body, err_str = '', '', '', ''
    try:
        req = request.Request(print_uri, data=data.encode('utf-8'), headers=headers, method='POST')
        with request.urlopen(req, context=ssl_context) as res:
            body = res.read()
    except error.HTTPError as err:
        err_str = str(err.code) + ':' + err.reason + ':' + str(err.read())
    except error.URLError as err:
        err_str = err.reason

    pprint('4. Execute print: ----------------------------------')
    pprint(print_uri)
    if res == '':
        pprint(err_str)
    else:
        pprint(str(res.status) + ':' + res.reason)
        pprint(json.loads(body))


def print_status(access_token, subject_id, job_id):
    print_uri = f'https://{HOST}/api/1/printing/printers/{subject_id}/jobs/{job_id}'
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json; charset=utf-8'
    }

    req, res, body, err_str = '', '', '', ''
    try:
        req = request.Request(print_uri, headers=headers, method='GET')
        with request.urlopen(req, context=ssl_context) as res:
            body = res.read()
    except error.HTTPError as err:
        err_str = str(err.code) + ':' + err.reason + ':' + str(err.read())
    except error.URLError as err:
        err_str = err.reason

    if res == '':
        pprint(err_str)
    else:
        pprint(str(res.status) + ':' + res.reason)
        pprint(json.loads(body))

    if err_str != '' or res.status != HTTPStatus.OK:
        sys.exit(1)

    return json.loads(body)
