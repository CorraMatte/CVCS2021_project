import torch
import os
from torch import optim
from torch.optim import lr_scheduler
from torch.utils.data import DataLoader
from torch.nn import TripletMarginWithDistanceLoss, PairwiseDistance
from road_signs.cnn.TripletNet import TripletNet
from road_signs.Unknown.dataset.UnknownDatasetTripletOnline import UnknownDatasetTriplet
from road_signs.utils.Const import *
from road_signs.train.Triplet import train_epoch, test_epoch
from road_signs.train.fit import fit


if __name__ == '__main__':
    train_loader = DataLoader(UnknownDatasetTriplet(train=True), batch_size=BS, shuffle=True, pin_memory=bool(os.getenv('USE_LAB')))
    test_loader = DataLoader(UnknownDatasetTriplet(train=False), batch_size=BS, shuffle=True, pin_memory=bool(os.getenv('USE_LAB')))

    model = TripletNet()
    loss_fn = TripletMarginWithDistanceLoss(distance_function=PairwiseDistance(), margin=MARGIN)
    cuda = torch.cuda.is_available()
    optimizer = optim.Adam(model.parameters(), lr=INIT_LR)
    scheduler = lr_scheduler.StepLR(optimizer, 8, gamma=0.1, last_epoch=-1)
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    model.to(device)
    loss_fn.to(device)

    fit(train_loader, test_loader, model, loss_fn, optimizer, scheduler, NUM_EPOCHS, cuda, train_epoch, test_epoch, 'triplet.txt')
    torch.save(model.state_dict(), '../../weights/Unknown/triplet.pth')
