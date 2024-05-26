#!/usr/bin/python3
"""index of views"""

from api.v1.views import app_views
from flask import jsonify


@app_views.route('/status', methods=['GET'])
def status():
    """return status OK on route /status"""
    return jsonify({"status": "OK"})
