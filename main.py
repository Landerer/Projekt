from dataclasses import asdict
import logging

from flask import Flask, send_file, render_template, request
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound

import images as img


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
api = Api(app)
images = img.Images("dane", "opisane")


@app.route("/")
def main_page():
    return render_template("main_page.html")


@app.route("/image")
def get_image():
    id = request.args.get("id")
    try:
        file_object = images.get_image(id).asPng()
    except img.ImageNotExistsError as e:
        raise NotFound(str(e)) from e

    return send_file(file_object, mimetype="image/PNG")


@api.resource("/images")
class Images(Resource):
    def get(self):
        return [asdict(image) for image in images.get_images(is_described=False)]


@api.resource("/images/<int:image_id>")
class Image(Resource):
    def get(self, image_id):
        try:
            asdict(images.get_image(image_id))
        except img.ImageNotExistsError as e:
            raise NotFound(str(e)) from e

    def put(self, image_id):
        images.save_image(image_id)


@api.resource("/images/<int:image_id>/descriptions")
class Descriptions(Resource):
    def get(self, image_id):
        try:
            return [asdict(d) for d in images.get_descriptions(image_id)]
        except img.DescriptionNotExistsError as e:
            raise NotFound(str(e)) from e

    def delete(self, image_id):
        images.delete_descriptions(image_id)


@api.resource("/images/<int:image_id>/descriptions/<int:description_id>")
class Description(Resource):
    def post(self, image_id, description_id):
        logging.debug(request.form)
        description = img.Description(
            description_id,
            image_id,
            int(request.form["x"]),
            int(request.form["y"]),
            int(request.form["width"]),
            int(request.form["height"]),
        )
        images.add_description(description)
        return asdict(description)

    def get(self, image_id, description_id):
        try:
            return asdict(images.get_description(image_id, description_id))
        except img.DescriptionNotExistsError as e:
            raise NotFound(str(e)) from e

    def delete(self, image_id, description_id):
        images.delete_description(image_id, description_id)


app.run()