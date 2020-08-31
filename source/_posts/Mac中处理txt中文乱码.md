---
title: Mac中处理txt中文乱码
date: 2020-08-31 22:50:21
category:
tags:
---
> 最近下载了一本电子书，格式为TXT，打开后发现乱码，故在网上找到若干解决方法，特记于此，免于后烦。

## 合并文件
首先，每个章节为一个独立文件，文件名格式“章节编号.txt”。需要一个shell脚本整合到一个文件中
```sh
file=ALL.TXT
echo > $file

cat CONTENT.txt >> $file

for i in {1..101}
do
        index="${i}.txt"
        if [ $i -lt 10 ]
        then
                index="0${i}.txt"
        fi
        echo ${index}
        cat ${index} >> $file
        echo >> $file
done
```
## 解决乱码
[在线监测文件编码](https://it365.gitlab.io/zh-cn/decode/)
看到该文件编码为GB18030。
使用shell命令转换文件编码，命令格式如下：
```sh
 iconv -f encoding -t encoding sourcefile > destinationfile
```
则具体命令为
```sh
iconv -f GB18030 -t UTF8 A.txt > B.txt
```
参考文章中有批量命令，特誊抄于此：
```sh
find *.txt -exec sh -c "iconv -f GB18030 -t UTF8 {} > {}.txt" \;
```
至此，转码完成，需要对文件中特殊符号`^M`做删除处理，可参考我之前文章[windows格式文件转linux格式文件](https://carl-zk.github.io/blog/2017/05/09/Bash-Script%E5%AD%A6%E4%B9%A0/)

## 参考
https://www.jianshu.com/p/f55ddf1e9839
https://zhuanlan.zhihu.com/p/46935220
