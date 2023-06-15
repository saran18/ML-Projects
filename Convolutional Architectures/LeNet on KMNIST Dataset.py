# -*- coding: utf-8 -*-
"""KMNIST_using_LeNet.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1arJUzm_CwjUHHj-UiUeGDsM86dkvLJT7
"""

import numpy as np
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms

batch_size = 32
num_classes = 10
learning_rate = 0.001
num_epochs = 20

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

all_transforms = transforms.Compose([transforms.Resize((28,28)),
                                     transforms.ToTensor(),
                                     transforms.Normalize((0.1307,), (0.3081,))
                                     ])
# Create Training dataset
train_dataset = torchvision.datasets.KMNIST(root = './data',
                                             train = True,
                                             transform = all_transforms,
                                             download = True)

# Create Testing dataset
test_dataset = torchvision.datasets.KMNIST(root = './data',
                                            train = False,
                                            transform = all_transforms,
                                            download=True)

# Instantiate loader objects to facilitate processing
train_loader = torch.utils.data.DataLoader(dataset = train_dataset,
                                           batch_size = batch_size,
                                           shuffle = True)


test_loader = torch.utils.data.DataLoader(dataset = test_dataset,
                                           batch_size = batch_size,
                                           shuffle = True)

# # Viewing the batches
# examples = enumerate(train_loader)
# batch_idx, (example_data, example_targets) = next(examples)

# # A single batch of dimensions (32,1,28,28)
# # ith image of the batch -> example_data[i-1][0] -> (28,28)
# example_data[0][0].shape

# fig = plt.figure()
# for i in range(6):
#   plt.subplot(2,3,i+1)
#   plt.tight_layout()
#   plt.imshow(example_data[i][0], cmap='gray', interpolation='none')
#   plt.title("Ground Truth: {}".format(example_targets[i]))
#   plt.xticks([])
#   plt.yticks([])
# fig

class LeNet(nn.Module):
  def __init__(self, num_classes):
    super(LeNet, self).__init__()
    self.conv1 = nn.Conv2d(in_channels=1, out_channels = 6, kernel_size = 5, padding='valid')
    self.mp1 = nn.MaxPool2d(kernel_size = 2, stride = 2)
    self.conv2 = nn.Conv2d(in_channels = 6, out_channels = 16, kernel_size = 5, padding='valid')
    self.mp2 = nn.MaxPool2d(kernel_size = 2, stride = 2)
    self.flatten = nn.Flatten()
    self.fc1 = nn.Linear(256, 120)
    self.fc2 = nn.Linear(120, 84)
    self.fc3 = nn.Linear(84, num_classes)

  def forward(self, x):
    out = self.conv1(x)
    out = self.mp1(out)

    out = self.conv2(out)
    out = self.mp2(out)

    out = self.flatten(out)
    out = self.fc1(out)
    out = self.fc2(out)
    out = self.fc3(out)

    return out

model = LeNet(num_classes)
if torch.cuda.is_available():
    model.cuda()
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, weight_decay = 0.005, momentum = 0.9)

for epoch in range(num_epochs):
    for i, (images, labels) in enumerate(train_loader):  
        images = images.to(device)
        labels = labels.to(device)
        
        # Forward pass
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        # Backward and optimize
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print('Epoch [{}/{}], Loss: {:.4f}'.format(epoch+1, num_epochs, loss.item()))

# Saving checkpoint
PATH = "model.pt"

torch.save(model.state_dict(), PATH)

# Loading Checkpoint
# model = LeNet(num_classes)
# model.load_state_dict(torch.load(PATH))
# if torch.cuda.is_available():
#   model.cuda()

# model.train()

def check_accuracy(loader, model):
    num_correct = 0
    num_samples = 0
    model.eval()
    
    with torch.no_grad():
        for x, y in loader:
            x = x.to(device=device)
            y = y.to(device=device)
            
            scores = model(x)
            _, predictions = scores.max(1)
            num_correct += (predictions == y).sum()
            num_samples += predictions.size(0)
        
        print(f'Got {num_correct} / {num_samples} with accuracy {float(num_correct)/float(num_samples)*100:.2f}') 
    
    model.train()

check_accuracy(test_loader, model)