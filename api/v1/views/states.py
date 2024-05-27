#!/usr/bin/python3
"""State objects handling RESTFul API actions"""
from flask import Flask, jsonify, request, abort
from models import storage
from models.state import State
from api.v1.views import app_views


@app_views.route('/states', methods=['GET', 'POST'], strict_slashes=False)
def states():
    """Get list of all State objects or
       Creates a State object accroding to used method"""
    if request.method == 'GET':
        states = storage.all(State).values()
        return jsonify([state.to_dict() for state in states])
    if request.method == 'POST':
        if not request.json:
            abort(400, description="Not a JSON")
        if 'name' not in request.json:
            abort(400, description="Missing name")
        data = request.get_json()
        new_state = State(**data)
        storage.new(new_state)
        storage.save()
        return jsonify(new_state.to_dict()), 201


@app_views.route('/states/<state_id>', methods=['GET', 'DELETE', 'PUT'],
        strict_slashes=False)
def state_id(state_id):
    """Get a State object by its ID,
       Deletes a State object by its ID or
       Updates a State object by its ID  accroding to used method"""
    state = storage.get(State, state_id)
    if state is None:
            abort(404)
    if request.method == 'GET':
        return jsonify(state.to_dict())
    if request.method == 'DELETE':
        storage.delete(state)
        storage.save()
        return jsonify({}), 200
    if request.method == 'PUT':
        if not request.json:
            abort(400, description="Not a JSON")
        data = request.get_json()
        for key, value in data.items():
            if key not in ['id', 'created_at', 'updated_at']:
                setattr(state, key, value)
        storage.save()
        return jsonify(state.to_dict()), 200
