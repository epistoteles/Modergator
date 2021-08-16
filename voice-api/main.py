import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask
from flask_restful import Resource, Api, reqparse
import json
from transformers import Speech2TextProcessor, Speech2TextForConditionalGeneration
import soundfile as sf
import subprocess
import pickle

app = Flask(__name__)
api = Api(app)

DATA_STUMP = 'data/'

class ASR(Resource):

    model = Speech2TextForConditionalGeneration.from_pretrained("facebook/s2t-small-librispeech-asr")
    processor = Speech2TextProcessor.from_pretrained("facebook/s2t-small-librispeech-asr")

    def get(self):
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

    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

api.add_resource(ASR, '/asr')  # add endpoints

port = pickle.load(open("portdict.pickle", "rb"))['voice-api']

if __name__ == '__main__':
    app.run(port=port)  # run our Flask app
