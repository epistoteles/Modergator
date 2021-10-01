from PIL import Image
import cv2
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from operator import itemgetter

def show_img(img_list: list, size=(10,5)):
    plt.figure(figsize=size)
    plt.imshow(img_list)
    plt.show()

def load_img(path: str) -> list:
    img_list_bgr = cv2.imread(path)
    img_list_rbg = cv2.cvtColor(img_list_bgr, cv2.COLOR_BGR2RGB)
    return img_list_rbg 

# get rgb mean of edge colors of an image
def get_edge_colors(image: list) -> int:
    
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
                append_colors(x,y)
            elif y == 0 or y == image.height:
                append_colors(x,y)
                
    result_df = pd.DataFrame(edge_colors)

    r_mean = result_df.r.mean()
    g_mean = result_df.g.mean()
    b_mean = result_df.b.mean()
    total_mean = np.mean([r_mean, g_mean, b_mean])
    
    return total_mean

def crop_images(bounding_boxes: np.ndarray, img_list: list) -> list:
    
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
        
    def get_font_color(all_mean_edge_colors: int) -> str:
        
        if all_mean_edge_colors < 50:
            font_color = 'white'
        elif all_mean_edge_colors > 200:
            font_color = 'black'
        else:
            font_color = 'white'
        return font_color
    
    def handle_negatives(x,y):
        if x<0:
            x = 0
        if y<0:
            y = 0
        return x,y
    
    def sort_bounding_boxes(bounding_boxes: np.ndarray) -> list:
        
        coordinates = []
        for box in bounding_boxes:
            rect = cv2.boundingRect(box)
            x,y,w,h = rect
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
                        pts['h'] =  pts['h'] + abs(diff)
                    pts['y'] = y_cluster_min_all[cluster] 
                    
        coordinates = sorted(coordinates,key=itemgetter('y','x'))
        
        return coordinates
        
    coordinates = sort_bounding_boxes(bounding_boxes)
    
    croped_images = []
    total_mean_edge_colors_all = []
    
    for pts in coordinates:
        x,y,w,h = pts['x'], pts['y'], pts['w'], pts['h']
        x,y = handle_negatives(x,y)
        croped = img_list[y:y+h, x:x+w].copy()
        total_mean_edge_colors = get_edge_colors(croped)
        total_mean_edge_colors_all.append(total_mean_edge_colors)            
        th, croped = cv2.threshold(croped, 200, 255, cv2.THRESH_BINARY_INV)
        croped_images.append(croped)
    
    all_mean_edge_colors = np.mean(total_mean_edge_colors_all)
    
    font_color = get_font_color(all_mean_edge_colors)
    
    for i in range(len(croped_images)):
        if font_color == 'black':
            croped_images[i] = cv2.bitwise_not(croped_images[i])
            
    return croped_images, font_color, all_mean_edge_colors, total_mean_edge_colors_all
    
    
