import torch.nn as nn
from transformers import BertModel

class TargetGroupModel(nn.Module):

    def __init__(self, amount_target_groups, dropout_ratio, freeze_bert = True):
        super(TargetGroupModel, self).__init__()
        self.amount_target_groups = amount_target_groups

        self.bert_layer = BertModel.from_pretrained("bert-base-uncased")
        
        if freeze_bert:
            for p in self.bert_layer.parameters():
                p.requires_grad = False
        
        self.dropout = nn.Dropout(dropout_ratio)
        self.target_group_classifier = nn.Linear(768, self.amount_target_groups)

    def forward(self, input_token_ids, token_type_ids, attention_mask):
        bert_pooled = self.bert_layer(input_token_ids, token_type_ids = token_type_ids, attention_mask = attention_mask)[1]
        bert_pooled = self.dropout(bert_pooled)
        target_logits = self.target_group_classifier(bert_pooled)
        return target_logits