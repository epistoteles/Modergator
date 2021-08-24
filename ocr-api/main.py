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
import ocr

app = Flask(__name__)
api = Api(app)

class OCRClassifierRequestSchema(Schema):
    path = fields.Str(required=True, description="The path/url to an image/meme.")

class OCRClassifierResponseSchema(Schema):
    ocr_text = fields.Str(description="The recognised text form the given image/meme.")

class OCR(MethodResource,Resource):

    @doc(description='A classifier that detects the text from an image/meme.',  tags=['OCR Classification'])
    @use_kwargs(OCRClassifierRequestSchema, location="querystring")
    @marshal_with(OCRClassifierResponseSchema)
    def get(self,**kwargs):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('path', required=True)  # add args
        args = parser.parse_args()  # parse arguments to dictionary
        path = args['path']

        ocr_text = ocr.do_ocr(path, custom_config = r'--oem 1 --psm 8')
        return {'ocr_text': ocr_text}, 200

api.add_resource(OCR, '/ocr')  # add endpoints

# check if project is run with scripts or docker and assign ports
if os.path.isfile("portdict.pickle"):
    port = pickle.load(open("portdict.pickle", "rb"))['text-api']
    host = '127.0.0.1'
else:
    port = 5003
    host = '172.20.0.13'

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
    app.run(host=host, port=port)  # run our Flask app
