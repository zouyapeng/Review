import json
import urlparse
import requests
import urllib
import urllib2


def build_url(base, additional_params=None):
    """Construct a URL based off of base containing all parameters in
    the query portion of base plus any additional parameters.

    :param base: Base URL
    :type base: str
    ::param additional_params: Additional query parameters to include.
    :type additional_params: dict
    :rtype: str
    """
    url = urlparse.urlparse(base)
    query_params = {}
    query_params.update(urlparse.parse_qsl(url.query, True))
    if additional_params is not None:
        query_params.update(additional_params)
        for k, v in additional_params.iteritems():
            if v is None:
                query_params.pop(k)

    return urlparse.urlunparse((url.scheme,
                                url.netloc,
                                url.path,
                                url.params,
                                urllib.urlencode(query_params),
                                url.fragment))


class Client(object):
    def __init__(self, client_id, client_secret, redirect_uri, \
                 authorization_uri, token_uri, openid_uri, user_uri=None):
        """Constructor for OAuth 2.0 Client.

        :param client_id: Client ID.
        :type client_id: str
        :param client_secret: Client secret.
        :type client_secret: str
        :param redirect_uri: Client redirect URI: handle provider response.
        :type redirect_uri: str
        :param authorization_uri: Provider authorization URI.
        :type authorization_uri: str
        :param token_uri: Provider token URI.
        :type token_uri: str
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.authorization_uri = authorization_uri
        self.token_uri = token_uri
        self.openid_uri = openid_uri
        self.user_uri = user_uri

    def get_user_info(self, access_token, openid):
        response = requests.get("%sget_user_info/" % self.user_uri, params=
        {'access_token': access_token, 'client_id': self.client_id, "openid": openid}, verify=False)
        try:
            return response.json()
        except TypeError:
            return response.json

    def get_user_group_info(self, access_token, openid):
        response = requests.get("%sget_user_group_info/" % self.user_uri, params=
        {'access_token': access_token, 'client_id': self.client_id, "openid": openid, "group": "bodhi"}, verify=False)
        try:
            return response.json()
        except TypeError:
            return response.json

    def get_openid(self, access_token):
        response = requests.get(self.openid_uri, params={'access_token': access_token}, verify=False)
        try:
            return response.json()
        except TypeError:
            return response.json

    @property
    def default_response_type(self):
        return 'code'

    @property
    def default_grant_type(self):
        return 'authorization_code'

    def http_post(self, url, data=None):
        """POST to URL and get result as a response object.

        :param url: URL to POST.
        :type url: str
        :param data: Data to send in the form body.
        :type data: str
        :rtype: requests.Response
        """
        # if not url.startswith('https://'):
        # raise ValueError('Protocol must be HTTPS, invalid URL: %s' % url)
        return requests.post(url, data, verify=False)


    def get_authorization_code_uri(self, **params):
        """Construct a full URL that can be used to obtain an authorization
        code from the provider authorization_uri. Use this URI in a client
        frame to cause the provider to generate an authorization code.

        :rtype: str
        """
        if 'response_type' not in params:
            params['response_type'] = self.default_response_type
        params.update({'client_id': self.client_id,
                       'redirect_uri': self.redirect_uri})
        return build_url(self.authorization_uri, params)

    def get_token(self, **params):
        """Get an access token from the provider token URI.

        :param code: Authorization code.
        :type code: str
        :return: Dict containing access token, refresh token, etc.
        :rtype: dict
        """
        if 'grant_type' not in params:
            params['grant_type'] = self.default_grant_type
        params.update({'client_id': self.client_id,
                       'client_secret': self.client_secret})
        if params['grant_type'] != 'refresh_token':
            params['redirect_uri'] = self.redirect_uri
        response = self.http_post(self.token_uri, params)
        try:
            return response.json()
        except TypeError:
            return response.json
