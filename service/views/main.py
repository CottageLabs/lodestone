from flask import Blueprint

from octopus.lib.webapp import jsonp
from flask import request, g, send_from_directory
from service.lib.crud_helper import CrudHelper
from service.lib.response_builder import *
# from service.deposit import get_file

import os

blueprint = Blueprint('main', __name__)

@blueprint.route("/ethesis", methods=['GET', 'POST'])
@blueprint.route("/data", methods=['GET', 'POST'])
@jsonp
def list_records():
    if request.method == "GET":
        if 'username' in g.params:
            if isinstance(g.params['username'], list):
                user = g.params['username'][0]
            else:
                user = g.params['username']
            records = CrudHelper(g.record_type).get_user_records(user)
            return http_200(records)
        else:
            # records = CrudHelper(g.record_type).get_records()
            return http_400()

    if request.method == "POST":
        data = g.params
        if not data:
            return http_400()
        record_crud = CrudHelper(g.record_type, job_id='new')
        if not record_crud.create_record(data):
            return http_400()
        record_crud.submit_record()
        return http_201('/%s/%s' % (g.record_type, record_crud.job_id))


@blueprint.route("/ethesis/<job_id>", methods=['GET', 'PUT', 'DELETE'])
@blueprint.route("/data/<job_id>", methods=['GET', 'PUT', 'DELETE'])
@jsonp
def each_record(job_id):
    record_crud = CrudHelper(g.record_type, job_id=job_id)
    if request.method == "GET":
        record = record_crud.get_record()
        if record:
            return http_200(record)
        else:
            http_404()
    if request.method == "PUT":
        data = g.params
        if not data:
            return http_400()
        if record_crud.dao_record:
            if not record_crud.dao_record.status_code == 'draft':
                return http_405('Resource cannot be updated once submitted')
            resp = http_204()
        else:
            resp = http_201('/%s/%s' % (g.record_type, record_crud.job_id))
        if not record_crud.create_record(data):
            return http_400()
        record_crud.submit_record()
        return resp
    if request.method == "DELETE":
        if not record_crud:
            resp = http_404()
        elif not record_crud.dao_record.status_code or record_crud.dao_record.status_code == 'draft':
            record_crud.delete_record()
            resp = http_200()
        else:
            resp = http_405('Resource cannot be deleted once submitted')
        return resp


@blueprint.route("/ethesis/<job_id>/files", methods=['GET', 'POST'])
@blueprint.route("/data/<job_id>/files", methods=['GET', 'POST'])
@jsonp
def record_files(job_id):
    record_crud = CrudHelper(g.record_type, job_id=job_id)
    if request.method == "GET":
        if not record_crud.dao_record:
            return http_404()
        return http_200(record_crud.dao_record.files)
    if request.method == "POST":
        file_master = request.files.get("file", None)
        if file_master:
            record_crud.add_file(file_master, g.params)
            return http_201('/%s/%s/files/%s' % (g.record_type, record_crud.job_id, file_master.filename))
        else:
            return http_400()


@blueprint.route("/ethesis/<job_id>/files/<file_name>", methods=['GET', 'DELETE'])
@blueprint.route("/data/<job_id>/files/<file_name>", methods=['GET', 'DELETE'])
@jsonp
def record_file(job_id, file_name):
    record_crud = CrudHelper(g.record_type, job_id=job_id)
    if not record_crud or not file_name:
        return http_404()
    file_path = None
    file_url = None
    for val in record_crud.dao_record.files:
        if val['file_name'] == file_name:
            file_path = val['file_path']
            file_url = val['file_url']
    if request.method == "GET":
        if file_path and os.path.isfile(file_path):
            return send_from_directory(directory=os.path.dirname(os.path.abspath(file_path)), filename=file_name)
        # elif file_url:
        #    return get_file(file_url, app.config.get('SWORD_USERNAME'), app.config.get('SWORD_PASSWORD'))
        return http_404()
    if request.method == "DELETE":
        if record_crud.dao_record.status_code != 'draft':
            return http_405('Resource cannot be deleted once submitted')

        record_crud.dao_record.delete_file(file_name)
        record_crud.dao_record.save()
        return http_200()

@blueprint.before_request
def get_params_and_record_type():
    # params
    g.params = {}
    if request.json:
        g.params = request.json
    elif request.form:
        g.params = request.form
    g.params = dict(g.params)
    if request.args:
        g.params.update(dict(request.args))
    # record type
    rule = request.url_rule
    g.record_type = None
    if rule and rule.rule:
        if 'ethesis' in rule.rule:
            g.record_type = 'ethesis'
        elif 'data' in rule.rule:
            g.record_type = 'dataset'
    return
