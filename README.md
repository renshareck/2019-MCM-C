# 2019-MCM-C
2019-MCM-C题（数据可视化及网络化SIRS模型模拟）

## 文件说明
mcm_data.sql  为数据库文件（mysql）

map.py        为可视化地图数据

list.json     为Kentucky中各县网络结构邻接表

get_model.py  为基于网络化SIRS模型模拟程序



## 细节说明

### 数据可视化说明
数据地图显示主要基于echarts
http://pyecharts.org

### 模型说明
SIRS为封闭范围内的一种传播模型，此处将封闭条件打破，使SIRS影响因素由自身转变为相邻地区及自身共同影响，即网络化的SIRS模型。
使 dI/dt= g · Average(I, Inear) − K
核心在于使 SIRS 模型在拓扑网络结构上也可适用。
