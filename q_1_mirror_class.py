import math
import openpyxl
import matplotlib.pyplot as plt
import test


path1="/Users/lvangge/Desktop/附件.xlsx"

def get_ord(path1):
    workbook=openpyxl.load_workbook(path1)
    sheet=workbook.active

    x=[cell.value for cell in sheet['A']]
    y=[cell.value for cell in sheet['B']]
    x.pop(0)
    y.pop(0)
    return x,y

x,y=get_ord(path1)

class Mirrors:
    def __init__(self,x,y,a=6,b=6) -> None:
        self.x=x
        self.y=y
        self.a=a
        self.b=b#长宽为默认值6
        self.point=list(zip(x,y))
        self.r=[math.sqrt(x[i]**2+y[i]**2) for i in range(len(x))]
        #self.angle=[math.atan(y[i]/x[i]) for i in range(len(x)) ]
    
    def d_v(self):
        '''径向'''
        i,j=0,1
        d_v={'d':[],'ind':[]}
        while j<len(self.x):
            if 12<math.dist((self.x[i],self.y[i]),(self.x[j],self.y[j]))<20 and j>i+1:
                d_v['d'].append(math.dist((self.x[i],self.y[i]),(self.x[j],self.y[j])))
                d_v['ind'].append(i)
                i=j
            j+=1
        return d_v
    
    def num(self):
        return [self.d_v()['ind'][i+1]-self.d_v()['ind'][i] for i in range(len(self.d_v()['ind'])-1)]
    
    def d_r(self):
        '''切向'''
        d_r=[]
        for i in range(len(self.d_v()['ind'])-1):
            d_r.append(sum([math.dist((mirrors.x[j],mirrors.y[j]),(mirrors.x[j+1],mirrors.y[j+1]))for j in range(self.d_v()['ind'][i],self.d_v()['ind'][i+1])])/self.num()[i])  
        return d_r
    
    def plot_show(self):
        plt.scatter(self.x,self.y,s=10,color='silver')
        plt.title("mirrors")
        plt.xlabel('x')
        plt.ylabel('y')
        plt.show()  
        

mirrors=Mirrors(x,y)

# mlist=[test.Mirror(x[i],y[i]) for i in range(len(x))]

# print(test.E_mean(mlist)*len(mlist)*36)


# print(mirrors.d_r())
# print(sum(mirrors.d_v()['d'])/len(mirrors.d_v()['d']))#相邻层层距离
# print(mirrors.d_v()['ind'])#每层与0元素对齐的元素指标
# print(mirrors.num())#每层元素个数
# print(mirrors.d_r())
# mirrors.plot_show()
#print(mirrors.r)



        
    
    

