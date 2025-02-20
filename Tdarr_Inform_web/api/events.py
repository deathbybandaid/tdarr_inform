from flask import request, Response
import json
import threading

import Tdarr_Inform.handlers


def process_information(tdarr_inform, webhook_json):
    Tdarr_Inform.handlers.Webhook_Event(tdarr_inform, webhook_json, process_event=True)


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
            event_handler = Tdarr_Inform.handlers.Webhook_Event(self.tdarr_inform, webhook_json, process_event=False)
        except Exception as exception_msg:
            event_handler = str(exception_msg)
            self.tdarr_inform.logger.error(event_handler)
            return Response(status=501,
                            response=json.dumps({"tdarr_inform": event_handler}, indent=4),
                            mimetype='application/json')

        event_handling_thread = threading.Thread(target=process_information, args=(self.tdarr_inform, webhook_json))
        event_handling_thread.start()

        return Response(status=200,
                        response=json.dumps({"tdarr_inform": "success"}, indent=4),
                        mimetype='application/json')
