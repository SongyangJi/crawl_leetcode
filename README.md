# crawl_leetcode

## 介绍
我的爬虫项目（一） —————— 爬取力扣题目集、题解等信息
目前爬取了[力扣首页](https://leetcode-cn.com/problemset/all/)的题目列表
![](https://img-blog.csdnimg.cn/20210710041931194.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQ0ODQ2MzI0,size_16,color_FFFFFF,t_70)

以及对应每一道题目的详细信息。
![](https://img-blog.csdnimg.cn/20210710042307538.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQ0ODQ2MzI0,size_16,color_FFFFFF,t_70)


## 使用说明
1. 下载好本项目需要的py包
2. 配置好本地的MongoDB环境
3. 下载Chrome Driver(selenium需要使用到)
4. 抓取数据：运行scrape/crawler.py 即可


## 软件架构
### 下载器模块
downloader模块提供下载web资源的统一接口，例如下载图片、下载文本文件、视屏资源等等。
目前仅仅编写了下载了图片的代码。

### 池化模块
将可以复用的资源池化。如进程、线程、动态IP等等。
#### 进程池、线程池
目前主要编写了可用于多任务批处理的程序。
由于cPython的GIL（全局解释器锁）的存在，使得Python的多线程无法真正发挥多核处理器处理CPU密集型任务的优势。
所以，编写了BatchProcessing.py 这个程序，向外提供一个 commit(runnable: Runnable)、batch()的接口提供批处理任务的功能。
其中 Runnable是可执行任务的接口类，用户需要自己override掉它的run方法。

#### 动态IP池
当我们使用爬虫的时候，如果频繁对某一个界面请求过太多的次数，
那么有些网站就会因为反爬虫的措施发现同一个IP地址对它请求了太多的次数，因此对我们的爬虫进行了禁止。
如果我们能够直接在请求网页的时候不断更换自己的IP地址，就不会被系统检查出来。
因此，这也是我们需要使用动态IP代理的缘故。

代理IP的匿名度：
+ 透明：服务器知道该次请求使用了代理，也知道本次请求的真实IP。
+ 匿名：知道使用了代理，但是不知道真实的IP。
+ 高匿：服务器不知道使用了代理，也不知道使用了假的IP。

设计思路：
从那些提供免费的动态IP的网站，获取批量的ip放入一个队列。
在每次发出http请求的时候，从队列中返回一个可用的ip（通过一个检测函数，测试ip的可用性）
不过目前还没有写，挖个坑

### 持久化模块
目前使用MongoDB数据库作为持久化存储。
理由：十分方便地存储、查询json形式等非结构化的web数据。

### 分析与可视化模块
使用了pandas的DataFrame作为数据分析的载体，
可以很方便的进行求平均数、分组等操作。

可视化方面，本来打算使用pycharts。
后来简单处理了一下，使用使用matplotlib和pandas的画图功能即可。
只不过画起来没那么好看罢了。