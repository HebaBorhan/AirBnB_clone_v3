#!/usr/bin/python3
"""Place objects handling RESTFul API actions"""
from flask import Flask, jsonify, request, abort
from models import storage
from models.city import City
from models.place import Place
from models.user import User
from models.state import State
from models.amenity import Amenity
from api.v1.views import app_views


@app_views.route(
        '/cities/<city_id>/places', methods=['GET'], strict_slashes=False)
def get_places(city_id):
    """Get list of all Place objects of a City"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    return jsonify([place.to_dict() for place in city.places])


@app_views.route(
        '/cities/<city_id>/places', methods=['POST'], strict_slashes=False)
def create_place(city_id):
    """Creates a Place object"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    try:
        data = request.get_json()
    except Exception:
        data = None
    if not data:
        abort(400, description="Not a JSON")
    if 'user_id' not in data:
        abort(400, description="Missing user_id")
    user = storage.get(User, data['user_id'])
    if user is None:
        abort(404)
    if 'name' not in data:
        abort(400, description="Missing name")
    data['city_id'] = city_id
    new_place = Place(**data)
    storage.new(new_place)
    storage.save()
    return jsonify(new_place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def get_place(place_id):
    """Get Place object by its ID"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route(
        '/places/<place_id>', methods=['DELETE'], strict_slashes=False)
def delete_place(place_id):
    """Deletes a Place object by its ID"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({}), 200


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    """Updates a Place object by its ID"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    try:
        data = request.get_json()
    except Exception:
        data = None
    if not data:
        abort(400, description="Not a JSON")
    for key, value in data.items():
        if key not in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(place, key, value)
    storage.save()
    return jsonify(place.to_dict()), 200


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def places_search():
    """Search for Place objects based on JSON request body"""
    try:
        data = request.get_json()
    except Exception:
        data = None
    if not data:
        abort(400, description="Not a JSON")

    # If the JSON body is empty or each list of all keys are empty: retrieve all Place objects
    if not data or (not data.get("states") and not data.get("cities") and not data.get("amenities")):
        places = storage.all("Place").values()
        return jsonify([place.to_dict() for place in places])

    places = set()
    states = data.get("states", [])
    cities = data.get("cities", [])
    amenities = data.get("amenities", [])

    # If states list is not empty, results should include all Place objects for each State id listed
    for state_id in states:
        state = storage.get("State", state_id)
        if state:
            for city in state.cities:
                places.update(city.places)

    # If cities list is not empty, results should include all Place objects for each City id listed
    for city_id in cities:
        city = storage.get("City", city_id)
        if city:
            places.update(city.places)

    # If amenities list is not empty, limit search results to only Place objects having all Amenity ids listed
    if amenities:
        amenity_ids = set(amenities)
        filtered_places = []
        for place in places:
            place_amenities_ids = {amenity.id for amenity in place.amenities}
            if amenity_ids.issubset(place_amenities_ids):
                filtered_places.append(place)
        places = filtered_places

    return jsonify([place.to_dict() for place in places])
