# python -m datasets.Shanghai

import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from torch.utils.data import random_split, Subset
import random
import math
import torch
import h5py
import numpy as np
from torchvision import transforms 
from matplotlib import colors

import os
from config import config_root  # 导入全局配置

# data_path = os.path.join(config_root, "datasets", "Shanghai.pt")

data_path = os.path.join(config_root, "datasets", "shanghai.h5")

PIXEL_SCALE = 90.0

class Shanghai(Dataset):
    def __init__(self, data_path, img_size, type='train', trans=None, seq_len=-1):
        super().__init__()
        
        self.pixel_scale = PIXEL_SCALE
        
        self.data_path = data_path
        self.img_size = img_size

        assert type in ['train', 'test', 'val']
        self.type = type if type!='val' else 'test'
        with h5py.File(data_path,'r') as f:
            self.all_len = int(f[self.type]['all_len'][()]) 
        if trans is not None:
            self.transform = trans
        else:
            self.transform = transforms.Compose([
                        transforms.Resize((img_size, img_size)),
                    ])
                    
    def __len__(self):
        return self.all_len

    def sample(self):
        index = np.random.randint(0, self.all_len)
        return self.__getitem__(index)
    
    
    def __getitem__(self, index):

        with h5py.File(self.data_path,'r') as f:
            imgs = f[self.type][str(index)][()]   # numpy array: (25, 565, 784), dtype=uint8, range(0,70)
            frames = torch.from_numpy(imgs).float().squeeze() 
            frames = frames / 255.0
            frames = self.transform(frames)     
        return frames.unsqueeze(1) # (25,1,128,128)
 


COLOR_MAP = np.array([
    [0, 0, 0,0],
    [0, 236, 236, 255],
    [1, 160, 246, 255],
    [1, 0, 246, 255],
    [0, 239, 0, 255],
    [0, 200, 0, 255],
    [0, 144, 0, 255],
    [255, 255, 0, 255],
    [231, 192, 0, 255],
    [255, 144, 2, 255],
    [255, 0, 0, 255],
    [166, 0, 0, 255],
    [101, 0, 0, 255],
    [255, 0, 255, 255],
    [153, 85, 201, 255],
    [255, 255, 255, 255]
    ]) / 255

BOUNDS = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75, PIXEL_SCALE]
THRESHOLDS = [20, 30, 35, 40]

HMF_COLORS = np.array([
    [82, 82, 82],
    [252, 141, 89],
    [255, 255, 191],
    [145, 191, 219]
]) / 255

def gray2color(image, **kwargs):

    # 定义颜色映射和边界
    cmap = colors.ListedColormap(COLOR_MAP )
    bounds = BOUNDS
    norm = colors.BoundaryNorm(bounds, cmap.N)

    # 将图像进行染色
    colored_image = cmap(norm(image))

    return colored_image


class CustomShanghai(Shanghai):
    def __init__(self, base_dataset, indices):
        super().__init__(base_dataset.data_path, base_dataset.img_size, type=base_dataset.type)
        self.indices = indices

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        original_idx = self.indices[idx]
        return super().__getitem__(original_idx)
        

# data = torch.load(data_path).to(torch.float32)


full_dataset = Shanghai(data_path, 256, type='train')
all_indices = np.arange(len(full_dataset))
l = len(full_dataset)
train_end = math.floor(l * 0.6)
val_end = math.floor(l * 0.8)
data = [full_dataset[i] for i in range(len(full_dataset))]



# print(data.shape)
l = len(data)
train_end = math.floor(l * 0.7)
val_end = math.floor(l * 0.85)
train_dataset = data[:train_end]
val_dataset = data[train_end:val_end]
test_dataset = data[val_end:]
