---
title: windows
date: 2024-05-19 12:04:23
category: 系统配置
tags:
---

## software
### [PowerToys](https://learn.microsoft.com/en-us/windows/powertoys/)
![](/2024/05/19/windows/powertoys.png)
### [LightShot 截图工具](https://app.prntscr.com/en/) or [snipaste](https://www.snipaste.com/)
### [coreDNS](https://coredns.io/)
![](/2024/05/19/windows/coreDNS.png)
[Corefile](/blog/2024/05/19/windows/Corefile)
[my-core-dns-service.xml](/blog/2024/05/19/windows/my-core-dns-service.xml)
[winSW](https://github.com/winsw/winsw)
检查一下 `nslookup example.com 127.0.0.1`
改WiFi的dns：
![](/2024/05/19/windows/wifi.png)
### [v2rayN](https://github.com/2dust/v2rayN)
![](/2024/05/19/windows/v2rayN.png)
### [JDownloader2](https://jdownloader.org/download/index)
![](/2024/05/19/windows/JDownloader2.png)
### [qbittorrent](https://www.qbittorrent.org/download)
### [Twinkle Tray](https://twinkletray.com/)
### [荐片高清影音](https://www.jianpian8.co/)
### [potplayer](https://potplayer.tv/?lang=zh_CN)
### [cudaText](https://cudatext.github.io/)
`ctr-shift-p`
### [hhkb Keymap Tool](https://happyhackingkb.com/download/)
### ssh
```sh
ssh 配置 client 无密码登录

远程主机中：
cd .ssh // 没有就执行 ssh-keygen
vi authorized_keys
将id_rsa.pub复制进去
chmod 600 authorized_keys

本地：
cd .ssh
vi config
Host hostA //名字随便起
  Hostname ip
  Port 22
  User xx
  ServerAliveInterval 120 //每2分钟发一个空包，保持连接用的
  ServerAliveCountMax 5 //5次收不到服务端响应就断开
Host * // *匹配所有
  Port 22
  ServerAliveInterval 120 //每2分钟发一个空包，保持连接用的
  ServerAliveCountMax 5 //5次收不到服务端响应就断开
  
使用：
ssh hostA

帮助：
man ssh_conifg
```

other optional utils:
[PuTTY](https://www.putty.org/)
[mRemoteNG](https://mremoteng.org/)

## local
[openJDK](https://adoptium.net/temurin/releases/?os=windows)
[eclipse](https://www.eclipse.org/downloads/packages/)
[eclipse_preferences.epf](/blog/2024/05/19/windows/eclipse_preferences.epf)
[settings.xml](/blog/2024/05/19/windows/settings.xml)
[RainbowDrops.xml](/blog/2024/05/19/windows/RainbowDrops.xml)
![](/2024/05/19/windows/eclipse.png)

## dns over https
https://doh.libredns.gr/noads
https://dns.quad9.net/dns-query

## desktop
[Macified-Windows](https://github.com/Runixe786/Macified-Windows)

## 输入法
[小狼毫](https://github.com/rime/home/wiki/CustomizationGuide#%E4%B8%80%E4%BE%8B%E5%AE%9A%E8%A3%BD%E6%AF%8F%E9%A0%81%E5%80%99%E9%81%B8%E6%95%B8)


