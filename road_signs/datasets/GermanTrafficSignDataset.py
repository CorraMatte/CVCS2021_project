import os
from road_signs.datasets.GermanTrafficSignDatasetAbs import GermanTrafficSignDatasetAbs


class GermanTrafficSignDataset(GermanTrafficSignDatasetAbs):
    def __init__(self, train=True, trans=None):
        super().__init__(train, trans)

    def __len__(self):
        return len(self.img_labels)

    def __getitem__(self, index):
        item = self.img_labels.iloc[index]
        return self.transform(self.format_image(os.path.join(self.base_dir, item.Path))), item.ClassId
