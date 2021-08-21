import os
import cv2
from torch.utils.data import Dataset
from torch.utils.data.dataset import T_co
from torchvision import transforms
import xml.etree.ElementTree as ET


BASE_DIR_LOCAL = '/home/corra/Desktop/Unknown'
BASE_DIR_LAB = '/nas/softechict-nas-3/mcorradini/Unknown'
TRANSFORMS = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])
CLASSES = ['trafficlight', 'speedlimit', 'crosswalk', 'stop']


class UnknownDatasetAbs(Dataset):
    def __init__(self, train=True, trans=None):
        self.base_dir = BASE_DIR_LOCAL if os.getenv('IS_LOCAL') else BASE_DIR_LAB
        self.transform = trans if trans else TRANSFORMS
        self.train = train
        self.classes = 4
        self.labels = []
        self.BASE_ANNOTATION_DIR = os.path.join(self.base_dir, 'annotations')
        self.BASE_IMAGES_DIR = os.path.join(self.base_dir, 'images')

        for index, f in enumerate(os.listdir(self.BASE_ANNOTATION_DIR)):
            if (not train and index % 5 == 0) or train:
                ann_doc = ET.parse(os.path.join(self.BASE_ANNOTATION_DIR, f)).getroot()
                self.labels.append({
                    'path': os.path.join(self.BASE_IMAGES_DIR, ann_doc.find("./filename").text),
                    'label': ann_doc.find("./object/name").text,
                    'size': {
                        'width': ann_doc.find("./size/width").text,
                        'height': ann_doc.find("./size/height").text
                    },
                    'bbox': {
                        'xmin': int(ann_doc.find("./object/bndbox/xmin").text),
                        'ymin': int(ann_doc.find("./object/bndbox/ymin").text),
                        'xmax': int(ann_doc.find("./object/bndbox/xmax").text),
                        'ymax': int(ann_doc.find("./object/bndbox/ymax").text)
                    }
                })

    def __len__(self):
        return len(self.labels)

    def read_image(self, img):
        img_path = os.path.join(self.base_dir, img['path'])
        bb = img['bbox']
        image = transforms.ToTensor()(cv2.imread(img_path)[:, :, :3])
        image = image[:, int(bb['ymin']):int(bb['ymax']), int(bb['xmin']):int(bb['xmax'])].float()
        return image

    def __getitem__(self, index) -> T_co:
        raise NotImplementedError
