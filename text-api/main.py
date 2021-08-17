import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask
from flask_restful import Resource, Api, reqparse
from forbidden_words import forbidden_words
import re
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
import pickle

app = Flask(__name__)
api = Api(app)

class Classifier(Resource):
    # def get(self):
    #     parser = reqparse.RequestParser()  # initialize
    #     parser.add_argument('text', required=True)  # add args
    #     args = parser.parse_args()  # parse arguments to dictionary
    #     text = args['text']
    #
    #     words = {x for x in forbidden_words if bool(re.search(f'(^|\\W){x}(\\W|$)', text.lower()))}
    #
    #     return {'score': float(int(bool(words))),
    #             'words': json.dumps(list(words))}, 200

    tokenizer = AutoTokenizer.from_pretrained("Hate-speech-CNERG/bert-base-uncased-hatexplain")
    model = AutoModelForSequenceClassification.from_pretrained("Hate-speech-CNERG/bert-base-uncased-hatexplain")
    categories = {0: 'hate', 1: 'normal', 2: 'offensive'}

    def get(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('text', required=True)  # add args
        args = parser.parse_args()  # parse arguments to dictionary
        text = args['text']
        inputs = self.tokenizer(text, return_tensors="pt")
        labels = torch.tensor([1]).unsqueeze(0)  # Batch size 1
        outputs = self.model(**inputs, labels=labels)
        scores = outputs.logits.softmax(dim=-1).tolist()[0]
        label = self.categories[np.argmax(scores)]
        print("SCORE LABEL: ", np.argmax(scores))
        print("SCORE LABEL INT", int(np.argmax(scores)))
        return {'scores': json.dumps(scores),
                'label': label,
                'label_score': max(scores)}, 200

    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass


api.add_resource(Classifier, '/classifier')  # add endpoints

port = pickle.load(open("portdict.pickle", "rb"))['text-api']

if __name__ == '__main__':
    app.run(port=port)  # run our Flask app
