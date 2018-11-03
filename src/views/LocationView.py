from flask import request, g, Blueprint, json, Response
from ..shared.Authentication import Auth
from ..models.LocationModel import LocationModel, LocationSchema

location_api = Blueprint('location_api', __name__)
location_schema = LocationSchema()

@location_api.route('/', methods=['POST'])
@Auth.auth_required
@Auth.terminal_required
def create():
    """
    Post new location
    ---
    tags:
        - locations
    post:
        description: Create new location providing latitude, longitude and info(optional)
        consumes:
            - application/json
        parameters:
            - in: body
              name: location
              description: Location GPS coordinates and info
              schema:
                type: object
                required:
                    - latitude
                    - longitude
                properties:
                    latitude:
                        type: number
                        format: float
                    longitude:
                        type: number
                        format: float
                    info:
                        type: string
        responses:
            201:
                description: The location that has been posted
                schema: LocationSchema
            400:
                description: Problem on posting new location
                schema:
                    type: string
                    properties:
                        _schema:
                            type: string
                            description: No data provided or invalid json format
                        generated-error:
                            type: string
    """
    req_data = request.get_json()
    if req_data is None:
        message = {'_schema': 'No data provided or invalid json format'}
        return custom_response(message, 400)

    req_data['owner_id'] = g.user.get('id')
    data, error = location_schema.load(req_data, partial=True)
    if error:
        return custom_response(error, 400)
    location = LocationModel(data)
    location.save()
    data = location_schema.dump(location).data
    return custom_response(data, 201)


@location_api.route('/', methods=['GET'])
@Auth.auth_required
def get_all():
    """
    Get all locations
    ---
    tags:
        - locations
    get:
        description: Get all locations from all users
        produces:
            - application/json
        security:
            - APIKeyHeader: []
        responses:
            200:
                description: A list of all the locations
                schema: LocationSchema
    securityDefinitions:
        APIKeyHeader:
            type: apiKey
            in: header
            name: api-token
            description: Auto generated api token
    """
    locations = LocationModel.get_all_locations()
    data = location_schema.dump(locations, many=True).data
    return custom_response(data, 200)


@location_api.route('/by-date')
@Auth.auth_required
def get_between_dates():
    """
    Get locations between dates
    ---
    tags:
        - locations
    get:
        description: Get all locations between 2 datesr
        produces:
            - application/json
        security:
            - APIKeyHeader: []
        parameters:
            - in: query
              name: start_date
              type: string
              format: date-time
              required: true
              description: Start date search
            - in: query
              name: end_date
              type: string
              format: date-time
              reequired: true
              description: End date search
        responses:
            200:
                description: All locations that have been posted between the 2 dates
                schema: LocationSchema
            400:
                description: No parameters
                schema:
                    type: string
                    properties:
                        error:
                            type: string
            404:
                description: No locations found betwen start_date and end_date
                schema:
                    type: string
                    properties:
                        error:
                            type: stringx
    securityDefinitions:
        APIKeyHeader:
            type: apiKey
            in: header
            name: api-token
            description: Auto generated api token
    """
    args = request.args
    if not args:
        return custom_response( {'error': 'No parameters provided'}, 400 )
    start_date = args['start_date']
    end_date = args['end_date']
    locations = LocationModel.get_by_dates(start_date, end_date)
    if not locations:
        return custom_response( {'error': 'Locations not found'}, 404 )
    ser_locations = location_schema.dump(locations, many=True)
    return custom_response(ser_locations, 200)


@location_api.route('/<int:location_id>', methods=['PUT'])
@Auth.auth_required
@Auth.terminal_required
def update(location_id):
    """
    Modify location
    ---
    tags:
        - locations
    put:
        description: Modify location by its ID providing latitude, longitude and info (all optional, at least 1 required)
        consumes:
            - application/json
        produces:
            - application/json
        parameters:
            - in: body
              name: location
              description: Location GPS coordinates and info
              schema:
                type: object
                properties:
                    latitude:
                        type: number
                        format: float
                    longitude:
                        type: number
                        format: float
                    info:
                        type: string
        responses:
            201:
                description: The location that has been updated
                schema: LocationSchema
            400:
                description: Operation available only for the owner of location
                schema:
                    type: string
                    properties:
                        error:
                            type: string
                        generated-error:
                            type: string
            404:
                description: Location not found (invalid location)
                schema:
                    type: string
                    properties:
                        error:
                            type: string
    """
    req_data = request.get_json()
    location = LocationModel.get_one_location(location_id)  # get location object from location ID
    if not location:
        return custom_response( {'error': 'Location not found (invalid location'}, 404 )
    data = location_schema.dump(location).data  # convert location object to dict type with schema fields

    if data.get('owner_id') != g.user.get('id'):
        return custom_response( {'error': 'Permission denied. You are not the owner of this location post'}, 400 )

    data, error = location_schema.load(req_data, partial=True)  # convert json to Location object with schema fields
    if error:
        return custom_response(error, 400)
    location.update(data)

    data = location_schema.dump(location).data
    return custom_response(data, 200)


@location_api.route('/<int:location_id>', methods=['DELETE'])
@Auth.auth_required
@Auth.terminal_required
def delete(location_id):
    """
    Delete location by ID
    ---
    tags:
        - locations
    delete:
        description: Delete a location by its numerical ID
        security:
            - APIKeyHeader: []
        parameters:
            - in: path
              name: location_id
              type: Integer
              required: true
              description: Numeric ID of the location to be deleted
        responses:
            204:
                description: deleted
                schema:
                    type: string
                    properties:
                        message:
                            type: string
                            description: User deleted
            400:
                description: Permission denied. Only the user who created the location can delete it
                schema:
                    type: string
                    properties:
                        error:
                            type: string
            404:
                description: Location not found (invalid location)
                schema:
                    type: string
                    properties:
                        error:
                            type: string
    securityDefinitions:
        APIKeyHeader:
            type: apiKey
            in: header
            name: api-token
            description: Auto generated api token
    """
    location = LocationModel.get_one_location(location_id)
    if not location:
        return custom_response( {'error': 'Location not found (invalid location)'}, 404 )
    data = location_schema.dump(location).data
    if data.get('owner_id') != g.user.get('id'):
        return custom_response( {'error': 'Permission denied'}, 400 )

    location.delete()
    return custom_response( {'message': 'Location deleted'}, 204 )


def custom_response(res, status_code):
    """
    Custom response function
    :param res:
    :param status_code:
    :return: Response()
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )
