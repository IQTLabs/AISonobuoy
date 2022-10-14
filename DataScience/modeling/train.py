import os
from time import time
import argparse
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import logging
import sys

import torchmetrics
from torchvision.models import resnet18, ResNet18_Weights
from torch.utils.tensorboard import SummaryWriter

from dataset import BoatDataset


def logging_config():
    tensorboard_writer = SummaryWriter()
    return logging.basicConfig(filename="custom.log"), tensorboard_writer


def parse_cli():
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


def visualize_batch():
    pass


def create_data_loader(data_dir, classes, batch_size, is_training, num_workers):
    shuffle = not is_training
    tugboat_ds = BoatDataset(data_dir=data_dir, class_dir_names=classes)

    return DataLoader(
        tugboat_ds,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        drop_last=True,
    )


def save_stats(out_dir, value, out_file):
    with open(os.path.join(out_dir, out_file), "a") as out_write:
        out_write.write(str(value) + "\n")


def train_epoch(
    train_data_loader, model, loss_func, optimizer, tensorboard_writer, epoch
):
    model.train()
    loss_ls = []
    for X, y in train_data_loader:
        X, y = X.cuda(), y.cuda()
        optimizer.zero_grad()
        logits = model(X)
        loss = loss_func(logits, y)
        tensorboard_writer.add_scalar("Loss/train", loss, epoch)
        loss.backward()
        optimizer.step()
        loss = loss.mean()
        loss_ls.append(loss.item())
    return np.vstack(loss_ls).mean()


@torch.no_grad()
def eval_func(
    test_data_loader, model, loss_func, metric_func, tensorboard_writer, epoch
):
    model.eval()
    preds = []
    gt = []
    loss_ls = []
    for X, y in test_data_loader:
        X, y = X.cuda(), y.cuda()
        logits = model(X)
        _, preds_ = torch.max(logits, 1)
        _, gt_ = torch.max(y, 1)
        loss = loss_func(logits, y)
        tensorboard_writer.add_scalar("Loss/val", loss, epoch)
        loss_ls.append(loss)
        preds.append(preds_.type(torch.int32).cpu())
        gt.append(gt_.type(torch.int32).cpu())
    metric = metric_func(torch.cat(preds), torch.cat(gt))
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
    best_loss = np.float32(sys.maxsize)
    for epoch in range(epochs):
        start_time = time()
        train_loss = train_epoch(
            train_data_loader, model, loss_func, optimizer, tensorboard_writer, epoch
        )
        eval_loss, eval_metric = eval_func(
            test_data_loader, model, loss_func, metric_func, tensorboard_writer, epoch
        )
        scheduler.step()

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

        save_stats(out_dir, train_loss, "train_loss.txt")
        save_stats(out_dir, eval_loss, "eval_loss.txt")
        save_stats(out_dir, eval_metric, "eval_metric.txt")

        tensorboard_writer.flush()

    return {
        "epoch": epochs,
        "train_loss": train_loss,
        "eval_loss": eval_loss,
        "eval_metric": eval_metric.item(),
    }


if __name__ == "__main__":
    logge, tensorboard_writer = logging_config()
    args = parse_cli()

    os.makedirs(args.out_dir, exist_ok=True)
    torch.manual_seed(1)

    classes = args.class_dirs.split(" ")

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

    print("TRAIN DATALOADER LENGTH", len(train_data_loader))
    print("TEST DATALOADER LENGTH", len(test_data_loader))

    assert len(train_data_loader) > 1
    assert len(test_data_loader) > 1
    # TODO: add validation step (in seperate script)

    model = resnet18(weights=ResNet18_Weights.DEFAULT)
    # model = resnet18()
    num_features = model.fc.in_features
    print("NUM FEATURES", num_features)
    # model.fc = nn.Linear(num_features, len(classes))
    model.fc = nn.Sequential(nn.Linear(num_features, len(classes))).cuda()
    model.cuda()
    # for param in model.parameters():
    #     param.requires_grad = True
    print("Model size:", sum(p.numel() for p in model.parameters()), "parameters")
    # print(model)

    loss_func = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        params=model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay
    )
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=1000, gamma=0.1)
    metric_func = torchmetrics.F1Score(num_classes=2)

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

    tensorboard_writer.close()

    torch.save(
        {"model_state_dict": model.state_dict(), **results_dict},
        os.path.join(args.out_dir, "last.pt"),
    )
