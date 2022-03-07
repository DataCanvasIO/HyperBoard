# hboard-frontend

这个项目是hypernets实验可视化的前端组件库。
它被项目`hboard`和`hboard-widget`所使用。

## 构建项目

构建所需要的软件环境：
- [nodejs v14.15.0+](https://nodejs.org/en/)

这个项目使用yarn管理依赖、webpack构建，先安装这两个工具：
```
npm install -g webpack webpack-cli yarn
```

克隆项目源码：
```
git clone https://github.com/DataCanvasIO/HyperBoard.git
```

构建项目：
```
cd HyperBoard/hboard-frontend
yarn
webpack
```
