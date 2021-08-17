import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model import TargetGroupModel
#from transformers.file_utils import torch_required
from flask import request
import pickle
#import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
#import json
#import re
from flask_restful import Resource, Api, reqparse
from flask import Flask

app = Flask(__name__)
api = Api(app)

# TODO: change mapping to the specific one (read from command line while training)
id_to_target_group = {0: 'Buddhism', 1: 'Asexual', 2: 'Disability', 3: 'Arab', 4: 'Homosexual', 5: 'African', 6: 'Nonreligious', 7: 'Men', 8: 'Indian', 9: 'Jewish', 10: 'Asian', 11: 'Refugee', 12: 'Caucasian', 13: 'Indigenous', 14: 'Christian', 15: 'Women', 16: 'Heterosexual', 17: 'Bisexual', 18: 'Hindu', 19: 'Other', 20: 'Islam', 21: 'Minority', 22: 'Hispanic', 23: 'Economic'}
model = TargetGroupModel(len(id_to_target_group), 0.1) # dropout_ration = 0.1
model.load_state_dict(torch.load("target-api/model/hate_target.pth",map_location=torch.device('cpu')))
model.eval()
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

class Target(Resource):

    def get(self):
        print("START get")
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('text', required=True)  # add args
        args = parser.parse_args()  # parse arguments to dictionary
        text = args['text']
        #output = self.model.predict(text)
        print("nach text")
        logits = self.predict(text, tokenizer, model)
        print("text nach logits1")
        logits = torch.sigmoid(logits)
        print("text nach logits2")


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
        print("START predicition")
        encoded_input = tokenizer(text)
        token_ids = torch.tensor(encoded_input.input_ids).unsqueeze(0)
        token_type_ids = torch.tensor(encoded_input.token_type_ids).unsqueeze(0)
        attention_mask = torch.tensor(encoded_input.attention_mask).unsqueeze(0)
        logits = model(token_ids, token_type_ids, attention_mask)
        return logits

api.add_resource(Target, '/classifier')  # add endpoints

port = pickle.load(open("portdict.pickle", "rb"))['target-api']

if __name__ == '__main__':
    app.run(port=port)  # run our Flask app
