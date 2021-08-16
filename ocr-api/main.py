import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask
from flask_restful import Resource, Api, reqparse
import pickle
import ocr

app = Flask(__name__)
api = Api(app)

class OCR(Resource):

    def get(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('path', required=True)  # add args
        args = parser.parse_args()  # parse arguments to dictionary
        path = args['path']

        ocr_text = ocr.do_ocr(path, custom_config = r'--oem 1 --psm 8')
        return {'ocr_text': ocr_text}, 200


    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass


api.add_resource(OCR, '/ocr')  # add endpoints

port = pickle.load(open("portdict.pickle", "rb"))['ocr-api']

if __name__ == '__main__':

    app.run(port=port)  # run our Flask app
