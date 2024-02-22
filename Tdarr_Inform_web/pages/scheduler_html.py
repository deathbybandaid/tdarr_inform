from flask import request, render_template, session


class Scheduler_HTML():
    endpoints = ["/scheduler", "/scheduler.html"]
    endpoint_name = "page_scheduler_html"
    endpoint_access_level = 2
    pretty_name = "Scheduler"

    def __init__(self, tdarr_inform):
        self.tdarr_inform = tdarr_inform

    def __call__(self, *args):
        return self.handler(*args)

    def handler(self, *args):

        formatted_jobsdicts = self.tdarr_inform.scheduler.list_jobs_humanized
        unscheduled_job_items = self.tdarr_inform.scheduler.unscheduled_jobs

        return render_template('scheduler.html', request=request, session=session, tdarr_inform=self.tdarr_inform,
                               jobsdicts=formatted_jobsdicts, unscheduled_job_items=unscheduled_job_items)
