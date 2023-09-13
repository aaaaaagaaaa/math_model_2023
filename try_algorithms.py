#用于测试退火算法 求目标函数最小值
import math
from random import random
import matplotlib.pyplot as plt

#优化函数
def func(x,y):
    return x**2+y**2

class SA:
    def __init__(self,func,iter=100,T_max=100,T_min=0.01,alpha=0.99) -> None:
        self.func=func
        self.iter=iter
        self.T_max=T_max
        self.T_min=T_min
        self.alpha=alpha
        self.T=T_max            #当前温度
        self.x=[random()*11-5 for i in range(iter)]
        self.y=[random()*11-5 for i in range(iter)]#随机生成iter个目标点 实际范围在(-6,6)
        self.most_best=[]
        self.history={'f':[],'T':[]}

    def generatr_new(self,x,y):
        '''用于更新数据 严格落入[-5,5]定义域中'''
        while True:
            x_new=x+self.T*(random() - random())
            y_new=x+self.T*(random() - random())
            
            if (-5<=x_new<=5) & (-5<=y_new<=5):
                break
        return x_new,y_new
    
    def Metroplics(self,f,f_new):
        '''Metroplics准则'''
        if f>=f_new:
            return 1 
        else:
            p=math.exp((f - f_new) / self.T)
            if random() < p:
                return 1
            else:
                return 0
    
    def best(self):
        '''用于得出循环中各点中的最小值'''
        f_list=[]
        for i in range(self.iter):
            f_list.append(self.func(self.x[i],self.y[i]))
        f_best=min(f_list)
        ind=f_list.index(f_best)
        return f_best,ind
        
        
    def run(self):     
        '''运行SA'''
        count=0
        while self.T>self.T_min:#执行外循环
            
            for i in range(self.iter):#执行内循环
                f=self.func(self.x[i],self.y[i])
                x_new,y_new=self.generatr_new(self.x[i],self.y[i])
                f_new=self.func(x_new,y_new)
                if self.Metroplics(f,f_new):
                    self.x[i]=x_new
                    self.y[i]=y_new
            
            f_inside,ind_inside=self.best()
            self.history['f'].append(f_inside)
            self.history['T'].append(self.T)
            self.T=self.T * self.alpha
            count+=1
        
        f_final,ind_final=self.best()
        print(f"F={f_final},x={self.x[ind_final]},y={self.y[ind_final]}")

sa=SA(func)
sa.run()

# #绘制图像
plt.plot(sa.history['T'],sa.history['f'])
plt.title("SA")
plt.xlabel('T')
plt.ylabel('f')
plt.gca().invert_xaxis()
plt.show()             