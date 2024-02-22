from flask import send_from_directory

import pathlib


class Brython_bry():
    endpoints = ["/brython.bry"]
    endpoint_name = "file_brython_bry"

    def __init__(self, tdarr_inform):
        self.tdarr_inform = tdarr_inform
        self.brython_path = pathlib.Path(self.tdarr_inform.config.internal["paths"]["Tdarr_Inform_web_dir"]).joinpath('brython')

    def __call__(self, *args):
        return self.handler(*args)

    def handler(self, *args):

        return send_from_directory(self.brython_path, 'brython_code.py')
