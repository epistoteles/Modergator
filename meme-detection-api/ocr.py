import pytesseract
import pandas as pd
from PIL import Image
from model.craft import CRAFT
import model.craft_utils as craft_utils
import torch
from collections import OrderedDict
import torch.backends.cudnn as cudnn
import time
import numpy as np
import model.imgproc as imgproc
import cv2
from torch.autograd import Variable
from operator import itemgetter


def get_edge_colors(image):
    def append_colors(x, y):
        r, g, b = px[x, y]
        single_result = {'r': r, 'g': g, 'b': b}
        edge_colors.append(single_result)

    edge_colors = []
    image = Image.fromarray(image).convert('RGB')
    px = image.load()

    for x in range(image.width):
        for y in range(image.height):
            if x == 0 or x == image.width:
                append_colors(x, y)
            elif y == 0 or y == image.height:
                append_colors(x, y)

    result_df = pd.DataFrame(edge_colors)

    r_mean = result_df.r.mean()
    g_mean = result_df.g.mean()
    b_mean = result_df.b.mean()
    total_mean = np.mean([r_mean, g_mean, b_mean])

    return total_mean


def test_net(net, image, text_threshold, link_threshold, low_text, cuda, poly, refine_net=None):
    t0 = time.time()

    # resize
    img_resized, target_ratio, size_heatmap = imgproc.resize_aspect_ratio(image, square_size=1280,
                                                                          interpolation=cv2.INTER_LINEAR, mag_ratio=1.5)
    ratio_h = ratio_w = 1 / target_ratio

    # preprocessing
    x = imgproc.normalizeMeanVariance(img_resized)
    x = torch.from_numpy(x).permute(2, 0, 1)  # [h, w, c] to [c, h, w]
    x = Variable(x.unsqueeze(0))  # [c, h, w] to [b, c, h, w]
    if cuda:
        x = x.cpu()

    # forward pass
    with torch.no_grad():
        y, feature = net(x)

    # make score and link map
    score_text = y[0, :, :, 0].cpu().data.numpy()
    score_link = y[0, :, :, 1].cpu().data.numpy()

    # refine link
    if refine_net is not None:
        with torch.no_grad():
            y_refiner = refine_net(y, feature)
        score_link = y_refiner[0, :, :, 0].cpu().data.numpy()

    t0 = time.time() - t0
    t1 = time.time()

    # Post-processing
    boxes, polys = craft_utils.getDetBoxes(score_text, score_link, text_threshold, link_threshold, low_text, poly)

    # coordinate adjustment
    boxes = craft_utils.adjustResultCoordinates(boxes, ratio_w, ratio_h)
    polys = craft_utils.adjustResultCoordinates(polys, ratio_w, ratio_h)
    for k in range(len(polys)):
        if polys[k] is None: polys[k] = boxes[k]

    t1 = time.time() - t1

    # render results (optional)
    render_img = score_text.copy()
    render_img = np.hstack((render_img, score_link))
    ret_score_text = imgproc.cvt2HeatmapImg(render_img)

    return boxes, polys, ret_score_text


def copyStateDict(state_dict):
    if list(state_dict.keys())[0].startswith("module"):
        start_idx = 1
    else:
        start_idx = 0
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = ".".join(k.split(".")[start_idx:])
        new_state_dict[name] = v
    return new_state_dict


def grouper(iterable):
    prev = None
    group = []
    for item in iterable:
        if not prev or item - prev <= 15:
            group.append(item)
        else:
            yield group
            group = [item]
        prev = item
    if group:
        yield group


def get_images(bboxes, image):
    def handle_negatives(x, y):
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        return x, y

    coordinates = []
    for box in bboxes:
        rect = cv2.boundingRect(box)
        x, y, w, h = rect
        coordinates.append({'x': x, 'y': y, 'w': w, 'h': h})

    y_all = [item['y'] for item in coordinates]
    h_all = [item['h'] for item in coordinates]
    y_clusters = dict(enumerate(grouper(y_all), 1))

    y_cluster_min_all = {}

    for cluster in y_clusters.keys():
        y_cluster_single = np.min(y_clusters[cluster])
        y_cluster_min_all[cluster] = y_cluster_single

    height_max = np.max(h_all)

    for pts in coordinates:
        for cluster in y_clusters.keys():
            if pts['y'] in y_clusters[cluster]:
                diff = pts['y'] - y_cluster_min_all[cluster]
                if diff > 0:
                    pts['h'] = pts['h'] + abs(diff)
                pts['y'] = y_cluster_min_all[cluster]

    coordinates = sorted(coordinates, key=itemgetter('y', 'x'))

    croped_images = []
    total_mean_edge_colors_all = []
    for pts in coordinates:
        x, y, w, h = pts['x'], pts['y'], pts['w'], pts['h']
        x, y = handle_negatives(x, y)
        croped = image[y:y + h, x:x + w].copy()
        total_mean_edge_colors = get_edge_colors(croped)
        total_mean_edge_colors_all.append(total_mean_edge_colors)

        #if debug:
        #    display(Image.fromarray(croped))

        th, croped = cv2.threshold(croped, 200, 255, cv2.THRESH_BINARY_INV)

        croped_images.append(croped)

    all_mean_edge_colors = np.mean(total_mean_edge_colors_all)

    if all_mean_edge_colors < 50:
        font_color = 'white'
    elif all_mean_edge_colors > 200:
        font_color = 'black'
    else:
        font_color = 'white'

    #if debug:
    #    print('detected_font_color: ', font_color)

    for i in range(len(croped_images)):
        if font_color == 'black':
            croped_images[i] = cv2.bitwise_not(croped_images[i])
    return croped_images


def get_croped_images(image):
    bboxes, polys, score_text = test_net(net, image, text_threshold=0.8, link_threshold=0.4, low_text=0.4, cuda=True,
                                         poly=False, refine_net=None)
    croped_images = get_images(bboxes, image)
    return croped_images


def do_ocr(f, custom_config, resize=None):
    image = imgproc.loadImage(f)
    if resize:
        height, width = image.shape[:2]
        image = cv2.resize(image, (int(resize * width), int(resize * height)), interpolation=cv2.INTER_CUBIC)
    #if debug:
    #    display(Image.fromarray(image))
    croped_images = get_croped_images(image)
    text_all = []
    for croped in croped_images:
        text = pytesseract.image_to_string(croped, lang='eng', config=custom_config)
        # if debug:
        #    display(Image.fromarray(croped))
        text = text.replace('\n', ' ')
        text = text.replace('\x0c', '')
        text = text.lower()
        text_all.append(text)
        # if debug:
        #    print(text)

    result = ''

    for i, word in enumerate(text_all):
        result += word
        if i != len(text_all) - 1:
            result += ''
    return result[:-1]




# load net
net = CRAFT()  # initialize

# Load weights
net.load_state_dict(copyStateDict(torch.load('ocr-api/model/craft_mlt_25k.pth', map_location=torch.device('cpu'))))

net = net.cpu()
net = torch.nn.DataParallel(net)
cudnn.benchmark = False

# Config
custom_config = r'--oem 1 --psm 8'

