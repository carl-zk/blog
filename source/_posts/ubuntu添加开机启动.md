---
title: ubuntu添加开机启动
date: 2016-06-18 12:50:27
category: 系统配置
tags:
---
> 我将mysql server 的开机启动写成脚本,加到rc.local文件中;
> XX-Net需要联网,所以设置成为一个启动服务,优先级99;

#### 1、方法一，编辑rc.loacl脚本 
Ubuntu开机之后会执行/etc/rc.local文件中的脚本，
所以我们可以直接在/etc/rc.local中添加启动脚本。
当然要添加到语句：exit 0 前面才行。
如：
sudo vi /etc/rc.local
然后在 exit 0 前面添加好脚本代码。

```sh
#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.

echo never > /sys/kernel/mm/transparent_hugepage/enabled

# mysql start with system
/usr/local/mysql/bin/mysqld_safe --user=root &

exit 0

```
 #### 2、方法二，添加一个Ubuntu的开机启动服务。
如果要添加为开机启动执行的脚本文件，
可先将脚本复制或者软连接到/etc/init.d/目录下，
然后用：update-rc.d xxx defaults NN命令(NN为启动顺序)，
将脚本添加到初始化执行的队列中去。
注意如果脚本需要用到网络，则NN需设置一个比较大的数字，如99。
1) 将你的启动脚本复制到 /etc/init.d目录下
 以下假设你的脚本文件名为 test。
2) 设置脚本文件的权限
 $ sudo chmod 755 /etc/init.d/test
3) 执行如下命令将脚本放到启动脚本中去：
 $ cd /etc/init.d
 $ sudo update-rc.d test defaults 95
 注：其中数字95是脚本启动的顺序号，按照自己的需要相应修改即可。在你有多个启动脚本，而它们之间又有先后启动的依赖关系时你就知道这个数字的具体作用了。该命令的输出信息参考如下：
update-rc.d: warning: /etc/init.d/test missing LSB information
update-rc.d: see <http://wiki.debian.org/LSBInitScripts>
  Adding system startup for /etc/init.d/test ...
    /etc/rc0.d/K95test -> ../init.d/test
    /etc/rc1.d/K95test -> ../init.d/test
    /etc/rc6.d/K95test -> ../init.d/test
    /etc/rc2.d/S95test -> ../init.d/test
    /etc/rc3.d/S95test -> ../init.d/test
    /etc/rc4.d/S95test -> ../init.d/test
    /etc/rc5.d/S95test -> ../init.d/test
卸载启动脚本的方法：
 $ cd /etc/init.d
$ sudo update-rc.d -f test remove
命令输出的信息参考如下：
Removing any system startup links for /etc/init.d/test ...
    /etc/rc0.d/K95test
    /etc/rc1.d/K95test
    /etc/rc2.d/S95test
    /etc/rc3.d/S95test
    /etc/rc4.d/S95test
    /etc/rc5.d/S95test
    /etc/rc6.d/K95test

\>sudo update-rc.d xxnet-service defaults 99

/*xxnet-service*/
```sh
#!/bin/bash

/opt/XX-Net-3.1.19/start
```