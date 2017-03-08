from flask import jsonify


def http_200(data=None):
    resp = jsonify({'data': data, 'success': True})
    resp.mimetype = "application/json"
    resp.status = "200 OK"
    resp.status_code = 200
    return resp


def http_201(location):
    resp = jsonify({'data': location, 'success': True})
    resp.headers['location'] = location
    resp.autocorrect_location_header = False
    resp.status = '201 Created'
    resp.status_code = 201
    return resp


def http_204():
    resp = jsonify()
    resp.status = '204 No content'
    resp.status_code = 204
    return resp


def http_400():
    resp = jsonify({'data': None, 'success': False})
    resp.status = '400 Bad request'
    resp.status_code = 400
    return resp


def http_404():
    resp = jsonify()
    resp.status = '404 Not Found'
    resp.status_code = 404
    return resp


def http_405(message=None):
    if not message:
        message = 'Method Not Allowed'
    resp = jsonify({'message': message, 'success': False})
    resp.status = '405 Method Not Allowed'
    resp.status_code = 405
    return resp
