from datetime import datetime, timedelta, tzinfo
from enum import Enum
import multiprocessing as mp
from random import choice
import string
from typing import Dict, List, Optional
from fastapi import Header
import pytz

from email_validator import EmailNotValidError, validate_email
import arrow
import threading
import requests
from requests import adapters
from common.exceptions import ApplicationError, ErrorCode

# from requests_aws4auth import AWS4Auth
import boto3
import os
import urllib.request

# from image.entity import ImageEntity
# from image.service import ImageService
from django.utils.timezone import make_aware
import re
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# import botocore

mp.set_start_method('fork', force=True)
CPU_CNT = mp.cpu_count() if not os.getenv('DEBUG') else mp.cpu_count()
UTC_TIMEZONE = pytz.timezone('UTC')
SEOUL_TIMEZONE = pytz.timezone('Asia/Seoul')
ENV = os.getenv('ENV')

# image_service = ImageService()
region = 'ap-northeast-2'
service = 'es'
thread_local = threading.local()
requests_https_adapter = adapters.HTTPAdapter(pool_connections=100)
requests_http_adapter = adapters.HTTPAdapter(pool_connections=100)
FIREBASE_WEB_API_KEY = os.getenv('FIREBASE_WEB_API_KEY')
ELASTICSEARCH_HOST = (
    os.getenv('PROD_ES_URL')
    if ENV == 'prod'
    else os.getenv('DEV_ES_URL')
    if ENV == 'dev'
    else os.getenv('LOCAL_ES_URL', 'http://host.docker.internal:9200')
)


global awsauth
# awsauth = AWS4Auth(refreshable_credentials=botocore.session.Session().get_credentials(), region=region, service='es')


def get_requests_session():
    if not hasattr(thread_local, "requests_session"):
        s = requests.Session()
        s.mount("http://", requests_https_adapter)
        s.mount("https://", requests_http_adapter)
        thread_local.requests_session = s
    return thread_local.requests_session


def multiline_description(*lines: str):
    return '<br>'.join(lines)


class ESmethod(str, Enum):
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'
    DELETE_BY_ID = 'delete_by_id'
    UPDATE = 'update'


def convert_to_dict_list(key, list: List):
    result_list = []
    for item in list:
        result_list.append({item[key]: item})
    return result_list


def get_json(uri: str, options: Optional[Dict] = {}):
    try:
        res = requests.get(uri, headers=options['header'] if options else {})
        return res.json()
    except Exception as e:
        raise ApplicationError(
            ErrorCode.INTERNAL_SERVER_ERROR, f'get_json error : {str(e)}, URI={uri}, options: {options}'
        )


def get_user_tz(TZ: str = Header(...)) -> str:
    try:
        user_tz = pytz.timezone(TZ)
    except Exception:
        user_tz = pytz.timezone('Asia/Seoul')

    return str(user_tz)


# # es는 숙소, 리뷰 등 여러 도메인에 걸쳐서 쓰이므로 utils에 위치함.
# def es(method: ESmethod, url: str, body: Optional[Dict]):
#     global awsauth
#     res = None
#     url = f'{ELASTICSEARCH_HOST}{url}'
#     header = {'Content-type': 'application/json'}
#     s = requests.Session()
#     s.headers.update(header)
#     s.auth = awsauth

#     try:

#         if method == ESmethod.GET:

#             res = requests_retry_session(backoff_factor=4.5, session=s).get(url=url, json=body, timeout=20)

#             res = res.json()

#             if 'hits' in res:
#                 res = res['hits']['hits']

#         if method == ESmethod.POST or method == ESmethod.DELETE or method == ESmethod.UPDATE:
#             res = requests.post(url, headers=header, json=body, auth=awsauth, timeout=5).json()

#         if method == ESmethod.PUT:
#             res = requests.put(url, headers=header, json=body, auth=awsauth, timeout=5).json()

#         if method == ESmethod.DELETE_BY_ID:
#             res = requests.delete(url, headers=header, json=body, auth=awsauth, timeout=5).json()

#         if res:
#             # print(res)
#             return res

#     except Exception as e:
#         raise ApplicationError(ErrorCode.APPLICATION_ERROR, f'es util error : {str(e)}, res = {res}')


def get_nights(from_date: str, to_date: str) -> int:
    if len(from_date) < 11:
        from_date = from_date + ' 00:00:00'
    if len(to_date) < 11:
        to_date = to_date + ' 00:00:00'

    from_date = arrow.get(from_date, 'YYYY-MM-DD')
    to_date = arrow.get(to_date, 'YYYY-MM-DD')

    nights = to_date - from_date  # type: ignore
    days = nights.days
    if days == 0:
        days = 1
    return days


def convert_timezone(date: str, from_tz: tzinfo, to_tz: tzinfo) -> str:
    date_info = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    date_info = make_aware(date_info, timezone=from_tz)
    converted_date = date_info.astimezone(tz=to_tz)
    result = datetime.strftime(converted_date, '%Y-%m-%d %H:%M:%S')
    return result


def convert_timezone_from_utc(date: str, to_tz: str) -> str:
    return arrow.get(date).to(to_tz).format('YYYY-MM-DD HH:mm:ss')


def get_weekday(date_str: str) -> str:
    """
    이미 timezone이 적절하게 적용되었다고 가정하고 진행
    """
    days = ['월', '화', '수', '목', '금', '토', '일']
    date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    weekday = days[date.weekday()]
    return weekday


def get_period(from_date: str, to_date: str) -> str:
    if len(from_date) < 11:
        from_date = from_date + ' 00:00:00'
    if len(to_date) < 11:
        to_date = to_date + ' 00:00:00'

    """
    이미 timezone이 적절하게 적용되었다고 가정하고 진행
    """
    period = f'{from_date}({get_weekday(from_date)})~{to_date}({get_weekday(to_date)})'
    return period


def get_date_range(from_date: str, to_date: str) -> List[str]:
    start = datetime.strptime(from_date, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(to_date, "%Y-%m-%d %H:%M:%S")
    dates = [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end - start).days + 1)]
    return dates


def delete_s3_directory(bucket: str, prefix: str) -> bool:
    s3_client = boto3.client('s3')
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)

    if 'Contents' in response:
        for object in response['Contents']:
            print('Deleting', object['Key'])
            s3_client.delete_object(Bucket=bucket, Key=object['Key'])
    return True


def download_img_from_url(url: str, file_name: str) -> bool:
    remaining_download_tries = 15
    while remaining_download_tries > 0:
        try:
            urllib.request.urlretrieve(url, file_name)
            print("successfully downloaded")
        except Exception:
            print("error downloading " + str(16 - remaining_download_tries))
            remaining_download_tries = remaining_download_tries - 1
            continue
        else:
            break
    return True


def isMobileNumber(tel: str) -> bool:
    if len(tel) < 10 or len(tel) > 11:
        return False
    reg = re.compile("^010|011|070\d{3,4}\d{4}$")
    return reg.match(tel) is not None


def generate_key(length: int = 3):
    return (
        str(arrow.now().timestamp)
        + '-'
        + ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(length))
    )


def create_dynamic_link(
    link: str,
    fallback_link: str = '',
    social_title: str = '',
    social_description: str = '',
    social_image_link: str = '',
) -> str:
    shortLink = ''
    url = f'https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key={FIREBASE_WEB_API_KEY}'
    body = {
        "dynamicLinkInfo": {
            "domainUriPrefix": "https://goldhand.page.link",
            "link": link,
            "androidInfo": {"androidPackageName": "com.goldhand.project_gold_hand"},
            "iosInfo": {"iosBundleId": "com.goldhand.projectGoldHand"},
            "navigationInfo": {"enableForcedRedirect": True},
        },
        "suffix": {"option": "SHORT"},
    }

    if fallback_link:
        body['dynamicLinkInfo']['androidInfo']['androidFallbackLink'] = fallback_link
        body['dynamicLinkInfo']['iosInfo']['iosFallbackLink'] = fallback_link

    if social_title and social_description:
        body['dynamicLinkInfo']['socialMetaTagInfo'] = {
            "socialTitle": social_title,
            "socialDescription": social_description,
            "socialImageLink": social_image_link,
        }

    header = {'Content-type': 'application/json'}

    r = requests.post(url=url, json=body, headers=header).json()

    shortLink = r['shortLink'] if 'shortLink' in r else shortLink
    # print(shortLink)
    return shortLink


# create_dynamic_link(
#     link=f'https://www.goldhand.app?page=photo_recruit_detail&id={111}',
#     social_title='OG TITLE',
#     social_description='OG DESCRIPTION',
#     social_image_link='https://www.bootpay.co.kr/assets/main/1_phone',
# )


class Validator:
    @classmethod
    def is_valid_provider(cls, provider: str) -> bool:
        try:
            OAuthProvider(provider)
        except ValueError:
            return False
        return True

    @classmethod
    def is_valid_email(cls, email: str) -> bool:
        try:
            validate_email(email)
        except EmailNotValidError:
            return False
        return True

    @classmethod
    def is_valid_gender(cls, sex: str) -> bool:
        try:
            Gender(sex)
        except ValueError:
            return False
        return True

    @classmethod
    def is_valid_date(cls, date: str) -> bool:
        try:
            arrow.get(date, 'YYYY-MM-DD')
        except arrow.parser.ParserMatchError:
            return False
        return True

    @classmethod
    def is_valid_address(cls, address: str) -> bool:
        # FIXME: validate address format
        return True

    @classmethod
    def is_valid_name(cls, name: str) -> bool:
        return 1 <= len(name) <= 20


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_region_1depth(address: str) -> str:
    try:
        tokens = address.split(' ')
        first_token = tokens[0]
        if len(first_token) == 2:
            return first_token

        if first_token == '세종특별자치시':
            return '세종'
        if first_token == '충청북도':
            return '충북'
        if first_token == '충청남도':
            return '충남'
        if first_token == '전라북도':
            return '전북'
        if first_token == '전라남도':
            return '전남'
        if first_token == '경상북도':
            return '경북'
        if first_token == '경상남도':
            return '경남'
        if first_token == '제주특별자치도':
            return '제주'

    except Exception:
        return ''
    return ''
