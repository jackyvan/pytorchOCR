#-*- coding:utf-8 _*-
"""
@author:fxw
@file: util_function.py
@time: 2020/08/07
"""
import os
import importlib
import math
import cv2
import torch
import numpy as np

def create_module(module_str):
    tmpss = module_str.split(",")
    assert len(tmpss) == 2, "Error formate\
        of the module path: {}".format(module_str)
    module_name, function_name = tmpss[0], tmpss[1]
    somemodule = importlib.import_module(module_name, __package__)
    function = getattr(somemodule, function_name)
    return function


def resize_image(img,algorithm,side_len=736,stride = 128):
    if algorithm == 'DB' or algorithm == 'PAN' or algorithm == 'CRNN':
        height, width, _ = img.shape
        if height < width:
            new_height = side_len
            new_width = int(math.ceil(new_height / height * width / stride) * stride)
        else:
            new_width = side_len
            new_height = int(math.ceil(new_width / width * height / stride) * stride)
        resized_img = cv2.resize(img, (new_width, new_height))
    else:
        height, width, _ = img.shape
        if height > width:
            new_height = side_len
            new_width = int(math.ceil(new_height / height * width / stride) * stride)
        else:
            new_width = side_len
            new_height = int(math.ceil(new_width / width * height / stride) * stride)
        resized_img = cv2.resize(img, (new_width, new_height))
    return  resized_img


def save_checkpoint(state, checkpoint='checkpoint', filename='model.pth.tar'):
    filepath = os.path.join(checkpoint, filename)
    torch.save(state, filepath)

class LossAccumulator():
    def __init__(self):
        super(LossAccumulator,self).__init__()
        self.loss_items = []
    def loss_add(self,loss):
        self.loss_items.append(loss)
    def loss_sum(self):
        return sum(self.loss_items)
    def loss_mean(self):
        return sum(self.loss_items)/len(self.loss_items)
    def loss_clear(self):
        self.loss_items = []

def create_process_obj(algorithm,pred):
    if(algorithm=='DB'):
        return pred.cpu().numpy()
    elif(algorithm=='SAST'):
        pred['f_score'] = pred['f_score'].cpu().numpy()
        pred['f_border'] = pred['f_border'].cpu().numpy()
        pred['f_tvo'] = pred['f_tvo'].cpu().numpy()
        pred['f_tco'] = pred['f_tco'].cpu().numpy()
        return pred
    else:
        return pred


def create_loss_bin(algorithm):
    bin_dict = {}
    if(algorithm=='DB'):
        keys = ['loss_total','loss_l1', 'loss_bce', 'loss_thresh']
    elif(algorithm=='PSE'):
        keys = ['loss_total','loss_kernel', 'loss_text']
    elif(algorithm=='PAN'):
        keys = ['loss_total','loss_text', 'loss_agg', 'loss_kernel', 'loss_dis']
    elif (algorithm == 'SAST'):
        keys = ['loss_total', 'loss_score', 'loss_border', 'loss_tvo', 'loss_tco']
    elif (algorithm == 'CRNN'):
        keys = ['loss_ctc']
    else:
        assert 1==2,'only support algorithm DB,SAST,PSE,PAN,CRNN !!!'

    for key in keys:
        bin_dict[key] = LossAccumulator()
    return bin_dict

def set_seed(seed):
    import numpy as np
    import random
    import torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def create_dir(path):
    if not (os.path.exists(path)):
        os.mkdir(path)

def load_model(model,model_path):
    if torch.cuda.is_available():
        model_dict = torch.load(model_path)['state_dict']
    else:
        model_dict = torch.load(model_path,map_location='cpu')['state_dict']
    try:
        model.load_state_dict(model_dict)
    except:
        state = model.state_dict()
        for key in state.keys():
            state[key] = model_dict['module.' + key]
        model.load_state_dict(state)
    return model
