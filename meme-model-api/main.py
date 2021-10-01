import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import flask
from flask import Flask
from flask import request
from flask import jsonify
from flask_restful import Resource, Api, reqparse
from flask_apispec import marshal_with, doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_apispec.extension import FlaskApiSpec
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from marshmallow import Schema, fields
import requests  # to get image from the web
import shutil  # to save it locally
import urllib
import urllib.request
import json
import subprocess  # to use subprocess
import glob
import pickle

app = Flask(__name__)
api = Api(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'JPG', 'JPEG'}
UPLOAD_FOLDER = '.meme-model-api/vilio/data/img'

class ModelRequestSchema(Schema):
    image = fields.Str(required=True, description="URL of an image. Allowed extensions are 'png', 'jpg', 'jpeg', 'gif', 'JPG', 'JPEG'")
    image_description = fields.Str(required=True, description="The text that is shown on the image.")

class ModelResponseSchema(Schema):
    result = fields.Boolean(description="True = the meme is not hateful, False = the meme is hateful")

class Model(MethodResource,Resource):

    @doc(description='This get request triggers a ML Model that judges the hatefulness of a meme.',  tags=['Meme Classification'])
    @use_kwargs(ModelRequestSchema, location="form")
    @marshal_with(ModelResponseSchema)
    def post(self, **kwargs):
        src_dir = os.getcwd()
        image_url = request.form['image']
        image_description = request.form['image_description']
        if not image_url:
            raise APIImageError('No matching image file found (.jpg .jpeg. png .gif JPG or JPEG)')
        else:
            filename = image_url.split("/")[-1]
            fullfilename = os.path.join(UPLOAD_FOLDER, filename)
            file_ending = image_url.split(".")[-1]
            only_filename = filename.split(".")[0]
            if self.validate_file(filename):
                headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                           'Accept-Encoding': 'none',
                           'Accept-Language': 'en-US,en;q=0.8',
                           'Connection': 'keep-alive'}
                request_ = urllib.request.Request(
                    image_url, None, headers)  # The assembled request
                response = urllib.request.urlopen(
                    request_)  # store the response

                # save image for inference
                file_inference = "10000" + "." + file_ending
                f = open('meme-model-api/vilio/data/img/' + file_inference, 'wb')
                rep = response.read()
                f.write(rep)
                f.close()

                #  save image for feature extraction
                file_extraction = "10000" + "." + file_ending
                f = open('meme-model-api/vilio/py-bottom-up-attention/data/img/' +
                         file_extraction, 'wb')
                f.write(rep)
                f.close()

            try:
                json_file = self.create_json(file_ending, only_filename, image_description)
                self.extract_features()
                score = self.calculate_score()
                score_float = float(score)
                hate_value = self.calculate_hate(score_float)
            # any error: always delete saved image(s)
            except:
                self.clean_up()

            result = False
            if hate_value=="1": # 0 = not hateful, 1 = hateful
                result = True
            data = {'result': result}
            self.clean_up()
            return data

    def validate_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def calculate_score(self):
        p1 = subprocess.Popen(['python3', 'model_inference.py', '--seed', '129', '--model', 'U', '--test', 'testset',
                             '--lr', '1e-5', '--batchSize', '8', '--tr', 'bert-large-cased', '--epochs', '5',
                                     '--tsv', '--num_features', '36', '--num_pos', '6', '--loadfin', './input/viliou36/LASTtraindev.pth', '--exp', 'U36'], cwd = 'meme-model-api/vilio', stdout=subprocess.PIPE)
        p_status = p1.wait()
        result = p1.communicate()[0]
        string_result = result.split()
        return string_result[-1].decode('UTF-8')

    def create_json(self, file_ending, only_filename, image_description):
        data = {}
        data['id'] = 10000
        data['img'] = "img/" + "10000" + "." + file_ending
        data['label'] = 1 # means hateful
        data['text'] = image_description

        path = 'meme-model-api/vilio/data/'
        jsonname = 'testset'
        ext = '.json'
        filePathNameWExt = path + jsonname + ext

        #gets overriden with new file
        with open(filePathNameWExt, "w") as f:
            f.seek(0)
            json.dump(data, f)

    def extract_features(self):
        p = subprocess.Popen(['python3', 'detectron2_mscoco_proposal_maxnms.py', '--batchsize', '1', '--split', 'img', '--weight', 'vgattr', '--minboxes', '36', '--maxboxes', '36'],cwd="meme-model-api/vilio/py-bottom-up-attention/")
        #This makes the wait possible:
        p_status = p.wait()
        shutil.move("meme-model-api/vilio/py-bottom-up-attention/data/hm_vgattr3636.tsv","meme-model-api/vilio/data/HM_img.tsv")
    def calculate_hate(self, prob):
        if(prob <= -0.75):
            return 1
        else:
            return 0

    def clean_up(self):
        files = glob.glob('meme-model-api/vilio/data/img/*')
        for f in files:
            os.remove(f)
        files0 = glob.glob('meme-model-api/vilio/data/HM_img.tsv')
        for f0 in files0:
            os.remove(f0)
        files2 = glob.glob('meme-model-api/vilio/py-bottom-up-attention/data/img/*')
        for f2 in files2:
            os.remove(f2)

class APIImageError(Exception):
    code = 403
    description = "Image Handling Error"

api.add_resource(Model, '/classifier')

# check if project is run with scripts or docker and assign ports
if os.path.isfile("portdict.pickle"):
    port = pickle.load(open("portdict.pickle", "rb"))['meme-model-api']
    host = '127.0.0.1'
else:
    port = 5001
    host = '0.0.0.0'

app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Meme Model API',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)

docs.register(Model)

if __name__ == '__main__':
    app.run(host=host, port=port)  # run our Flask app
