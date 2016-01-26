# -*- coding: utf-8 -*-

import logging
import requests
import time
import urllib

from uuid import uuid4

from .exceptions import LctvException

logger = logging.getLogger('lctv-api')

LCTV_BASE_PATH = "https://www.livecoding.tv"
LCTV_DOC_END_POINT = "/developer/documentation/api-docs/api/v1"


def check_response(end_point, code):
    '''Match the returned value of the HTTP response and raise
    a LctvException in case of error.
    '''
    if code / 100 == 2:
        msg_ = "Valid response from Livecoding.tv"
        logger.info(msg_)
        return True, msg_
    elif code == 401:
        msg_ = "Token or client credentials invalid({}): {}".format(code, end_point)
        logger.error(msg_)
    elif code == 403:
        msg_ = "Not enough permissions (check the scope) \
for this operation: {}".format(end_point)
        logger.error(msg_)
    raise LctvException(msg_)


class LctvOauth2App(object):
    '''This class encapsulates the OAuth2 logic required for the
    communication with Livecoding.TV REST API. In summary the work flow is
    similar to this:

    #. state,scope,auth_url = get_authorization_url()

    #. ... a valid code is received as GET parameter in a request for
       REDIRECT_URI. the state is also a GET parameter of that request in order
       to link the code witht the original state

    #. token = generate_token(code)
       operations = get_available_remote_api_calls()
       end_point = operations["/api/livestreams/"]["end_point"]
       token.api_operation_call(end_point,params)
    '''

    def __init__(self, client_id, client_secret, redirect_uri, scope='read',
                 grant_type='authorization_code'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.grant_type = grant_type

    def get_client_auth(self):
        client_auth = requests.auth.HTTPBasicAuth(self.client_id,
                                                  self.client_secret)
        return client_auth

    def get_authorization_url(self):
        """Generates a 3-tuple with the state, scopes, and the auth. url.
        The authorization URL is used in the first step fo the OAuth2
        authorization process to request a valid code for a incoming
        request.
        """
        state = str(uuid4())
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "state": state,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope
        }
        return (state, self.scope, LCTV_BASE_PATH + "/o/authorize/?" + urllib.urlencode(params))

    def get_available_remote_api_calls(self):
        """Autodiscover the available Livecoding.tv API operations and
        returns a dict with this information. This dict contains the
        end_points.
        """
        response = requests.get(LCTV_BASE_PATH + LCTV_DOC_END_POINT)
        json_ = response.json()
        actions = {}
        for api in json_['apis']:
            action = api['path']
            actions[action] = {
                'name': action.replace('/', ' ').replace('{', '{{').replace('}', '}}'),
                'end_point': action.replace('{', '{{').replace('}', '}}'),
            }
        return actions

    def generate_token(self, code):
        """Used in the second phase of the OAuth2 process, after receives
        the valid code from Livecoding.tv, you will execute this method to
        get a valid access token. This token, usually is linked in some
        manner with the final user in the application side.

        Receives a :code value as a parameter. This value is obtained
        externally as a HTTP request from Livecoding.tv to the defined
        REDIRECT_URI in the application.

        Raises :LctvException in case of authentication or permision issues.
        """
        post_data = {
            "grant_type": self.grant_type,
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        end_point = "/o/token/"
        response = requests.post(
            LCTV_BASE_PATH + end_point,
            auth=self.get_client_auth(),
            data=post_data)
        token_json = response.json()
        logger.debug("generate_token: {{end_point: {}, status_code: {}}}".format(
                     end_point, response.status_code))
        logger.debug("generate_token: {}".format(token_json))
        check_response(end_point, response.status_code)
        return LctvOauth2Token(app=self, **token_json)

    def api_operation_call(self, end_point, access_token, params={}):
        """Delegates in Livecoding.tv the request and recovers the delivered
        information.

        The :end_point is any of the available operations documented online
        in https://www.livecoding.tv/developer/documentation/.

        The :access_token is a valid token streamin recovered from
        Livecoding.tv. This value usually is encapsulated in
        a LctvOauth2Token object. We recommend the usage of the
        :api_operation_call method in the LctvOauth2Token class instance of
        this method if you don't need perform some particular operations.

        The :params are any of the filter,ordering,searcing or similar
        modifiers that Livecoding.tv supports:

        Searching:
            GET /api/user?search=russell

        Filter:
            GET /api/livestreams/?coding__name=python

        Ordering:
            GET /api/livestreams/?ordering=title
            GET /api/livestreams/?ordering=-title
            GET /api/scheduledbroadcast/?ordering=livestreams,title

        Format:
            GET /api/codingcategories/?format=api&offset=100
            GET /api/codingcategories/?format=json&offset=100

        Pagination:
            GET /api/codingcategories/?offset=100
            GET /api/codingcategories/?offset=200&limit=100
        """
        headers = {"Authorization": "bearer " + access_token}
        response = requests.get(LCTV_BASE_PATH + end_point,
                                params=params,
                                headers=headers)
        logger.debug("api_operation_call: {{end_point: {}, status_code: {}}}".format(
            end_point, response.status_code))
        return (response.status_code, response.json())


class LctvOauth2Token(object):

    def __init__(self, app, access_token,
                 token_type, expires_in, refresh_token, scope):
        self.app = app
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.expiration_time = time.time() + expires_in
        self.refresh_token = refresh_token
        self.scope = scope

    def api_refresh_token(self):
        """Refresh the token properties with new values requested to
        Livecoding.tv.
        """
        post_data = {
            "grant_type": "refresh_token",
            "access_token": self.access_token,
            "refresh_token": self.refresh_token
        }
        response = requests.post(
            LCTV_BASE_PATH + "/o/token/",
            auth=self.app.get_client_auth(),
            data=post_data)
        token_json = response.json()
        logger.debug("api_refresh_token: {}".format(token_json))
        self.access_token = token_json['access_token']
        self.token_type = token_json['token_type']
        self.expires_in = token_json['expires_in']
        self.expiration_time = time.time() + self.expires_in
        self.refresh_token = token_json['refresh_token']
        self.scope = token_json['scope']

    def api_operation_call(self, end_point, params={}, always_refresh=False):
        """Delegates in Livecoding.tv the request and recovers the delivered
        information.

        The :end_point is any of the available operations documented online
        in https://www.livecoding.tv/developer/documentation/.

        The :always_refresh forces the regeneration of the token anytime
        that the API is used. This only is recommended in special cases
        like debugging or similar stuffs.

        The :params are any of the filter,ordering,searcing or similar
        modifiers that Livecoding.tv supports:

        Searching:
            GET /api/user?search=russell

        Filter:
            GET /api/livestreams/?coding__name=python

        Ordering:
            GET /api/livestreams/?ordering=title
            GET /api/livestreams/?ordering=-title
            GET /api/scheduledbroadcast/?ordering=livestreams,title

        Format:
            GET /api/codingcategories/?format=api&offset=100
            GET /api/codingcategories/?format=json&offset=100

        Pagination:
            GET /api/codingcategories/?offset=100
            GET /api/codingcategories/?offset=200&limit=100
        """
        if always_refresh:
            self.api_refresh_token()
        if time.time() + 60 > self.expiration_time:
            self.api_refresh_token()
        return self.app.api_operation_call(end_point, self.access_token, params)

    def __repr__(self, ):
        """Return the canonical str representation of the object
        """
        return '{{access_token:{}, token_type:{}, expires_in:{:.0f},refresh_token:{},scope:{}}}'.format(
            self.access_token,
            self.token_type,
            self.expiration_time - time.time(),
            self.refresh_token,
            self.scope)
