from flask import request, Response, abort


class Images():
    endpoints = ["/api/images"]
    endpoint_name = "api_images"
    endpoint_methods = ["GET", "POST"]
    endpoint_parameters = {
                            "method": {
                                    "default": "generate"
                                    },
                            "type": {
                                    "default": "content"
                                    },
                            "message": {
                                    "default": "Internal Image Handling"
                                    }
                            }

    def __init__(self, tdarr_inform):
        self.tdarr_inform = tdarr_inform

    def __call__(self, *args):
        return self.handler(*args)

    def handler(self, *args):

        image = None

        method = request.args.get('method', default="get", type=str)

        if method == "generate":
            image_type = request.args.get('type', default="content", type=str)
            if image_type in ["content"]:
                message = request.args.get('message', default="Unknown Request", type=str)
                image = self.tdarr_inform.device.images.generate_image(image_type, message)

        elif method == "get":
            image = self.tdarr_inform.device.images.generate_image("content", "Unknown Request")

        if image:
            imagemimetype = self.tdarr_inform.device.images.get_image_type(image)
            return Response(image, content_type=imagemimetype, direct_passthrough=True)

        else:
            return abort(501, "Not a valid image request")
