from functools import wraps

import jwt
import os
import datetime
from flask import json, Response, request, g
from ..models.UserModel import UserModel

class Auth():
    """
    Auth class - for authentication purposes
    """

    @staticmethod
    def generate_token(user_id):
        """
        Generate Token Method
        :param user_id:
        :return: utf-8 jwt encoded auth key
        """

        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),  # 1 day available token
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                os.getenv('JWT_SECRET_KEY'),        # the key used to encode the token is stored local machine
                'HS256'                             # HS256 - the algorithm used to encode the token
            ).decode("utf-8")
        except Exception as e:
            return Response(
                mimetype="application/json",
                response=json.dumps({'error': 'error in generating user token'}),
                status=400
            )

    @staticmethod
    def decode_token(token):
        """
        Decode token method
        :param token:
        :return: response as user_id or token error
        """

        re = {'data': {}, 'error': {}}
        try:
            payload = jwt.decode(token, os.getenv('JWT_SECRET_KEY'))
            re['data'] = {'user_id': payload['sub']}
            return re
        except jwt.ExpiredSignatureError:
            re['error'] = {'message': 'Token expired, please login again'}
            return re
        except jwt.InvalidTokenError:
            re['error'] = {'message': 'Invalid token. Please login again or try a new token'}
            return re

    # decorator
    @staticmethod
    def auth_required(func):        # this decorator checks if the token is valid for each request
        """
        Auth decorator - checks if a token exists in the request

        :param func:
        :return: ????
        """

        @wraps(func)
        def decorated_auth(*args, **kwargs):
            if 'api-token' not in request.headers:
                return Response(
                    mimetype="application/json",
                    response=json.dumps({'error': 'Authentication token is not available, please login to get one'}),
                    status=400
                )
            token = request.headers.get('api-token')
            data = Auth.decode_token(token)
            if data['error']:
                return Response(
                    mimetype="application/json",
                    response=json.dumps(data['error']),
                    status=400
                )
            user_id = data['data']['user_id']
            check_user = UserModel.get_one_user(user_id)
            if not check_user:
                return Response(
                    mimetype="application/json",
                    response=json.dumps({'error': 'user does not exist, invalid token'}),
                    status=400
                )
            g.user = {
                'id': user_id,   # if all checks are passed, put in global g the current user
                'is_terminal': check_user.is_terminal
            }
            return func(*args, **kwargs)
        return decorated_auth

    @staticmethod
    def terminal_required(func):
        """
        Is_terminal decorator - checks if a user has the field is_terminal = true
        :param func:
        :return:
        """

        @wraps(func)
        def decorated_terminal(*args, **kwargs):
            if g.user.get('is_terminal') is False:
                return Response(
                    mimetype="application/json",
                    response=json.dumps({'error': 'You have to be logged as a terminal to post location'}),
                    status=400
                )
            return func(*args, **kwargs)
        return decorated_terminal





