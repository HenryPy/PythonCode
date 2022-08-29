## 1 程序说明

- 作为上位机使用,串口连接测试机,PLC,机械手
- 软件分为中控和终端,两个.exe文件安装在windows10 X64系统上
- 主要功能为通讯:即让机械手准确知道应该去哪里取放料,以及当前产品状态
- 产品状态分为1N/2N/3N/OK,不同状态需要机械手进行不同处理

## 2 项目结构

### 2.1 Central_logic
- 里面是中控的代码+UI转的.py文件+图片资源转的.rcc资源
### 2.1 Terminal_logic
- 里面是终端的代码+UI转的.py文件+图片资源转的.rcc资源

## 3 软件打包.exe
- 这里就不作讲解了,上传两个打包好的文件,运行在行x64系统上!
### 2.8 图片
- 上几张设计UI图
[登录](https://user-images.githubusercontent.com/90136935/187111831-218b1cf1-471d-4222-821e-584adee88d9c.JPG)
![软件集成](https://user-images.githubusercontent.com/90136935/187111935-6f77a941-0cce-40c9-a19b-ab6508c2e913.jpg)
![中控](https://user-images.githubusercontent.com/90136935/187111964-c9ee68ab-4b50-48d5-9ce0-6362a8d1e4ef.JPG)
![终端](https://user-images.githubusercontent.com/90136935/187111972-e47b7a30-1a83-46b0-b850-736fac8d2135.JPG)
![3](https://user-images.githubusercontent.com/90136935/187112018-79d1ae52-fd00-448f-8cc9-107c2531a0ba.jpg)
![1](https://user-images.githubusercontent.com/90136935/187112040-4aff1d12-d2cb-4a2e-8dde-0909c2f1b95a.jpg)
