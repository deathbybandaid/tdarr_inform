from flask import request, Response
import json


class Debug_JSON():
    endpoints = ["/api/debug"]
    endpoint_name = "api_debug"
    endpoint_methods = ["GET", "POST"]

    def __init__(self, tdarr_inform):
        self.tdarr_inform = tdarr_inform

    def __call__(self, *args):
        return self.handler(*args)

    def handler(self, *args):

        base_url = request.url_root[:-1]

        debugjson = {
                    "base_url": base_url,
                    }

        debug_json = json.dumps(debugjson, indent=4)

        return Response(status=200,
                        response=debug_json,
                        mimetype='application/json')
