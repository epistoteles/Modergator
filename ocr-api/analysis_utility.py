import ocr_utility
import img_utility
import text_scene_detection_utility
import pandas as pd
#from IPython.display import clear_output, display

net = text_scene_detection_utility.build_model()

# run entire ocr pipeline
def do_ocr(path, custom_config=r'--oem 1 --psm 8'):

    img_list = img_utility.load_img(path)
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    bounding_boxes, b, ret_score_text = text_scene_detection_utility.text_detection(net, img_list, text_threshold=0.8, link_threshold=0.4, low_text=0.4, cuda=False, poly=False, refine_net=None)
=======
    bounding_boxes, b, ret_score_text = text_scene_detection_utility.text_detection(net, img_list, text_threshold=0.8, link_threshold=0.4, low_text=0.4, cuda=True, poly=False, refine_net=None)
>>>>>>> added all relevant files of Niklas
=======
    bounding_boxes, b, ret_score_text = text_scene_detection_utility.text_detection(net, img_list, text_threshold=0.8, link_threshold=0.4, low_text=0.4, cuda=False, poly=False, refine_net=None)
>>>>>>> fix cuda bugs
=======
    bounding_boxes, b, ret_score_text = text_scene_detection_utility.text_detection(net, img_list, text_threshold=0.8, link_threshold=0.4, low_text=0.4, cuda=False, poly=False, refine_net=None)
>>>>>>> 4991298cebf79f2f5678780bbeee0740e508ed13

    if len(bounding_boxes) == 0:
        return '', 100

    croped_images, font_color, all_mean_edge_colors, total_mean_edge_colors_all = img_utility.crop_images(bounding_boxes, img_list)
    text, conf = ocr_utility.image_to_text(croped_images, custom_config)

    return text, conf


def ocr_on_df(df, ds_name, path, img_format):

    result_list = []

    for i in range(len(df)):
        clear_output(wait=True)
        display(i)

        row = df.iloc[i]

        if ds_name=='fb':
            img_columm = row['img']
            _id = img_columm.split('/')[-1].split('.')[0]
            orig_text = row['text']
            img_name = _id + '.' + img_format
        if ds_name=='kaggle':
            None

        text, conf = do_ocr(path+img_name)

        result = {'ds_name': ds_name, '_id': _id, 'confidence': conf, 'orig_text': orig_text, 'pred_text': text, 'orig_text': orig_text}
        result_list.append(result)

    result_df = pd.DataFrame(result_list)
    return result_df
