import pytesseract

<<<<<<< HEAD
<<<<<<< HEAD
#pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'
=======
pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'
>>>>>>> added all relevant files of Niklas
=======
#pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'
>>>>>>> fix ocr api

def image_to_text(croped_images, custom_config):
    
    def post_process_text(text: str) -> str:
        text = text.replace('\n', ' ')
        text = text.replace('\x0c', '')
        text = text.lower()
        return text
    
    text_all = []
    for croped in croped_images:
        data = pytesseract.image_to_data(croped,lang='eng', config=custom_config, output_type='data.frame') 
      
        if len(data[data.conf != -1]) == 0:
            continue
            
        text = str(data[data.conf != -1].text.values[0])
        conf = data[data.conf != -1].conf.values[0]
        
        text = post_process_text(text)
        text_all.append(text)
    
    text = ''
    
    for i, word in enumerate(text_all):
        text += word
        if i != len(text_all) -1:
            text += ' '
    
<<<<<<< HEAD
<<<<<<< HEAD
    return text[:-1], conf
=======
    return text[:-1], conf
>>>>>>> added all relevant files of Niklas
=======
    return text[:-1], conf
>>>>>>> fix ocr api
