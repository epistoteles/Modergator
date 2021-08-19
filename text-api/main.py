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
from forbidden_words import forbidden_words
import re
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
import pickle

app = Flask(__name__)
api = Api(app)

class TextClassifierRequestSchema(Schema):
    text = fields.Str(required=True, description="A text.")

class TextClassifierResponseSchema(Schema):
    label = fields.Str(description="A label that is either normal, offensive or hateful")
    label_score = fields.Str(description="A score that describes the confidence in the label (0-1)")

class Classifier(MethodResource,Resource):

    tokenizer = AutoTokenizer.from_pretrained("Hate-speech-CNERG/bert-base-uncased-hatexplain")
    model = AutoModelForSequenceClassification.from_pretrained("Hate-speech-CNERG/bert-base-uncased-hatexplain")
    categories = {0: 'hate', 1: 'normal', 2: 'offensive'}

    @doc(description='A classifier that judges the hatefulness of a text.',  tags=['Text Classification'])
    @use_kwargs(TextClassifierRequestSchema, location="querystring")
    @marshal_with(TextClassifierResponseSchema)
    def get(self,**kwargs):
        print("start")
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('text', required=True)  # add args
        args = parser.parse_args()  # parse arguments to dictionary
        text = args['text']
        print("text: ", text)
        inputs = self.tokenizer(text, return_tensors="pt")
        labels = torch.tensor([1]).unsqueeze(0)  # Batch size 1
        outputs = self.model(**inputs, labels=labels)
        scores = outputs.logits.softmax(dim=-1).tolist()[0]
        label = self.categories[np.argmax(scores)]
        print("SCORE LABEL: ", np.argmax(scores))
        print("SCORE LABEL INT", int(np.argmax(scores)))
        return {'label': label,
                'label_score': max(scores)}, 200
                # 'scores': json.dumps(scores),

    #def post(self):
    #    pass

    #def put(self):
    #    pass

    #def delete(self):
    #    pass


api.add_resource(Classifier, '/classifier')  # add endpoints

port = pickle.load(open("portdict.pickle", "rb"))['text-api']

app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Text Classifier API',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)

docs.register(Classifier)

if __name__ == '__main__':
    app.run(port=port)  # run our Flask app
