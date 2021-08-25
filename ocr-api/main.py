import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_apispec import marshal_with, doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_apispec.extension import FlaskApiSpec
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from marshmallow import Schema, fields
import pickle
#import ocr
import analysis_utility
import urllib
import urllib.request

app = Flask(__name__)
api = Api(app)

class OCRClassifierRequestSchema(Schema):
    path = fields.Str(required=True, description="The path/url to an image/meme.")

class OCRClassifierResponseSchema(Schema):
    ocr_text = fields.Str(description="The recognised text form the given image/meme.")

class OCR(MethodResource,Resource):

    @doc(description='This get request triggers a ML model that detects the text from an image/meme.',  tags=['OCR Classification'])
    @use_kwargs(OCRClassifierRequestSchema, location="querystring")
    @marshal_with(OCRClassifierResponseSchema)
    def get(self,**kwargs):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('path', required=True)  # add args
        args = parser.parse_args()  # parse arguments to dictionary
        path = args['path']
        print(path)
        file_ending = path.split(".")[-1]
        print(file_ending)
        filename = "10000" + "." + file_ending
        urllib.request.urlretrieve(path, filename)
        print(os.getcwd())
        print(filename)
        ocr_text, conf = analysis_utility.do_ocr(filename)
        return {'ocr_text': ocr_text, 'conf': conf}, 200

api.add_resource(OCR, '/ocr')  # add endpoints

# check if project is run with scripts or docker and assign ports
if os.path.isfile("portdict.pickle"):
    port = pickle.load(open("portdict.pickle", "rb"))['ocr-api']
else:
    port = 80

app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Optical Character Recognition Classifier API',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)

docs.register(OCR)

if __name__ == '__main__':
    print(port)
    app.run(port=port)  # run our Flask app
