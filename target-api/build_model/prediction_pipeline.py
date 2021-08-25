from transformers import AutoTokenizer
from transformers.file_utils import torch_required
from model import TargetGroupModel
import torch

#TODO: change mapping to the specific one (read from command line while training)
id_to_target_group = {0: 'Asian', 1: 'Women', 2: 'Christian', 3: 'Caucasian', 4: 'Refugee', 5: 'Economic', 6: 'Bisexual', 7: 'Indigenous', 8: 'Asexual', 9: 'Hispanic', 10: 'Nonreligious', 11: 'Men', 12: 'Buddhism', 13: 'Indian', 14: 'African', 15: 'Jewish', 16: 'Minority', 17: 'Disability', 18: 'Arab', 19: 'Other', 20: 'Heterosexual', 21: 'Islam', 22: 'Homosexual', 23: 'Hindu'}

def predict(text, tokenizer, model):
    encoded_input = tokenizer(text)
    token_ids = torch.tensor(encoded_input.input_ids).unsqueeze(0)
    token_type_ids = torch.tensor(encoded_input.token_type_ids).unsqueeze(0)
    attention_mask = torch.tensor(encoded_input.attention_mask).unsqueeze(0)
    logits = model(token_ids, token_type_ids, attention_mask)
    return logits

text = "Text here"
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
model = TargetGroupModel(len(id_to_target_group))
model.load_state_dict(torch.load("models/hate_target.pth", map_location=torch.device('cpu')))
logits = predict(text, tokenizer, model)
logits = torch.sigmoid(logits)

print("Input text:", text)
print("Logits:")
print(logits)
print("=====================================================================================")
print("Max logit value:", logits.max())
print("Min logit value:", logits.min())

hits = (logits > 0.4).nonzero(as_tuple = True)[1]
target_groups = [id_to_target_group[x] for x in hits.tolist()]

print("Offended target groups predicted by model:", target_groups)