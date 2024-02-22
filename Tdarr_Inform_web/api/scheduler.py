from flask import request, redirect, Response
import urllib.parse
import json


class Scheduler_API():
    endpoints = ["/api/scheduler"]
    endpoint_name = "api_scheduler"
    endpoint_methods = ["GET", "POST"]
    endpoint_parameters = {
                            "method": {
                                    "default": "get"
                                    }
                            }

    def __init__(self, tdarr_inform):
        self.tdarr_inform = tdarr_inform

    def __call__(self, *args):
        return self.handler(*args)

    def handler(self, *args):

        method = request.args.get('method', default="get", type=str)
        redirect_url = request.args.get('redirect', default=None, type=str)

        if method == "get":
            jobsdicts = self.tdarr_inform.scheduler.list_jobs

            formatted_jobsdicts = []
            for job_dict in jobsdicts:
                for run_item in ["last_run", "next_run"]:
                    if job_dict[run_item]:
                        job_dict[run_item] = job_dict[run_item].timestamp()
                formatted_jobsdicts.append(job_dict)

            return_json = json.dumps(formatted_jobsdicts, indent=4)

            return Response(status=200,
                            response=return_json,
                            mimetype='application/json')

        elif method == "run":
            job_tag = request.form.get('job_tag', None)

            if not job_tag:
                if redirect_url:
                    return redirect("%s?retmessage=%s" % (redirect_url, urllib.parse.quote("%s Failed" % method)))
                else:
                    return "%s Falied" % method

            self.tdarr_inform.scheduler.run_from_tag(job_tag)

        elif method == "remove":
            job_tag = request.form.get('job_tag', None)

            if not job_tag:
                if redirect_url:
                    return redirect("%s?retmessage=%s" % (redirect_url, urllib.parse.quote("%s Failed" % method)))
                else:
                    return "%s Falied" % method

            self.tdarr_inform.scheduler.remove(job_tag)

        elif method == "add":
            job_name = request.form.get('name', None)
            job_type = request.form.get('type', None)
            job_interval = request.form.get('interval', None)

            job_name  # ignore this

            if job_type == "Versions Update":
                if job_interval:
                    self.tdarr_inform.scheduler.every(int(job_interval)).seconds.do(
                        self.tdarr_inform.scheduler.job_wrapper(self.tdarr_inform.versions.get_online_versions)).tag("Versions Update")

        if redirect_url:
            if "?" in redirect_url:
                return redirect("%s&retmessage=%s" % (redirect_url, urllib.parse.quote("%s Success" % method)))
            else:
                return redirect("%s?retmessage=%s" % (redirect_url, urllib.parse.quote("%s Success" % method)))
        else:
            return "%s Success" % method
