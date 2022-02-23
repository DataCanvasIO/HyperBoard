# experiment-visualization

这个项目用来为Hypernets提供基于web的实验可视化功能。

### 安装

它依赖前端可视化组件库[experiment-visualization-frontend](../experiment-visualization-frontend)，开始构建前请先构建此项目。

构建所需要的软件环境：
- [nodejs v14.15.0+](https://nodejs.org/en/)

这个项目的前端部分使用yarn管理依赖、webpack构建，安装这两个工具：
```
npm install -g webpack webpack-cli yarn
```

克隆代码：
```shell
git clone https://github.com/DataCanvasIO/HyperBoard.git
```

构建并安装项目：
```shell
cd HyperBoard/experiment-visualization/js

# build frontend
yarn
yarn build
rm -rf ../experiment_visualization/assets/
cp -r build/ ../experiment_visualization/assets/

# install 
cd ..
python setup.py install
```
