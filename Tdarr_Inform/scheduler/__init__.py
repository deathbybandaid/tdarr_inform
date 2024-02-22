import functools
import threading
import schedule
import time

from Tdarr_Inform.tools import checkattr


class Scheduler():
    """
    tdarr_inform Scheduling events system.
    """

    def __init__(self, settings, logger, db):
        self.config = settings
        self.logger = logger
        self.db = db

        self.schedule = schedule

    def tdarr_inform_self_add(self, tdarr_inform):
        self.tdarr_inform = tdarr_inform

    @property
    def enabled_jobs(self):
        return [x["name"] for x in self.list_jobs]

    @property
    def unscheduled_jobs(self):

        unscheduled_job_items = []

        enabled_jobs = self.enabled_jobs

        if "Versions Update" not in enabled_jobs:
            frequency_seconds = self.tdarr_inform.config.dict["tdarr_inform"]["versions_check_interval"]
            unscheduled_job_items.append({
                "name": "Versions Update",
                "type": "Versions Update",
                "interval": self.tdarr_inform.time.humanized_time(frequency_seconds),
                "interval_epoch": frequency_seconds
                })

        return unscheduled_job_items

    # This decorator can be applied to any job function
    def job_wrapper(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            job_name = func.__name__
            start_timestamp = time.time()

            self.logger.debug('Running job: %s' % job_name)

            result = func(*args, **kwargs)

            total_time = self.tdarr_inform.time.humanized_time(time.time() - start_timestamp)
            self.logger.debug('Job %s completed in %s' % (job_name, total_time))

            return result

        return wrapper

    def get_scheduled_time(self, jobtag):
        """Get last and next run info for a tag"""
        jobsdict = {
                    "name": None,
                    "last_run": None,
                    "next_run": None
                    }
        joblist = self.jobs
        for job_item in joblist:
            if len(list(job_item.tags)):
                if jobtag in list(job_item.tags):
                    jobsdict.update({
                                     "name": list(job_item.tags)[0],
                                     "last_run": job_item.last_run,
                                     "next_run": job_item.next_run
                                     })
        return jobsdict

    def remove(self, remtag):
        joblist = self.jobs
        for job_item in joblist:
            if len(list(job_item.tags)):
                if remtag in list(job_item.tags):
                    self.schedule.cancel_job(job_item)

    @property
    def list_tags(self):
        tagslist = []
        joblist = self.jobs
        for job_item in joblist:
            if len(list(job_item.tags)):
                tagslist.extend(list(job_item.tags))
        return tagslist

    @property
    def list_jobs(self):
        jobsdicts = []
        joblist = self.jobs
        for job_item in joblist:
            if len(list(job_item.tags)):
                jobsdicts.append({
                    "name": list(job_item.tags)[0],
                    "last_run": job_item.last_run,
                    "next_run": job_item.next_run
                    })
        return jobsdicts

    @property
    def list_jobs_humanized(self):
        jobsdicts = self.list_jobs
        formatted_jobsdicts = []
        nowtime = time.time()
        for job_dict in jobsdicts:
            job_dict_copy = job_dict.copy()
            for run_item in ["last_run", "next_run"]:
                if job_dict_copy[run_item]:
                    job_dict_copy[run_item] = job_dict_copy[run_item].timestamp()
                    if job_dict_copy[run_item] > nowtime:
                        job_dict_copy[run_item] = self.tdarr_inform.time.humanized_time(job_dict_copy[run_item] - nowtime)
                    else:
                        job_dict_copy[run_item] = self.tdarr_inform.time.humanized_time(nowtime - job_dict_copy[run_item])
                else:
                    job_dict_copy[run_item] = "Never"
            formatted_jobsdicts.append(job_dict_copy)
        return formatted_jobsdicts

    def run_from_tag(self, runtag):
        joblist = self.jobs
        for job_item in joblist:
            if len(list(job_item.tags)):
                if runtag in list(job_item.tags):
                    self.logger.debug("Job %s was triggered to run." % list(job_item.tags)[0])
                    job_item.run()

    def run(self):
        """
        Run all scheduled tasks.
        """

        # Start a thread to run the events
        t = threading.Thread(target=self.thread_worker, args=())
        t.start()

    def thread_worker(self):
        while True:
            self.schedule.run_pending()
            time.sleep(1)

    def startup_tasks(self):
        self.tdarr_inform.logger.info("Running Startup Tasks.")

        tags_list = self.list_tags

        self.startup_versions_update(tags_list)

        self.tdarr_inform.logger.info("Startup Tasks Complete.")

        return "Success"

    def startup_versions_update(self, tags_list):
        if "Versions Update" in tags_list:
            self.tdarr_inform.scheduler.run_from_tag("Versions Update")

    def __getattr__(self, name):
        """
        Quick and dirty shortcuts. Will only get called for undefined attributes.
        """

        if checkattr(self.schedule, name):
            return eval("self.schedule.%s" % name)
