from flask import request, Response
import json

import Tdarr_Inform.handlers


class Events():
    endpoints = ["/api/events"]
    endpoint_name = "api_events"
    endpoint_methods = ["GET", "POST"]

    def __init__(self, tdarr_inform):
        self.tdarr_inform = tdarr_inform

    def __call__(self, *args):
        return self.handler(*args)

    def handler(self, *args):

        webhook_json = request.json

        try:
            event_handler = Tdarr_Inform.handlers.Webhook_Event(self.tdarr_inform, webhook_json)
        except Exception as exception_msg:
            event_handler = str(exception_msg)
            self.tdarr_inform.logger.error(event_handler)
            return Response(status=501,
                            response=json.dumps({"tdarr_inform": event_handler}, indent=4),
                            mimetype='application/json')

        return Response(status=200,
                        response=json.dumps({"tdarr_inform": "success"}, indent=4),
                        mimetype='application/json')
