# file/system manipulation
import os
import sys
import argparse

# logging utilities
import logging
from time import time
from torch.utils.tensorboard import SummaryWriter

# data manipulation
import numpy as np
import torch
from torch.utils.data import DataLoader

# modeling
import torchmetrics
import torch.nn as nn
import torch.optim as optim
from torchvision.models import resnet18, ResNet18_Weights

# dataset from dataset.py
from dataset import BoatDataset


def logging_config():
    """initalize logging

    Returns:
        logging.basicConfig: Python logging module configuration settings
        tensorboard.SummaryWriter: Tensorboard model training configuration
    """
    # initalize various logging classes
    tensorboard_writer = SummaryWriter()
    return logging.basicConfig(filename="custom.log"), tensorboard_writer


def parse_cli():
    """command line interface parser to simplify model training kickoff

    Returns:
        argparse.ArgumentParser().parse_args: trigger argument parsing
    """
    # specify parser arguments and thier descriptions + defaults
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--epochs", type=int, default=100, help="number of training epochs"
    )
    parser.add_argument(
        "--batch-size", type=int, default=18, help="size of training batch"
    )
    parser.add_argument(
        "--data-dir-train",
        type=str,
        default="",
        help="path to directory of train data assets",
    )
    parser.add_argument(
        "--data-dir-test",
        type=str,
        default="",
        help="path to directory of test data assets",
    )
    parser.add_argument(
        "--data-dir-val",
        type=str,
        default="",
        help="path to directory of validation data assets",
    )
    parser.add_argument(
        "--class-dirs",
        type=str,
        default="",
        help="space delimited string of class directory names",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default=os.path.join("", str(time()).split(".")[0]),
        help="default directory to save training outputs",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=1e-3,
        help="learning rate step of optimizer",
    )
    parser.add_argument(
        "--weight-decay",
        type=float,
        default=1e-3,
        help="weight decay regularization of optimizer",
    )
    parser.add_argument(
        "--num-workers",
        type=int,
        default=4,
        help="number of CPU threads for data loading",
    )
    parser.add_argument(
        "--is-training",
        type=bool,
        default=False,
        help="True if running inference, else False",
    )

    return parser.parse_args()


def create_data_loader(data_dir, classes, batch_size, is_training, num_workers):
    """create data loader for a PyTorch Dataset

    Args:
        data_dir (str): file path to dataset
        classes (str): space delimited string of classnames
        batch_size (int): size of training batch (dictated my system memory)
        is_training (bool): boolean that dictates wether or not to shuffle dataset
        num_workers (int): number of threads for data loading

    Returns:
        torch.utils.data.DataLoader: PyTorch DataLoader that serves up data for training
    """
    # if evaluating, order matters, otherwise shuffle such that order does not influence learning
    shuffle = not is_training
    # load dataset
    tugboat_ds = BoatDataset(data_dir=data_dir, class_dir_names=classes)

    # create PyTorch dataloader where last incomplete batch is dropped
    return DataLoader(
        tugboat_ds,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        drop_last=True,
    )


def save_stats(out_dir, value, out_file):
    """manual logging of values for posterity

    Args:
        out_dir (str): out data directory to save manual log files to
        value (float): value to write
        out_file (str): specific filename to write to
    """
    # opens file in append mode and writes logging-data-of-interest
    with open(os.path.join(out_dir, out_file), "a") as out_write:
        out_write.write(str(value) + "\n")


def train_epoch(
    train_data_loader, model, loss_func, optimizer, tensorboard_writer, epoch
):
    """implements within-epoch training step

    Args:
        train_data_loader (torch.utils.data.DataLoader): PyTorch DataLoader for serving up training feature-label pairs
        model (torchvision.models.resnet18): ResNet-18 model for training
        loss_func (torch.nn.CrossEntropyLoss): torch loss function for dictating loss landscape and location within it
        optimizer (torch.optim.Adam): torch optimizer for dictating step size and direction in loss landscape
        tensorboard_writer (tensorboard.SummaryWriter): logging and plotting various learning metrics
        epoch (int): epoch number for logging

    Returns:
        np.ndarray: numpy array of training loss for logging (0-dim array with scalar)
    """
    # switch to traning mode
    model.train()
    loss_ls = []
    # load feature-label pairs into memory
    for X, y in train_data_loader:
        # send to GPU
        X, y = X.cuda(), y.cuda()
        # reset gradients
        optimizer.zero_grad()
        # perform forward pass
        logits = model(X)
        # evaluate loss + compute gradients
        loss = loss_func(logits, y)
        # log loss value
        tensorboard_writer.add_scalar("Loss/train", loss, epoch)
        # backpropogate
        loss.backward()
        # step in computed direction + step size in loss landscape
        optimizer.step()
        # save loss for logging
        loss = loss.mean()
        loss_ls.append(loss.item())
    return np.vstack(loss_ls).mean()


@torch.no_grad()
def eval_func(
    test_data_loader, model, loss_func, metric_func, tensorboard_writer, epoch
):
    """implements within-epoch evaluation

    Args:
        test_data_loader (torch.utils.data.DataLoader): PyTorch DataLoader for serving up test feature-label pairs
        model (torchvision.models.resnet18): ResNet-18 model for training
        loss_func (torch.nn.CrossEntropyLoss): torch loss function for dictating loss landscape and location within it
        metric_func (torchmetrics.F1Score): metric function to judge training task performance
        tensorboard_writer (tensorboard.SummaryWriter): logging and plotting various learning metrics
        epoch (int): epoch number for logging

    Returns:
        torch.tensor: torch tensor of evaluation loss for logging (0-dim tensor with scalar)
        torch.tensor: torch tensor of task performance metric for logging (0-dim array with scalar)
    """
    # switch to evaluation mode
    model.eval()
    preds = []
    gt = []
    loss_ls = []
    # load feature-label pairs into memory
    for X, y in test_data_loader:
        # send to GPU
        X, y = X.cuda(), y.cuda()
        # get model guess
        logits = model(X)
        # post-process guess
        _, preds_ = torch.max(logits, 1)
        _, gt_ = torch.max(y, 1)
        # compute evaluation loss to compare with training loss
        loss = loss_func(logits, y)
        # log loss value
        tensorboard_writer.add_scalar("Loss/val", loss, epoch)
        # save guesses and loss values
        loss_ls.append(loss)
        preds.append(preds_.type(torch.int32).cpu())
        gt.append(gt_.type(torch.int32).cpu())
    # compute task performace metric
    metric = metric_func(torch.cat(preds), torch.cat(gt))
    # log task performance metric
    tensorboard_writer.add_scalar("Metric/f1", metric, epoch)
    return torch.vstack(loss_ls).mean().item(), metric


def train_loop(
    train_data_loader,
    test_data_loader,
    epochs,
    model,
    loss_func,
    optimizer,
    out_dir,
    scheduler,
    metric_func,
    tensorboard_writer,
):
    """model training driver function

    Args:
        train_data_loader (torch.utils.data.DataLoader): PyTorch DataLoader for serving up training feature-label pairs
        test_data_loader (torch.utils.data.DataLoader): PyTorch DataLoader for serving up test feature-label pairs
        epochs (int): number of epochs to train for
        model (torchvision.models.resnet18): ResNet-18 model for training
        loss_func (torch.nn.CrossEntropyLoss): torch loss function for dictating loss landscape and location within it
        optimizer (torch.optim.Adam): torch optimizer for dictating step size and direction in loss landscape
        out_dir (str): file path to out directory to save model checkpoints and manual logs to
        scheduler (optim.lr_scheduler.StepLR): leanring rate scheduler to increment/decrement learning rate
        metric_func (torchmetrics.F1Score): metric function to judge training task performance
        tensorboard_writer (tensorboard.SummaryWriter): logging and plotting various learning metrics

    Returns:
        dict: dictionary of various final summary metrics
    """
    # C-style find minimum initalization
    best_loss = np.float32(sys.maxsize)
    # epoch training + evaluation
    for epoch in range(epochs):
        start_time = time()
        # execute epoch training
        train_loss = train_epoch(
            train_data_loader, model, loss_func, optimizer, tensorboard_writer, epoch
        )
        # execute epoch evaluation
        eval_loss, eval_metric = eval_func(
            test_data_loader, model, loss_func, metric_func, tensorboard_writer, epoch
        )
        # step learning rate scheduler
        scheduler.step()

        # save model checkpoint if evaluation loss improves
        if eval_loss < best_loss:
            best_loss = eval_loss
            best_dict = {
                "epoch": epochs,
                "train_loss": train_loss,
                "eval_loss": eval_loss,
                "eval_metric": eval_metric.item(),
                "model_state_dict": model.state_dict(),
            }
            torch.save(best_dict, os.path.join(out_dir, "best.pt"))

        # log some informaiton to the console
        print(
            "Epoch #",
            epoch,
            ":",
            "Train loss:",
            train_loss,
            "Val loss:",
            eval_loss,
            "Val metric:",
            eval_metric.item(),
        )
        print("Epoch Time:", str(time() - start_time))

        # manually save some information for posterity
        save_stats(out_dir, train_loss, "train_loss.txt")
        save_stats(out_dir, eval_loss, "eval_loss.txt")
        save_stats(out_dir, eval_metric, "eval_metric.txt")

        # push all values to tensorboard session
        tensorboard_writer.flush()

    return {
        "epoch": epochs,
        "train_loss": train_loss,
        "eval_loss": eval_loss,
        "eval_metric": eval_metric.item(),
    }


if __name__ == "__main__":
    """training driver code"""
    # initalize various utilities
    logger, tensorboard_writer = logging_config()
    args = parse_cli()
    os.makedirs(args.out_dir, exist_ok=True)
    torch.manual_seed(1)
    classes = args.class_dirs.split(" ")

    # create DataLoaders
    train_data_loader = create_data_loader(
        data_dir=args.data_dir_train,
        classes=classes,
        batch_size=args.batch_size,
        is_training=args.is_training,
        num_workers=args.num_workers,
    )

    test_data_loader = create_data_loader(
        data_dir=args.data_dir_test,
        classes=classes,
        batch_size=args.batch_size,
        is_training=args.is_training,
        num_workers=args.num_workers,
    )

    # log size to console
    print("TRAIN DATALOADER LENGTH:", len(train_data_loader))
    print("TEST DATALOADER LENGTH:", len(test_data_loader))

    # initalize pre-trained model
    model = resnet18(weights=ResNet18_Weights.DEFAULT)

    # add classifier layer
    num_features = model.fc.in_features
    model.fc = nn.Sequential(nn.Linear(num_features, len(classes))).cuda()
    # send model to GPU
    model.cuda()

    # log model parameters to train to console
    print("MODEL SIZE:", sum(p.numel() for p in model.parameters()), "parameters")

    # initalize loss function, optimizer, learning-rate scheduler, and task metric
    loss_func = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        params=model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay
    )
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=1000, gamma=0.1)
    metric_func = torchmetrics.F1Score(num_classes=2)

    # execute training
    results_dict = train_loop(
        train_data_loader,
        test_data_loader,
        args.epochs,
        model,
        loss_func,
        optimizer,
        args.out_dir,
        scheduler,
        metric_func,
        tensorboard_writer,
    )

    # gracefully exit tensorboard
    tensorboard_writer.close()

    # save final model checkpoint
    torch.save(
        {"model_state_dict": model.state_dict(), **results_dict},
        os.path.join(args.out_dir, "last.pt"),
    )
