---
title: linux
date: 2026-05-30 12:42:49
category: 系统配置
tags:
---
## dual-system 
现在装双系统变的更简单了。
准备一个U盘或移动硬盘，备份好，
1. 用[Ventoy](https://www.ventoy.net/en/doc_start.html)烧录；它就是一个引导程序，不用烧录so文件。
2. 将ubuntu .so文件复制进去； 可以复制任意个so.
3. windows 磁盘管理，切割一块空白区域。
4. 我的是F2打开开机引导，如果是双系统，后面要选择“alongside with windows",具体的忘了，差不多是这个。
5. 中间不需要手动选择分区，也不用划分区，最新的ubuntu都是自动的，swap区也不需要。

## ubuntu
> first of all `sudo apt-update`

- v2rayn + chrome, ”一分机场“
- ibus-rime + double-pinyin， 小鹤双拼
- vs code，必须用.deb安装，否则ibus中文输入失效
- zsh, oh-my-zsh, theme选awsomepanda
- jdk, [termurin](https://adoptium.net/temurin/releases)，不叫openjdk但仍然是openjdk
- Intellij IDEA, 已不区分Community/Ultimate

安装的都在 /snap, /opt.  
config目录 ~/.config  
不用担心dnsleak了，coreDNS用不到了  

### env

- .zsh
```
# develop
export JAVA_HOME=/home/carl/local/jdk-25.0.3+9 
export PATH=$PATH:${JAVA_HOME}/bin
export IDE_HOME=/home/carl/local/idea-IU-261.24374.151
export PATH=$PATH:${IDE_HOME}/bin
```
如果频繁换版本，就设置软连接 ln -s 指向具体版本，以后不用改变量。

- .gitconfig
```
[user]
        name = carl
        email = zxfspace@gmail.com
        signingkey = 55E2D3919A960DFC
[init]
        defaultBranch = main
[commit]
        gpgsign = true
[alias]
        st = status
        co = checkout
        b = branch
        cm = commit -m
        lg = log --graph --oneline --decorate --all
[color]
        ui = auto
[diff]
        algorithm = histogram
[pull]
        ff = only
[includeIf "gitdir:~/work/"]
        path = ~/work/.gitconfig

```

- ~/.config/ibus/rime/default.custom.yaml
```
patch:
  schema_list:
    - {schema: double_pinyin_flypy}
  ascii_composer:
    switch_key:
      Shift_L: commit_code
      Shift_R: commit_code
```
左右shift切换中英文。

## HHKB 
![](/2026/05/30/linux/hhkb1.png)
![](/2026/05/30/linux/hhkb2.png)
