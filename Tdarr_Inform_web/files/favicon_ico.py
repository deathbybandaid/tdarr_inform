from flask import send_from_directory


class Favicon_ICO():
    endpoints = ["/favicon.ico"]
    endpoint_name = "file_favicon_ico"

    def __init__(self, tdarr_inform):
        self.tdarr_inform = tdarr_inform

    def __call__(self, *args):
        return self.handler(*args)

    def handler(self, *args):
        return send_from_directory(self.tdarr_inform.config.internal["paths"]["www_dir"],
                                   'favicon.ico',
                                   mimetype='image/vnd.microsoft.icon')
