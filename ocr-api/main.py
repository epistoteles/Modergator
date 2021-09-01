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
<<<<<<< HEAD
<<<<<<< HEAD
#import ocr
import analysis_utility
import urllib
import urllib.request
=======
import ocr
=======
#import ocr
>>>>>>> fix ocr api
import analysis_utility
<<<<<<< HEAD
>>>>>>> try to import analysis_utility.py not working yet
=======
import urllib
import urllib.request
>>>>>>> add Niklas new ocr, draft for downloading img

app = Flask(__name__)
api = Api(app)

class OCRClassifierRequestSchema(Schema):
    path = fields.Str(required=True, description="The path/url to an image/meme.")

class OCRClassifierResponseSchema(Schema):
    ocr_text = fields.Str(description="The recognised text form the given image/meme.")
    conf = fields.Str(description="The confidence socre of the ocr text.")

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
<<<<<<< HEAD
<<<<<<< HEAD
        print(os.getcwd())
        print(filename)
        ocr_text, conf = analysis_utility.do_ocr(filename)
        print('ocr:', ocr_text)
        print('conf', conf)
        print('both from api')
        return {'ocr_text': ocr_text, 'conf': conf}, 200
=======
        analysis_utility.do_ocr(r'../filename')
        #ocr_text = "test"
=======
        print(os.getcwd())
<<<<<<< HEAD
        analysis_utility.do_ocr(filename)
        print('ocr success')
>>>>>>> fix cuda bugs
        ocr_text, conf = analysis_utility.do_ocr(path, custom_config = r'--oem 1 --psm 8')
=======
        print(filename)
        ocr_text, conf = analysis_utility.do_ocr(filename)
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> fix ocr api
        return {'ocr_text': ocr_text}, 200
>>>>>>> add Niklas new ocr, draft for downloading img
=======
=======
        print(ocr_text)
        print(conf)
=======
        print('ocr:', ocr_text)
        print('conf', conf)
>>>>>>> added print statement
        print('both from api')
>>>>>>> try to fix issues with ocr, not working
        return {'ocr_text': ocr_text, 'conf': conf}, 200
>>>>>>> add conf from ocr

api.add_resource(OCR, '/ocr')  # add endpoints

# check if project is run with scripts or docker and assign ports
if os.path.isfile("portdict.pickle"):
    port = pickle.load(open("portdict.pickle", "rb"))['ocr-api']
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
