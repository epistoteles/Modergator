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
import json
from transformers import Speech2TextProcessor, Speech2TextForConditionalGeneration
import soundfile as sf
import subprocess
import pickle

app = Flask(__name__)
api = Api(app)

class ASRClassifierRequestSchema(Schema):
    filename = fields.Str(required=True, description="A filename of an .oga speech file that has already been downloaded by the modergator bot.")

class ASRClassifierResponseSchema(Schema):
    transcription = fields.Str(description="The transcription of the given speech file.")

DATA_STUMP = 'data/'

class ASR(MethodResource,Resource):

    model = Speech2TextForConditionalGeneration.from_pretrained("facebook/s2t-small-librispeech-asr")
    processor = Speech2TextProcessor.from_pretrained("facebook/s2t-small-librispeech-asr")

    @doc(description='A classifier that detects the target of a text.',  tags=['ASR Classification'])
    @use_kwargs(ASRClassifierRequestSchema, location="querystring")
    @marshal_with(ASRClassifierResponseSchema)
    def get(self, **kwargs):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('filename', required=True)  # add args
        args = parser.parse_args()  # parse arguments to dictionary
        filename = args['filename']

        stump = DATA_STUMP + 'voice/'
        filename, _ = filename.split('.')

        # convert .oga file to .wav and resample to 16000 Hz
        subprocess.run(
            ['ffmpeg', '-y', '-i', f'{stump}{filename}.oga', '-ar', '16000', f'{stump}{filename}.wav'])

        audio, sr = sf.read(f'{stump}{filename}.wav')

        input_features = self.processor(
            audio,
            sampling_rate=16000,
            return_tensors="pt"
        ).input_features  # Batch size 1
        generated_ids = self.model.generate(input_ids=input_features)

        transcription = self.processor.batch_decode(generated_ids)
        transcription = transcription[0].replace('</s>', '').strip(' ')

        return {'transcription': transcription}, 200

    #def post(self):
    #    pass

    #def put(self):
    #    pass

    #def delete(self):
    #    pass

api.add_resource(ASR, '/asr')  # add endpoints

# check if project is run with scripts or docker and assign ports
# check if project is run with scripts or docker and assign ports
if os.path.isfile("portdict.pickle"):
    port = pickle.load(open("portdict.pickle", "rb"))['text-api']
    host = '127.0.0.1'
else:
    port = 5004
    host = '172.20.0.14'

app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Audio Speech Recognition Classifier API [only usable for Modergator Bot]',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)

docs.register(ASR)

if __name__ == '__main__':
    app.run(host=host, port=port)  # run our Flask app
