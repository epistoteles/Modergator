import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model import TargetGroupModel
#from transformers.file_utils import torch_required
from flask import request
import pickle
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from flask_restful import Resource, Api, reqparse
from flask import Flask
from flask_apispec import marshal_with, doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_apispec.extension import FlaskApiSpec
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from marshmallow import Schema, fields

app = Flask(__name__)
api = Api(app)

class TargetClassifierRequestSchema(Schema):
    text = fields.Str(required=True, description="A text.")

class TargetClassifierResponseSchema(Schema):
    target_groups = fields.Str(description="All target groups that have been detected (can be none : [])")

# wenn the model is retrained, change the mapping here to the specific one of the trained model (read from command line while training)
id_to_target_group = {0: 'Buddhism', 1: 'Asexual', 2: 'Disability', 3: 'Arab', 4: 'Homosexual', 5: 'African', 6: 'Nonreligious', 7: 'Men', 8: 'Indian', 9: 'Jewish', 10: 'Asian', 11: 'Refugee', 12: 'Caucasian', 13: 'Indigenous', 14: 'Christian', 15: 'Women', 16: 'Heterosexual', 17: 'Bisexual', 18: 'Hindu', 19: 'Other', 20: 'Islam', 21: 'Minority', 22: 'Hispanic', 23: 'Economic'}
model = TargetGroupModel(len(id_to_target_group), 0.1) # dropout_ration = 0.1
model.load_state_dict(torch.load("target-api/model/hate_target.pth",map_location=torch.device('cpu')))
model.eval()
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

class Target(MethodResource,Resource):

    @doc(description='This get request triggers a classifier that detects the target of a text.',  tags=['Target Classification'])
    @use_kwargs(TargetClassifierRequestSchema, location="querystring")
    @marshal_with(TargetClassifierResponseSchema)
    def get(self,**kwargs):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('text', required=True)  # add args
        args = parser.parse_args()  # parse arguments to dictionary
        text = args['text']
        logits = self.predict(text, tokenizer, model)
        logits = torch.sigmoid(logits)
        print("Input text:", text)
        print("Logits:")
        print(logits)
        print("=====================================================================================")
        print("Max logit value:", logits.max())
        print("Min logit value:", logits.min())

        hits = (logits > 0.4).nonzero(as_tuple=True)[1]
        target_groups = [id_to_target_group[x] for x in hits.tolist()]

        print("Offended target groups predicted by model:", target_groups)
        return {'target_groups': target_groups}

    def predict(self,text, tokenizer, model):
        encoded_input = tokenizer(text)
        token_ids = torch.tensor(encoded_input.input_ids).unsqueeze(0)
        token_type_ids = torch.tensor(encoded_input.token_type_ids).unsqueeze(0)
        attention_mask = torch.tensor(encoded_input.attention_mask).unsqueeze(0)
        logits = model(token_ids, token_type_ids, attention_mask)
        return logits

api.add_resource(Target, '/classifier')  # add endpoints

app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Target Classifier API',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)

docs.register(Target)

# check if project is run with scripts or docker and assign ports
if os.path.isfile("portdict.pickle"):
    port = pickle.load(open("portdict.pickle", "rb"))['target-api']
    host = '127.0.0.1'
else:
    port = 5005
    host = '172.20.0.15'

if __name__ == '__main__':
    app.run(host=host, port=port)  # run our Flask app
