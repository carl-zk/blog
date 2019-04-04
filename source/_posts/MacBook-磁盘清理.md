---
title: MacBook 磁盘清理
date: 2019-04-04 19:51:52
category: 系统配置
tags:
---
> 刚买的电脑磁盘满了，有点怀疑人生。查下来发现是由于sublime的临时文件导致的。由于Mac上趁手的工具需要花钱，从磁盘中找到哪里出的问题也需要些技巧，所以在这里记下来方便以后查看。

## 查看磁盘总的使用情况
`df -h`
![](http://ppdxz524p.bkt.clouddn.com/macClean/1.png)
可以看到磁盘剩余89G。

## 查看文件夹大小
有两种方式，以查看文件夹A为例：
- 打开Finder，选中文件夹A，右键 -> Get Info。
- 打开终端，进入文件夹A的上一级目录，输入 `du -h -d 1`
我使用命令方式，逐级定位出超大文件夹位置。使用命令`ls -ahg`查看超大文件夹各文件大小：
![](http://ppdxz524p.bkt.clouddn.com/macClean/2.png)
至此终于找出299G大的临时文件.channel_v3.json.swp，将其删除即可。

## 帮助
Finder 查看隐藏文件（夹），快捷键：`command + shift + .`
Finder 打开显示完整路径 `View -> Show Path Bar` 
Finder 中右键进入Terminal `Finder -> Services -> Services Preferences/Shortcuts/Files and Folders/New Terminal Tab at Folder` 


