import os

import torch
from torch import optim
from torch.optim import lr_scheduler
from torch.utils.data import DataLoader

from road_signs.Mapillary.dataset.MapillaryDatasetSiamese import MapillarySiamese
from road_signs.cnn.SiameseNet import SiameseNet
from road_signs.loss.ConstrastiveLoss import ContrastiveLoss
from road_signs.train.Siamese import train_epoch, test_epoch
from road_signs.train.fit import fit
from road_signs.utils.Const import *


if __name__ == '__main__':
    train_loader = DataLoader(MapillarySiamese(train=True), batch_size=BS, shuffle=True, pin_memory=bool(os.getenv('USE_LAB')))
    test_loader = DataLoader(MapillarySiamese(train=False), batch_size=BS, shuffle=True, pin_memory=bool(os.getenv('USE_LAB')))
    model = SiameseNet()
    loss_fn = ContrastiveLoss(margin=MARGIN)
    cuda = torch.cuda.is_available()
    optimizer = optim.Adam(model.parameters(), lr=INIT_LR)
    scheduler = lr_scheduler.StepLR(optimizer, step_size=STEP_SIZE, gamma=GAMMA)
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    model.to(device)
    loss_fn.to(device)

    fit(train_loader, test_loader, model, loss_fn, optimizer, scheduler, NUM_EPOCHS, cuda, train_epoch, test_epoch, 'siamese.txt')
    torch.save(model.state_dict(), '../../weigths/Mapillary/siamese.pth')
