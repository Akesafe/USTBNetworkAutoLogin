# 北科大校园网自动登录脚本
## 原理
模拟浏览器访问202.204.48.66，填入用户名和密码并回车

具体地说，脚本通过TAB键遍历网页元素，查找类型为text和password的文本框，填入config.yaml文件中的用户名和密码，并在后台自动运行，方便服务器或无人值守电脑保持联网
## 支持环境
适用于Windows电脑+Chrome浏览器
## 使用说明
### 1.安装Python环境
具体教程略

在cmd中输入python能够显示版本号说明安装完成

完成之后在cmd中输入以下命令安装相应的包：
```
pip install selenium
pip install schedule
```
### 2.安装**Chrome**浏览器
具体教程略
### 3.修改config.yaml文件
下载并解压源码后，用记事本打开config.yaml，修改username（学号）和password（校园网登录密码），例如：
```
username: "423233xx"
password: "USTBxxxxxx"
```
配置文件里还可以修改其他配置信息，具体见config.yaml
### 4.双击USTBNetwork_AutoLogin.bat文件运行
### 5.（可选）将bat脚本添加到开机自启
- 使用 **Windows+R** 打开运行窗口
- 输入 **shell:startup** 并按回车进入启动目录
- 右击 **USTBNetwork_AutoLogin.bat** -> **创建快捷方式**
- 将快捷方式剪切到启动目录下
### 6.（可选）更新chromedriver
chrome版本和chromedriver版本需要对应，否则需要更新driver目录下的chromedriver.exe文件

可参考[https://zhuanlan.zhihu.com/p/110274934]()或自行上网搜索下载
## 注意
该脚本没有进程锁，如果你想通过Windows“计划任务”自动运行 **USTBNetwork_AutoLogin.bat** ，请将 **config.yaml** 中的 autorun - enabled 的值设置为false

*By Akesafe.*
