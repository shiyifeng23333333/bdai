import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt


class TorchModel(nn.Module):
    def __init__(self, input_size,hide_size,output_size):
        super(TorchModel, self).__init__()
        self.linear1 = nn.Linear(input_size, hide_size)  # 线性层
        self.linear2 = nn.Linear(hide_size, output_size)  # 线性层
        self.activation1 = nn.functional.sigmoid  # sigmoid归一化函数
        self.activation2 = nn.functional.softmax  # softmax归一化函数
        self.loss = nn.functional.cross_entropy  # loss函数采用交叉熵损失

    # 当输入真实标签，返回loss值；无真实标签，返回预测值
    def forward(self, x, y=None):
        x = self.linear1(x)  # (batch_size, input_size) -> (batch_size, hide_size)
        x = self.activation1(x)  # (batch_size, hide_size) -> (batch_size, hide_size)
        x = self.linear2(x)  # (batch_size, hide_size) -> (batch_size, output_size)
        y_pred = self.activation2(x)  # (batch_size, output_size) -> (batch_size, output_size)

        if y is not None:
            return self.loss(y_pred, y)  # 预测值和真实值计算损失
        else:
            return y_pred  # 输出预测结果


def build_sample():
    """
    x是个5维tensor，以数组中最大值为分类标识
    :return:
    """
    x = np.random.random(5)
    return x, to_one_hot(5, np.argmax(x))


def to_one_hot(len, index):
    rs = np.zeros(len)
    rs[index] = 1
    return rs


def build_dataset(total_sample_num,device):
    X = []
    Y = []
    for i in range(total_sample_num):
        x, y = build_sample()
        X.append(x)
        Y.append(y)
    return torch.FloatTensor(X).to(device), torch.FloatTensor(Y).to(device)


# 用来测试每轮模型的准确率
def evaluate(model,device):
    model.eval()
    test_sample_num = 100
    x, y = build_dataset(test_sample_num,device)
    # print("本次预测集中共有%d个正样本，%d个负样本" % (sum(y,axis=0), test_sample_num - sum(y,axis=0)))

    print("实际分类合计：")
    print(torch.sum(y,dim=0))

    correct, wrong = 0, 0
    with torch.no_grad():
        y_pred = model(x)  # 模型预测
        print("预测分类合计：")
        print(torch.sum(y_pred,dim=0))

        for y_p, y_t in zip(y_pred, y):  # 与真实标签进行对比
            yp_index = torch.argmax(y_p)
            yt_index = torch.argmax(y_t)
            if yt_index == yp_index:
                correct += 1
            else:
                wrong += 1
    print("正确预测个数：%d, 正确率：%f" % (correct, correct / (correct + wrong)))
    return correct / (correct + wrong)


def init_device():
    if torch.cuda.is_available():
        device = torch.device("cuda:0")  # you can continue going on here, like cuda:1 cuda:2....etc.
        print("Running on the GPU")
    else:
        device = torch.device("cpu")
        print("Running on the CPU")

    return device


# 训练
def train():
    # 配置参数
    epoch_num = 100  # 训练轮数
    batch_size = 100  # 每次训练样本个数
    train_sample = 5000  # 每轮训练总共训练的样本总数
    input_size = 5  # 输入向量维度
    hide_size = 15  # 隐藏层维度
    output_size = 5  # 输出层维度
    learning_rate = 0.001  # 学习率


    # 初始化device
    device = init_device()

    # 建立模型
    model = TorchModel(input_size,hide_size,output_size).to(device)

    # 选择优化器
    optim = torch.optim.Adam(model.parameters(), lr=learning_rate)

    log = []
    # 创建训练集，正常任务是读取训练集
    train_x, train_y = build_dataset(train_sample,device)
    # 训练过程
    for epoch in range(epoch_num):
        model.train()
        watch_loss = []
        for batch_index in range(train_sample // batch_size):
            x = train_x[batch_index * batch_size: (batch_index + 1) * batch_size]
            y = train_y[batch_index * batch_size: (batch_index + 1) * batch_size]
            loss = model(x, y)  # 计算loss
            loss.backward()  # 计算梯度
            # if batch_index % 2 == 0:
            optim.step()  # 更新权重
            optim.zero_grad()  # 梯度归零

            watch_loss.append(loss.item())
        print("=========\n第%d轮平均loss:%f" % (epoch + 1, np.mean(watch_loss)))
        acc = evaluate(model,device)  # 测试本轮模型结果
        log.append([acc, float(np.mean(watch_loss))])
    # 保存模型
    torch.save(model.state_dict(), "model.pth")
    # 画图
    print(log)
    plt.plot(range(len(log)), [l[0] for l in log], label="acc")  # 画acc曲线
    plt.plot(range(len(log)), [l[1] for l in log], label="loss")  # 画loss曲线
    plt.legend()
    plt.show()
    return


if __name__ == "__main__":
    train()
