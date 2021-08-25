import torch
import torch.nn as nn
from torch import optim
from torch.nn.modules import dropout
from torch.utils.data import DataLoader
from transformers import BertTokenizer
from hatespeech_dataset import HateSpeechDataset
from model import TargetGroupModel

def prepare(training_split, batch_size, learning_rate, dropout_ratio):
    torch.multiprocessing.freeze_support()
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    dataset = HateSpeechDataset("data/dataset.json", tokenizer)
    model = TargetGroupModel(len(dataset.target_group_set), dropout_ratio)
    model = model.to(device)

    train_size = int(training_split * len(dataset))
    test_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])
    train_loader = DataLoader(train_dataset, batch_size = batch_size, num_workers = 0)
    val_loader = DataLoader(val_dataset, batch_size = batch_size, num_workers = 0)
    optimizer = optim.Adam(model.parameters(), lr = learning_rate)
    return device, model, train_loader, val_loader, optimizer

def training(device, model, train_loader, optimizer, epochs):
    for ep in range(epochs):
        for it, (token_ids, token_type_ids, attention_mask, target_labels) in enumerate(train_loader):
            optimizer.zero_grad()

            token_ids = token_ids.to(device)
            token_type_ids = token_type_ids.to(device)
            attention_mask = attention_mask.to(device)
            target_labels = target_labels.to(device)

            logits = model(token_ids, token_type_ids, attention_mask)
            loss_fct = nn.BCEWithLogitsLoss()
            loss = loss_fct(logits, target_labels)

            loss.backward()
            optimizer.step()

            if (it + 1) % 10 == 0:
                print("Iteration {} of epoch {} complete. Loss : {}".format(it + 1, ep + 1, loss.item()))

def evaluate(device, model, val_loader, threshold, batch_size, amount_targets):
    tp, fp, tn, fn = 0, 0, 0, 0
    with torch.no_grad():
        for it, (token_ids, token_type_ids, attention_mask, target_labels) in enumerate(val_loader):
            token_ids = token_ids.to(device)
            token_type_ids = token_type_ids.to(device)
            attention_mask = attention_mask.to(device)
            target_labels = target_labels.to(device)
            logits = model(token_ids, token_type_ids, attention_mask)
            logits = torch.sigmoid(logits)
            logits = torch.where(logits < threshold, logits, torch.ones(batch_size, amount_targets))
            logits = torch.where(logits >= threshold, logits, torch.zeros(batch_size, amount_targets))

            tp_tensor = torch.where(logits == (target_labels == 1), logits, torch.zeros(batch_size, amount_targets))
            tp += (tp_tensor == 1.).sum().item()
            fp_tensor = torch.where((logits == 1) != target_labels, logits, torch.zeros(batch_size, amount_targets))
            fp += (fp_tensor == 1.).sum().item()
            tn_tensor = torch.where(logits == (target_labels == 0), logits, torch.ones(batch_size, amount_targets))
            tn += (tn_tensor == 0.).sum().item()
            fn_tensor = torch.where((logits == 0) != target_labels, logits, torch.ones(batch_size, amount_targets))
            fn += (fn_tensor == 0.).sum().item()

if __name__ == '__main__':
    batch_size = 64
    epochs = 10
    learning_rate = 2e-3
    dropout_ratio = 0.4
    train_size = 0.8
    classification_threshold = 0.4
    device, model, train_loader, val_loader, optimizer = prepare(train_size, batch_size, learning_rate, dropout_ratio)
    training(device, model, train_loader, optimizer, epochs)
    torch.save(model.state_dict(), "models/hate_target.pth")
    evaluate(device, model, val_loader, classification_threshold, batch_size, model.amount_target_groups)