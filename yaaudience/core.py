#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from .client import APIClient
from .objects import *


class BaseClass(object):
    pass


class ClientError(Exception):
    pass


class BadRequestError(ClientError):
    """ 400 http-status """
    pass


class UnauthorizedError(ClientError):
    """ 401 http-status """
    pass


class ForbiddenError(ClientError):
    """ 403 http-status """
    pass


class NotFoundError(ClientError):
    """ 404 http-status """
    pass


class MethodNotAllowedError(ClientError):
    """ 405 http-status """
    pass


class APIException(Exception):
    pass


class JSON2Obj(object):
    def __init__(self, page):
        self.__dict__ = json.loads(page.decode())



class YaAudience(object):
    """ Class for the API of Yandex Audience
    """
    HOST = 'https://api-audience.yandex.ru/'
    OAUTH_TOKEN = 'https://oauth.yandex.ru/token'

    VERSION = 'v1'

    MANAGEMENT = '%s/management' % VERSION

    SEGMENTS = MANAGEMENT + '/segments'
    SEGMENTS_UPLOAD_FILE = MANAGEMENT + '/segments/upload_file'
    SEGMENTS_UPLOAD_CSV_FILE = MANAGEMENT + '/segments/upload_csv_file'
    SEGMENT_CONFIRM = MANAGEMENT + '/segment/%d/confirm'
    SEGMENT_DELETE = MANAGEMENT + '/segment/%d'


    def __init__(self, token='', debug=False):
        self._token = token

        self._client = APIClient(debug)
        self._client.user_agent = 'yaaudience'
        self._data = ''

    @property
    def user_agent(self):
        return self._client.user_agent

    @user_agent.setter
    def user_agent(self, user_agent):
        self._client.user_agent = user_agent

    def _get_response_object(f):
        def wrapper(self):
            obj = JSON2Obj(self._data)

            if hasattr(obj, 'errors'):
                if hasattr(obj, 'message'):
                    raise APIException(u'{}: {}'.format(obj.code, obj.message))

                raise APIException(u'{}: {}'.format(obj.code, '\n'.join([error['message'] for error in obj.errors])))

            if hasattr(obj, 'message'):
                raise APIException(obj.message)

            return f(self, obj)

        return wrapper

    @_get_response_object
    def _authorize_handle(self, obj):
        if hasattr(obj, 'access_token'):
            self._token = obj.access_token


    def _auth(f):
        def wrapper(self, *args, **kwargs):
            if not self._token:
                self._authorize()

            return f(self, *args, **kwargs)

        return wrapper

    def _headers(self):
        header = {
            'User-Agent': self.user_agent,
            'Accept': 'application/x-yaaudience+json',
            'Accept-Language': 'ru,en-us;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '300',
            'Connection': 'keep-alive',
            'Authorization': 'OAuth %s' % self._token
        }
        return header

    @_get_response_object
    def _response_handle(self, obj):
        return obj

    @_auth
    def _get_data(self, method, uri, params=None):
        self._data = self._client.request(method, uri, params=params, headers=self._headers())

        #if self._client.status == 400:
        #    raise BadRequestError('%d %s' % (self._client.status, 'Check your request'))
        if self._client.status == 401:
            raise UnauthorizedError('%d: %s' % (self._client.status, 'Check your token'))
        if self._client.status == 403:
            raise ForbiddenError('%d: %s' % (self._client.status, 'Check your access rigths to object'))
        if self._client.status == 404:
            raise NotFoundError('%d: %s' % (self._client.status, 'Resource not found'))
        if self._client.status == 405:
            allowed = self._client.get_header('Allowed')
            raise MethodNotAllowedError('%d: %s\nUse %s' % (self._client.status, 'Method not allowed', allowed))

        return self._response_handle()

    def _get_uri(self, methodname, **params):
        uri = '%s%s.json' % (self.HOST, methodname)

        if params:
            uri += '?%s' % self._client.urlencode(**params)

        return uri

    def get_data(self):
        return self._data

    def _get_all_pages(attr_data, *attrs):
        def wrapper(f):
            def func(self, *args, **kwargs):
                offset = kwargs.get('offset', 1)
                per_page = kwargs.get('per_page', 1000)

                kwargs['offset'] = offset
                kwargs['per_page'] = per_page

                obj = f(self, *args, **kwargs)
                result = BaseClass()
                setattr(result, attr_data, [])
                attr = getattr(result, attr_data)
                attr.extend(getattr(obj, attr_data))

                for a in attrs:
                    if getattr(obj, a):
                        setattr(result, a, getattr(obj, a))

                rows = getattr(obj, 'rows', 0)

                while rows > offset * per_page:
                    offset += per_page

                    kwargs['offset'] = offset

                    obj = f(self, *args, **kwargs)
                    attr.extend(getattr(obj, attr_data))

                return result

            return func

        return wrapper


    # Segments 

    def segments(self, pixel=''):
        """ Return a list of existing segments
        """
        uri = self._get_uri(self.SEGMENTS)
        params = {
            'pixel': pixel
        }
        data = self._get_data('GET', uri, params)
        segment_list = []
        for s in data.segments:
            segment = SegmentObject(s)
            segment_list.append(segment)
        return segment_list

    def segments_upload_file(self, file):
        """ Upload a segment file
        """
        uri = self._get_uri(self.SEGMENTS_UPLOAD_FILE)
        data = self._get_data('POST', uri, file)
        segment_file = SegmentFileObject(data.segment)
        return segment_file

    def segments_upload_csv_file(self, csv_file):
        """ Upload a segment CSV file
        """
        uri = self._get_uri(self.SEGMENTS_UPLOAD_CSV_FILE)
        data = self._get_data('POST', uri, csv_file)
        segment_file = SegmentFileObject(data.segment)
        return segment_file


    def segment_confirm(self, segment_id, segment_name, content_type, hashed=False):
        """ Confirm a segment created from file
        """
        uri = self._get_uri(self.SEGMENT_CONFIRM % segment_id)
        params = '{"segment":{"id":%d,"name":"%s","hashed":%i,"content_type":"%s"}}' % (segment_id, segment_name, int(hashed), content_type)
        data = self._get_data('POST', uri, params)
        segment = SegmentObject(data.segment)
        return segment
        
    def segment_delete(self, segment_id):
        """ Delete a segment
        """
        uri = self._get_uri(self.SEGMENT_DELETE % segment_id)
        data = self._get_data('DELETE', uri)
        return data.success
