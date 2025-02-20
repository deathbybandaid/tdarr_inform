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

        self.tdarr_inform.scheduler.every(5).seconds.do(self.schedule_event_handler, self.tdarr_inform, webhook_json)

        return Response(status=200,
                        response=json.dumps({"tdarr_inform": "success"}, indent=4),
                        mimetype='application/json')

    def schedule_event_handler(self, tdarr_inform, webhook_json):
        try:
            event_handler = Tdarr_Inform.handlers.Webhook_Event(self.tdarr_inform, webhook_json)
        except Exception as exception_msg:
            event_handler = str(exception_msg)
            self.tdarr_inform.logger.error(event_handler)
        return self.tdarr_inform.scheduler.CancelJob
