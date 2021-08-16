import pytest
import requests
import pickle

PORTDICT = pickle.load(open("portdict.pickle", "rb"))

def test_text_api():
    params = {"text": "dies ist ein test text."}
    r = requests.get(url=f"http://127.0.0.1:{PORTDICT['text-api']}/classifier", params=params)
    assert r.status_code == 200 # Assumes that it will return a 200 response

#def test_target_api():
#    params = {"text": "Test text."}
#    r = requests.get(url=f"http://127.0.0.1:{PORTDICT['target-api']}/classifier", params=params)
#    assert r.status_code == 200 # Assumes that it will return a 200 response

def test_ocr_api_with_meme():
    image_url = "https://irights.info/wp-content/uploads/2016/05/notsure-490x368.jpg"
    params = {"path": image_url}
    r = requests.get(url=f"http://127.0.0.1:{PORTDICT['ocr-api']}/ocr", params=params)
    assert r.status_code == 200 # Assumes that it will return a 200 response

#def test_ocr_api_with_picture():
#    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Brookfield_zoo_fg06.jpg/450px-Brookfield_zoo_fg06.jpg"
#    params = {"path": image_url}
#    r = requests.get(url=f"http://127.0.0.1:{PORTDICT['ocr-api']}/ocr", params=params)
#    assert r.status_code == 200 # Assumes that it will return a 200 response

#def test_meme_model_api():
#    url = "https://irights.info/wp-content/uploads/2016/05/notsure-490x368.jpg"
#    description = "not sure if funny or copyright infringement"
#    params = {"image" : url, "image_description" : description}
#    r = requests.get(url=f"http://127.0.0.1:{PORTDICT['meme-model-api']}/classifier", params=params)
#    assert r.status_code == 200 # Assumes that it will return a 200 response




