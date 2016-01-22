# -*- coding: utf-8 -*-

import logging

from .exceptions import LctvException
from .models import LctvOauth2Token
from .models import LctvOauth2App

logger = logging.getLogger('lctv-api')


def build_playable_url(url, viewing_key):
    return "{}?t={}".format(url,viewing_key)

def build_playable_urls(urls, viewing_key):
    res = []
    for url in urls:
        res.append(build_playable_url(urls,viewing_key))
    return res

def get_playable_urls(element, viewing_key):
    if element.has_key['viewing_urls']:
        return build_playable_urls(element['viewing_urls'], viewing_key)
    raise LctvException("Not playable element")

def get_viewing_key(token):
    """This function requires read:user scope
    """
    end_point = "/api/v1/user/viewing_key"
    status_code,result = token.api_operation_call(end_point)
    try:
        return result["viewing_key"]
    except Exception:
        raise LctvException("viewing_key not accesible ({}) or missing".format(status_code))
