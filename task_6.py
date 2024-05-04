import torch
from torch import nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import numpy as np

# reshape输入为28*28的图像
class Reshape(nn.Module):
    def forward(self, x):
        return x.view(-1, 1, 28, 28)


# 定义网络
net = nn.Sequential(Reshape(), nn.Conv2d(1, 6, kernel_size=7, padding=3), nn.Sigmoid(),
                    nn.MaxPool2d(kernel_size=2, stride=2),
                    nn.Conv2d(6, 16, kernel_size=5), nn.Sigmoid(),
                    nn.MaxPool2d(kernel_size=2, stride=2),
                    nn.Flatten(),
                    nn.Linear(16*5*5, 120), nn.Sigmoid(),
                    nn.Linear(120, 84), nn.Sigmoid(),
                    nn.Linear(84, 10))

# 下载并配置数据集
train_dataset = datasets.MNIST(root='./dataset', train=True,
                               transform=transforms.ToTensor(), download=True)
test_dataset = datasets.MNIST(root='./dataset', train=False,
                              transform=transforms.ToTensor(), download=True)

# 配置数据加载器
batch_size = 64
train_loader = DataLoader(dataset=train_dataset,
                          batch_size=batch_size, shuffle=True)
test_loader = DataLoader(dataset=test_dataset,
                         batch_size=batch_size, shuffle=True)

# 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(net.parameters())
net.to(device='cuda')
estimation = []
all_loss = []

def train(epochs):
    # 训练模型
    for epoch in range(epochs):
        sum_loss = 0
        for i, (images, labels) in enumerate(train_loader):
            images = images.cuda()
            labels = labels.cuda()
            outputs = net(images)
            loss = criterion(outputs, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            
            if i % 50 == 0:
                sum_loss += loss.item()
                # print(
                #     f'Epoch: {epoch + 1}, Step: {i + 1}, Loss: {loss.item():.4f}')
        print(f'Loss: {sum_loss:.4f}')
        all_loss.append(sum_loss)
        
        correct = 0
        total = 0
        for images, labels in test_loader:
            images = images.cuda()
            labels = labels.cuda()
            outputs = net(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        estimation.append(correct/total)
        print(f'Accuracy: {correct / total * 100:.2f}%')

    # 保存模型
    torch.save(net.state_dict(),
               f"./model/LeNet_Epoch{epochs}_Accuracy{correct / total * 100:.2f}%.pth") 
    # 绘制图形
    # plt.plot(list(range(1,epochs+1)), all_loss)
    # plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.ylabel('loss')
    # plt.xlabel('epoch')
    # plt.savefig('result/kernal5/train_loss_epoch{}_kernal5.jpg'.format(epochs))
    # plt.show()
    
    # plt.plot(list(range(1,epochs+1)), estimation)
    # plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.ylabel('estimation')
    # plt.xlabel('epoch')
    # plt.savefig('result/kernal5/test_estimation_epoch{}_kernal5.jpg'.format(epochs))
    # plt.show()
    
if __name__ == '__main__' :
    train(epochs=20) 