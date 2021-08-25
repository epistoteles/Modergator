import torch
from torch.utils.data import Dataset
import json

class Tweet:
    post_id = ""
    post_tokens = []
    annotators = []
    targets = []
    targets_ids = []
    targets_one_hot = []

class HateSpeechDataset(Dataset):

    def __init__(self, dataset_path, tokenizer):
        super().__init__()
        self.all_tweets = self.read_tweets(dataset_path)
        self.bert_post_tokens = tokenizer([tweet.post_tokens for tweet in self.all_tweets], is_split_into_words = True, padding = True)
        self.target_group_set = self.get_target_group_set(self.all_tweets)
        self.target_to_id = {target: id for id, target in enumerate(self.target_group_set)}
        self.id_to_target = {id: target for target, id in self.target_to_id.items()}
        print(self.id_to_target)
        self.add_target_ids(self.all_tweets)

    def __len__(self):
        return len(self.all_tweets)

    def __getitem__(self, index):
        token_ids = torch.tensor(self.bert_post_tokens.input_ids[index])
        token_type_ids = torch.tensor(self.bert_post_tokens.token_type_ids[index])
        attention_mask = torch.tensor(self.bert_post_tokens.attention_mask[index])
        target_labels = torch.tensor(self.all_tweets[index].targets_one_hot)
        return token_ids, token_type_ids, attention_mask, target_labels

    def read_tweets(self, dataset_path):
        with open(dataset_path) as f:
            data = json.load(f)
        all_tweets = []
        for tweet_key in data:
            tweet = Tweet()
            tweet.post_id = data[tweet_key]["post_id"]
            tweet.post_tokens = data[tweet_key]["post_tokens"]
            tweet.annotators = data[tweet_key]["annotators"]
            tweet.targets = []
            for annotator in tweet.annotators:
                for annotation in annotator["target"]:
                    if annotation != "None":
                        tweet.targets.append(annotation)
            all_tweets.append(tweet)
        return all_tweets
    
    def get_target_group_set(self, all_tweets):
        target_group_set = set()
        for tweet in all_tweets:
            for target in tweet.targets:
                target_group_set.add(target)
        return target_group_set

    def add_target_ids(self, all_tweets):
        for tweet in all_tweets:
            tweet.targets_ids = [self.target_to_id[x] for x in tweet.targets]
            tweet.targets_ids = list(set(tweet.targets_ids))
            tweet.targets_one_hot = [0.0] * len(self.target_group_set)
            for x in tweet.targets_ids:
                tweet.targets_one_hot[x] = 1.0