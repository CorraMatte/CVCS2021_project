import os

import cv2
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision.transforms import ToTensor
from pycocotools.coco import COCO
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

ANNOTATION_PATH = os.getenv('ANNOTATION_PATH')
IMAGES_PATH = os.getenv('IMAGES_PATH')


# collate_fn needs for batch
def collate_fn(batch):
    return tuple(zip(*batch))


class CocoPedestrianDataset(Dataset):
    def __init__(self, root, annotation, transforms=None):
        self.root = root
        self.transforms = transforms
        self.coco = COCO(annotation)
        # self.catIds = coco.getCatIds(catNms=['person'])
        # self.imgIds = coco.getImgIds(catIds=self.catIds)
        # self.ids = list(sorted(self.coco.imgs.keys()))
        self.ids = list(sorted(self.coco.getImgIds(catIds=self.coco.getCatIds(catNms=['person']))))

    def __len__(self):
        # Contare immagini solo dove sono presenti pedoni
        return len(self.ids)

    def __getitem__(self, index):
        coco = self.coco
        # Image ID
        img_id = self.ids[index]
        # List: get annotation id from coco
        ann_ids = coco.getAnnIds(imgIds=img_id)
        # Dictionary: target coco_annotation file for an image
        coco_annotation = coco.loadAnns(ann_ids)
        # path for input image
        path = coco.loadImgs(img_id)[0]['file_name']
        # open the input image
        img = Image.open(os.path.join(self.root, path))

        # number of objects in the image
        num_objs = len(coco_annotation)

        # Bounding boxes for objects
        # In coco format, bbox = [xmin, ymin, width, height]
        # In pytorch, the input should be [xmin, ymin, xmax, ymax]
        boxes = []
        for i in range(num_objs):
            xmin = coco_annotation[i]['bbox'][0]
            ymin = coco_annotation[i]['bbox'][1]
            xmax = xmin + coco_annotation[i]['bbox'][2]
            ymax = ymin + coco_annotation[i]['bbox'][3]
            boxes.append([xmin, ymin, xmax, ymax])
        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        # Labels (In my case, I only one class: target class or background)
        labels = torch.ones((num_objs,), dtype=torch.int64)
        # Tensorise img_id
        img_id = torch.tensor([img_id])
        # Size of bbox (Rectangular)
        areas = []
        for i in range(num_objs):
            areas.append(coco_annotation[i]['area'])
        areas = torch.as_tensor(areas, dtype=torch.float32)
        # Iscrowd
        iscrowd = torch.zeros((num_objs,), dtype=torch.int64)

        # Annotation is in dictionary format
        my_annotation = dict()
        my_annotation["boxes"] = boxes
        my_annotation["labels"] = labels
        my_annotation["image_id"] = img_id
        my_annotation["area"] = areas
        my_annotation["iscrowd"] = iscrowd

        if self.transforms is not None:
            img = self.transforms(img)

        return img, my_annotation


def main():
    train_data_dir = IMAGES_PATH
    train_coco = ANNOTATION_PATH

    # create own Dataset
    my_dataset = CocoPedestrianDataset(root=train_data_dir, annotation=train_coco)

    # Batch size
    train_batch_size = 1

    # own DataLoader
    data_loader = torch.utils.data.DataLoader(my_dataset,
                                              batch_size=train_batch_size,
                                              shuffle=True,
                                              num_workers=1,
                                              collate_fn=collate_fn)

    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    # DataLoader is iterable over Dataset
    for imgs, annotations in data_loader:
        imgs = list(ToTensor()(img).to(device) for img in imgs)
        annotations = [{k: v.to(device) for k, v in t.items()} for t in annotations]
        for img in imgs:
            shape = img.shape
            print(shape)
            plt.imshow(img.reshape(shape[1], shape[2], shape[0]))
        # plt.show()

        # print(annotations)


if __name__ == '__main__':
    main()
