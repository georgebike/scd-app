from flask import request, json, Response, Blueprint, g
from ..models.UserModel import UserModel, UserSchema
from ..shared.Authentication import Auth

user_api = Blueprint('user', __name__)      # create a blueprint app that we'll use for all user resources
user_schema = UserSchema()

@user_api.route('/', methods=['POST'])
def create():
    """
    Register
    ---
    tags:
        - users
    post:
        description: Register new account with username, password, is_terminal fields
        consumes:
            - application/json
        parameters:
            - in: body
              name: user
              description: User account credentials
              schema:
                type: object
                required:
                    - username
                    - password
                    - is_terminal
                properties:
                    username:
                        type: string
                    password:
                        type: string
                    is_terminal:
                        type: boolean
        responses:
            201:
                description: On register success return api-token in body as {'jwt_token'  AUTO-GENERATED-KEY}
            400:
                description: Problem on register
                schema:
                    type: string
                    properties:
                        _schema:
                            type: string
                            description: No data provided or invalid json format
                        generated-error:
                            type: string
                            description: Empty fields | Invalid credentials | Incorrect password
    """
    req_data = request.get_json()           # get the JSON object from the body of the request
    if req_data is None:
        message = {'_schema': 'No data provided or invalid json format'}
        return custom_response(message, 400)

    data, error = user_schema.load(req_data)   # validate and deserialize the req_data into an object defined by UserSchema's fields
    if error:
        return custom_response(error, 400)

    # check if the user already exists in the db
    user_in_db = UserModel.get_user_by_username(data.get('username'))
    if user_in_db:
        message = {'error': 'User already exist, please supply a different username'}
        return custom_response(message, 400)

    user = UserModel(data)
    user.save()

    ser_data = user_schema.dump(user).data  # dump() = serialize the user object into a dict according to UserSchema's fields
    token = Auth.generate_token(ser_data.get('id'))

    return custom_response( {'jwt_token': token}, 201 )


@user_api.route('/login', methods=['POST'])
def login():
    """
    Login
    ---
    tags:
        - users
    post:
        description: Login to account using username and password fields
        consumes:
            - application/json
        produces:
            - application/json
        parameters:
            - in: body
              name: user
              description: User account credentials
              schema:
                type: object
                required:
                    - username
                    - password
                properties:
                    username:
                        type: string
                    password:
                        type: string
        responses:
            200:
                description: On login success return api-token in body as {'jwt_token'  AUTO-GENERATED-KEY}
            400:
                description: Problem on login
                schema:
                    type: string
                    properties:
                        _schema:
                            type: string
                            description: No data provided or invalid json format
                        error:
                            type: string
                            description: Empty fields | Invalid credentials | Incorrect password
    """
    req_data = request.get_json()           # get data from the request
    if req_data is None:
        message = {'_schema': 'No data provided or invalid json format'}
        return custom_response(message, 400)

    data, error = user_schema.load(req_data, partial=True)     # deserialize and validate the fields | partial=True because we don't need all the user fields (just username and password)
    if error:
        return custom_response(error, 400)

    if not data.get('username') or not data.get('password'):
        return custom_response({'error': 'Please enter a username and a password to sign in'}, 400)

    user = UserModel.get_user_by_username(data.get('username'))

    if not user:
        return custom_response({'error': 'Invalid credentials.'}, 400)

    if not user.check_hash(data.get('password')):
        return custom_response({'error': 'Incorrect password.'}, 400)

    ser_data = user_schema.dump(user).data

    token = Auth.generate_token(ser_data.get('id'))
    return custom_response({'jwt_token': token}, 200)


@user_api.route('/', methods=['GET'])
@Auth.auth_required
def get_all():
    """
    Get all users
    ---
    tags:
        - users
    get:
        description: Get every account's fields from the database (requires authentication with valid token)
        produces:
            - application/json
        security:
            - APIKeyHeader: []
        responses:
            200:
                description: A list of all the users' accounts
                schema: UserSchema
    securityDefinitions:
        APIKeyHeader:
            type: apiKey
            in: header
            name: api-token
            description: Auto generated api token
    """
    users = UserModel.get_all_users()
    ser_users = user_schema.dump(users, many=True).data     # many=True means serialize users as a collection
    return custom_response(ser_users, 200)


@user_api.route('/<int:user_id>', methods=['GET'])
@Auth.auth_required
def get_a_user(user_id):
    """
    Get user by ID
    ---
    tags:
        - users
    get:
        description: Get a user by their numerical ID (requires authentication with valid token)
        produces:
            - application/json
        security:
            - APIKeyHeader: []
        parameters:
            - in: path
              name: user_id
              type: Integer
              required: true
              description: Numeric ID of the user to get
        responses:
            200:
                description: Updated account fields to be returned
                schema: UserSchema
    securityDefinitions:
        APIKeyHeader:
            type: apiKey
            in: header
            name: api-token
            description: Auto generated api token
    """
    user = UserModel.get_one_user(user_id)
    if not user:
        return custom_response( {'error': 'User not found'}, 404 )

    ser_user = user_schema.dump(user).data
    return custom_response(ser_user, 200)

@user_api.route('/me', methods=['GET'])
@Auth.auth_required
def get_me():
    """
    Get self user
    ---
    tags:
        - users
    get:
        description: Get personal account fields (username, password) (requires authentication with valid token)
        produces:
            - application/json
        security:
            - APIKeyHeader: []
        responses:
            200:
                description: Updated account fields to be returned
                schema: UserSchema
    securityDefinitions:
        APIKeyHeader:
            type: apiKey
            in: header
            name: api-token
            description: Auto generated api token
    """
    user = UserModel.get_one_user(g.user.get('id'))
    ser_user = user_schema.dump(user).data
    return custom_response(ser_user, 200)

@user_api.route('/me', methods=['PUT'])
@Auth.auth_required
def update():
    """
    Update self user
    ---
    tags:
        - users
    put:
        description: Updates personal account fields (username, password) (requires authentication with valid token)
        consumes:
            - application/json
        produces:
            - application/json
        security:
            - APIKeyHeader: []
        parameters:
            - in: body
              name: user
              description: Self user to be updated (optional fields, at least one required)
              schema:
                type: object
                properties:
                    username:
                        type: string
                    password:
                        type: string
                    is_terminal:
                        type: boolean
        responses:
            200:
                description: Updated account fields to be returned
                schema: UserSchema
            400:
                description: Problem modifying personal account
                schema:
                    type: string
                    properties:
                        _schema:
                            type: string
                            description: No data provided or invalid json format
                        generated-error:
                            type: string
                            description: Error occured when deserializing and validating fields
    """
    req_data = request.get_json()
    if req_data is None:
        message = {'_schema': 'No data provided or invalid json format'}
        return custom_response(message, 400)

    data, error = user_schema.load(req_data, partial=True)
    if error:
        return custom_response(error, 400)

    user = UserModel.get_one_user(g.user.get('id'))
    user.update(data)
    ser_user = user_schema.dump(user).data
    return custom_response(ser_user, 200)


@user_api.route('/me', methods=['DELETE'])
@Auth.auth_required
def delete():
    """
    Delete self user
    ---
    tags:
        - users
    delete:
        description: Delete personal account
        security:
            - APIKeyHeader: []
        responses:
            204:
                description: deleted
                schema:
                    type: string
                    properties:
                        message:
                            type: string
                            description: User deleted
    securityDefinitions:
        APIKeyHeader:
            type: apiKey
            in: header
            name: api-token
            description: Auto generated api token
    """
    user = UserModel.get_one_user(g.user.get('id'))
    user.delete()
    return custom_response( {'message': 'deleted'}, 204 )


def custom_response(res, status_code):
    """

    :param res:
    :param status_code:
    :return: flask.Response
    """

    return Response(
        mimetype="application/json",
        response=json.dumps(res),            # creates a string containing key: value in a json format
        status=status_code
    )
