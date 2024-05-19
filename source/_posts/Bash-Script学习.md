---
title: Bash Script学习
date: 2017-05-09 22:58:50
category:
tags: shell
---
>不看[TLCL](http://linuxcommand.org/index.php),学会shell script也惘然！

## 常用命令
### windows格式文件转linux格式文件
```sh
sed -i 's/^M//g' file
```
^M=Ctrl+v,Ctrl+m
*注意：Mac中安装gnu-sed替换原生sed，然后增加别名即可* 
*alias sed="/usr/local/opt/gnu-sed/bin/gsed"* 

### 截取文件
#### 从第3行到最后
`tail -n +3 file > newfile`
or
`sed '1,2d' file > newFile`
#### sed
`sed '3d' file`  删除第3行
`sed '2,3d' file` 删除第2到第3行
`sed '2,$d' file` 删除第2行到最后
`sed '/key/d' file` 删除文件中包含key的行

#### vi
>Mac中vi 语法高亮+行号
  cp /usr/share/vim/vimrc ~/.vimrc
  vi ~/.vimrc
  syntax on
  set nu!

`/key` 从当前行向下查找
`?key` 从当前行向上查找
`:%s/old/new/g` 全部替换
`:s/old/new` 只替换当前行第一个
`:s/old/new/g` 替换当前行所有
`:2,$s/old/new/g` 第2行到文件末

# 入门大全
## 脚本文件
文件首行一般为所用shell类型：
```sh
#!/bin/bash
echo 'hello world'
```
or
```sh
#!/bin/sh
echo 'hello world'
```
现在所有Linux、Unix系统都有`bash/sh`，而bash是对sh的增强版本，所以推荐直接用bash。

## 输出重定向
```sh
0 标准输入
1 标准输出
2 错误

2>err.log 错误信息重定向到err.log
>&2 错误输入到/var/log/auth.log (Ubuntu系统下)

./run.sh > mylog 2>&1 或 ./run.sh &>mylog

2>/dev/null 不处理 

> 清空再写入
>> 追加到行末
```
demo
```sh
#!/bin/bash
log="mylog" 
echo "hello world" >$log 2>&1
sl >>$log 2>&1
```
日志记录的正确方式
```sh
#!/bin/bash
LOG_FILE=mylog
exec 1>>$LOG_FILE 2>&1

echo "hello" 
ls .
sl
```
这样，脚本执行过程中的所有输出均输出到文件mylog中。
> 单引号和双引号的区别：单引号内容为纯文本，双引号内容可以被解析，如：
> ```sh
> str='hello world'
> echo "$str"
> echo '$str'
> ```
> 结果为
> ```sh
> hello world
> $str
> ```
** here doc ** 可以使用tab键控制文本格式，但只为方便阅读，不作用于输出
```sh
#!/bin/sh
# 普通
cat << eof
  hh
eof
# here document
cat <<- _EOF_
  hello world
  haha
    123
_EOF_
# here string
cat <<< "hello world"
```

## 文本处理三大利器 & 正则表达式
### grep
基础表达式
`^ $ . [ ] *`
```sh
grep "^[a-z]" /etc/passwd
```
扩展表达式
`( ) { } ? + |`
扩展表达式可以使用正则，如
```
grep -E "^[a-z]{1,6}" /etc/passwd
```
### sed
输出文件的第k行
`sed -n kp file`
输出第k到m行
`sed -n "k,mp" file`

逐行比较两个文件：
```sh
#!/bin/sh
echo "file1=$1, file2=$2"
na=`grep -c ".*" $1`
nb=`grep -c ".*" $2`
if (($na != $nb)); then
  echo "diff lines number: $na : $nb"
  exit 1
fi
for ((i=1; i<=$na; i++)); do
  la=`sed -n ${i}p $1`
  lb=`sed -n ${i}p $2`
  if [[ $la != $lb ]]; then
    printf "%s: file1=%s, file2=%s\n"  $i $la $lb
    exit 1
  fi
done
echo "check result : same file"
exit
```
### awk
统计每个人每月的加班情况
要求：加班结束时间必须大于等于19：30, 加班时长=（加班结束时间-18:30）/8, 保留2位小数，小数位不进位。

加班记录的文档：record
```
张三            2016/5/1 19:30
李四  2017/5/1 20:30
jack    2016/6/1  21:29
张三            2016/3/1 15:30
李四  2017/9/1 22:10
jack    2015/2/1  21:29
张三            2016/5/10 23:30
李四  2017/5/12 21:00
```
每一列分别代表：姓名、日期、下班时间，中间既可以是n空格，也可以是n个tab，或者二者的组合。

处理脚本：cal_work.sh
```sh
#!/bin/bash

# read me
echo -e "输入文件格式必须满足：\n\
user  2016/4/1 17:33\n" ## 大致格式是这样，只要有空格或tab隔开就行

log="work.log"  ## 日志记录

file=$1

# 备份之前结果
if [[ -e result_day ]]; then
  bak_time=`date +%Y%m%d%H%M%S`
  mv result_day result_day.bak.${bak_time}
  mv result_month result_month.bak.${bak_time}
  echo "`date "+%F %T"` back result_day result_month" >> $log
fi

echo "展示格式化之后的文档:" 
awk -F '[/:\t" "]' '{gsub("\t", " ");gsub(" +", " ")} {print NR, $1, $2, $3, $4, $5, $6, NF}' $file | head -n5

echo -e "\n`date "+%F %T"` start process file : $file" | tee -a $log
awk -F '[/:\t" "]' '{gsub("\t", " ");gsub(" +", " ")} {total=0;hour=$5-19;minute=$6-30; if(minute<0) {minute=30;hour-=1;} else {minute=0;}; if(hour>=0 && minute>=0) {total=hour*60+minute+60;}} {if(total>0) {total=total/480;total=substr(total, 1, index(total, ".")+2);print NR, $1, $2, $3, $4, hour, minute, total}}' $file > result_temp1

# 提取user year day到文档temp2
awk '{print $2, $3, $4}' result_temp1 | sort -u > result_temp2

while read line
  do
    ## awk 正则匹配 变量：外面''，里面""
    ## awk printf 变量：外面"",中间'',里面""
    awk 'BEGIN {total=0;} {if($0~/'"$line"'/) {total=total+$8;}} END {printf("%s %.2f\n", "'"$line"'", total)}' result_temp1 >> result_temp3
done < result_temp2

# human readable format
awk '{printf("%s %d/%d/%d %.2f\n", $2, $3, $4, $5, $8)}' result_temp1 > result_day
awk '{printf("%s %d/%d %.2f\n", $1, $2, $3, $4)}' result_temp3 > result_month

rm -f result_temp1 result_temp2 result_temp3
echo -e "`date "+%F %T"` process done : result_day result_month" | tee -a $log
```

统计结果:
jack 2015 2 0.31
jack 2016 6 0.31
张三 2016 5 0.74
李四 2017 5 0.56
李四 2017 9 0.43
注：每人每个月加班时长，单位(天)

awk printf打印单引号：
```sh
awk '{printf("'\''%s'\''", $1)}' file
```
awk 正则匹配
```sh
awk '{if($0~/regExp/)printf("%s", $0)}' file
```
文件a中存的key值，文件b中存的‘key value’值，从文件a找b中对应的value：
```sh
#!/bin/bash
while read key; do
  awk '{if($0~/'"($key)"'/)printf("%s\n", $0)}' fileb
done < filea
```

## 控制流语句
### if
[tutorial网站](http://ryanstutorials.net/bash-scripting-tutorial/bash-if-statements.php)
```sh
if [ <some test> ]; then
  <commands>
elif [  ]; then
else
fi
```
1. 文件
-d FILE | FILE exists and is a directory.
-e FILE | FILE exists.
-r FILE | FILE exists and the read permission is granted.
-s FILE | FILE exists and it's size is greater than zero (ie. it is not empty).
-w FILE | FILE exists and the write permission is granted.
-x FILE | FILE exists and the execute permission is granted.
```sh
if [ -d passwd ];then echo 'yes';else echo 'no'; fi
```
2. 字符串
-n STRING | The length of STRING is greater than zero.
-z STRING | The lengh of STRING is zero (ie it is empty).
STRING1 = STRING2 | STRING1 is equal to STRING2
STRING1 != STRING2  | STRING1 is not equal to STRING2
增强版的 ** [[ ]] ** 除了 ** [ ] ** 所有的功能外，还增加了一个重要特性：** string =~ regex **
```sh
#!/bin/sh
s1=-5
s2=ab
test () {
  echo param=$1
  if [[ $1 =~ ^-[0-9]+$ ]]; then
    echo $1
  fi
}
test $s1
test $s2
```
输出:
```sh
param=-5
-5
param=ab
```

3. 数字
INTEGER1 -eq INTEGER2 | INTEGER1 is numerically equal to INTEGER2
INTEGER1 -ne INTEGER2 | INTEGER1 is numerically not equal to INTEGER2
INTEGER1 -gt INTEGER2 | INTEGER1 is numerically greater than INTEGER2
INTEGER1 -lt INTEGER2 | INTEGER1 is numerically less than INTEGER2
INTEGER1 -ge INTEGER2 | INTEGER1 is greater or equal INTEGER2
INTEGER1 -le INTEGER2 | INTEGER1 is less or equal INTEGER2
```sh
#!/bin/bash
# test-integer: evaluate the value of an integer.
INT=-5
if [ -z "$INT" ]; then
    echo "INT is empty." >&2
    exit 1
fi
if [ $INT -eq 0 ]; then
    echo "INT is zero."
else
    if [ $INT -lt 0 ]; then
        echo "INT is negative."
    else
        echo "INT is positive."
    fi
    if [ $((INT % 2)) -eq 0 ]; then
        echo "INT is even."
    else
        echo "INT is odd."
    fi 
fi
```
与 ** [[ ]] ** 类似，** (( )) ** 是对数字版的增强：
```sh
#!/bin/sh
s="123"
if (($s > 0));then
  if (( (($s % 2)) > 0)); then
    echo "${s}mod2=`expr $s % 2`"
  elif (( (($s % 3)) == 0)); then
    echo "oh no"
    exit 1
  fi
fi
```

### and、or、not
```sh
#!/bin/sh
MIN_VAL=-100
MAX_VAL=100
val=23

if [[ ($val -gt 10) && ($val -lt 50) ]]; then
  echo yes
fi

if [[ !($(($val % 2)) -eq 0) || ($val -le $MAX_VAL)]]; then
  echo yes
fi
```
### for
```sh
for variable [in worlds]; do
done
```

```sh
for i in {a..g}; do
  echo $i
done

i=1
for ((i=0; i<5; i++));do
  echo $i
done
# 读文件
for i in `cat file`; do
  wget "$i"
done
```
### while
```sh
i=1
while (($i < 5)); do
  echo $i
  ((i++))
done
```
while 还可以用于读文件
```sh
while read line; do
  echo $line
done < file
```
### case
```sh
case word in
  [pattern [|pattern]]...) command
                        ;;
  *) 
    exit 1
    ;;
esac
```
如果想一次匹配多个，则：`;;&`




## set 方便debug
[bash-set](http://www.ruanyifeng.com/blog/2017/11/bash-set.html)
全部
```
#！/bin/bash -x

```
部分
```
#！/bin/bash

set -x    # turn on tracing

set +x    # turn off tracing

```

## 字符串截取
```sh
截取URL：
s=http://www.xxx.com//123
# 1.从左边开始删除第一个//及左边所有字符
echo ${s#*//}
# 2.从左边开始删除最后一个//及左边所有字符
echo ${s##*//}
# 3.从右边开始删除第一个//及右边所有字符
echo ${s%//*}
# 4.从右边开始删除最后一个//及右边所有字符
echo ${s%%//*}
```
demo
```sh
## s.sh
s="http://www.fuck.com//123//4/5"
echo $s
echo ${s#*/}
echo ${s##*/}
echo ${s%/*}
echo ${s%%/*}

结果：
http://www.fuck.com//123//4/5
/www.fuck.com//123//4/5
5
http://www.fuck.com//123//4
http:
```


## 随机字符串和数字
生成不大于120的正整数
```sh
expr `cat /dev/urandom | od -An -N1 -tu1` % 120 
```
生成长度最小为3的字符串
```sh
cat /dev/urandom | sed 's/[^a-zA-Z]//g' | strings -n3 | head -n1
```

## find 
搜文件并删除
```sh
find . -name ".DS_Store" -exec rm -rf {} \;
```

每次匹配，ls都执行一次
`find /usr/bin -type f -name '*zip' -ok ls -l '{}' ';'`

所有结果传递，ls执行一次
`find /usr/bin -type f -name '*zip' -exec ls -l '{}' +`
or
`find /usr/bin -type f -name '*zip' | xargs ls -l`


## Networking
ping
traceroute xxx.com
ip a
netstat
ftp
wget
ssh
sftp
## Searching For Files
locate
find
xargs
touch
stat
