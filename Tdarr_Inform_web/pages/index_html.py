from flask import request, render_template, session


class Index_HTML():
    endpoints = ["/index", "/index.html"]
    endpoint_name = "page_index_html"
    endpoint_access_level = 0
    pretty_name = "Index"

    def __init__(self, tdarr_inform):
        self.tdarr_inform = tdarr_inform

    def __call__(self, *args):
        return self.handler(*args)

    def handler(self, *args):

        tdarr_inform_status_dict = {
                            "Script Directory": str(self.tdarr_inform.config.internal["paths"]["script_dir"]),
                            "Config File": str(self.tdarr_inform.config.config_file),
                            "Cache Path": str(self.tdarr_inform.config.internal["paths"]["cache_dir"]),
                            "Database Type": self.tdarr_inform.config.dict["database"]["type"],
                            "Logging Level": self.tdarr_inform.config.dict["logging"]["level"],
                            }

        return render_template('index.html', request=request, session=session, tdarr_inform=self.tdarr_inform, tdarr_inform_status_dict=tdarr_inform_status_dict, list=list)
