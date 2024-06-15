---
title: Bash Script学习
date: 2017-05-09 22:58:50
category:
tags: shell
---
>不看[TLCL](http://linuxcommand.org/index.php),学会shell script也惘然！

#!bin/bash -e 或 set -e 执行报错就停止
-x 打印每条
command & 后台执行
jobs --show back tasks
fg %job_number 把task从back挪出来，可以用ctr+c停掉
ctr+z 停process
bg %job_number 
kill -15/20

## 常用命令
### windows格式文件转linux格式文件
```sh
sed -i 's/^M//g' file
```
^M=Ctrl+v,Ctrl+m
*注意：Mac中安装gnu-sed替换原生sed，然后增加别名即可* 
*alias sed="/usr/local/opt/gnu-sed/bin/gsed"* 

windows 下 java项目编码由gbk改为utf8
```
find . -name '*.java' -exec bash -c "iconv -f gbk -t utf-8 '{}'.utf8" \;
find . -name '*.java' -exec rm -rf {} \;
find . -name '*.utf8' | awk -F "." '{print $2}' | xargs -i -t mv ./{}.java.utf8 ./{}.java;
```

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

vi file1 file2
:bn 切换
:bp
:buffers 文件列表

O -insert above line
I -insert lien heading
r -replace one char
R -replace until Esc
cw -change current word with next text
C -change until Esc
cc -change whole line
dw -delete word
D -delete to tail

?string -search backward

:.= -current line number
:= -total line number

:w newfile -write into another file



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

echo '$(cal)' 单引号使特殊字符失效

## string
foo="fdjslj jfd"
echo ${#foo} 长度
echo ${foo:5:2} 截取
test -z "$foo" && echo yes 必须用引号括起来

arr=("a" "b" "c")
for i in "${arr[@]}"; do 必须用引号括起来，最优方式
  echo $i
done

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

cat < file_name
cat > file_name


## 文本处理三大利器 & 正则表达式

```
^ (caret): Matches the start of a string.
$ (dollar): Matches the end of a string.
. (dot): Matches any single character except a newline character.
[] (square brackets): Defines a character class, matching any one character within the brackets.
{} (curly brackets): Specifies a specific quantity of characters to match.
- (hyphen): Specifies a range of characters when used within square brackets.
? (question mark): Makes the preceding character optional, matching zero or one occurrence.
* (asterisk): Matches zero or more occurrences of the preceding character.
+ (plus): Matches one or more occurrences of the preceding character.
() (parentheses): Groups expressions together.
| (pipe): Indicates an OR condition between two expressions.
\ (backslash): Escapes a metacharacter, allowing it to be matched as a literal character.
```

[regex-support from elastic](https://www.elastic.co/guide/en/beats/heartbeat/current/regexp-support.html)
|             Pattern              |                                         Description                                         |
|----------------------------------|---------------------------------------------------------------------------------------------|
|        **Single Characters**         |                                                                                             |
|                x                 |                                      single character                                       |
|                .                 |                                        any character                                        |
|              [xyz]               |                                       character class                                       |
|              [^xyz]              |                                   negated character class                                   |
|           [[:alpha:]]            |                                    ASCII character class                                    |
|           [[:^alpha:]]           |                                negated ASCII character class                                |
|                \d                |                                    Perl character class                                     |
|                \D                |                                negated Perl character class                                 |
|               \pN                |                          Unicode character class (one-letter name)                          |
|            \p{Greek}             |                                   Unicode character class                                   |
|               \PN                |                      negated Unicode character class (one-letter name)                      |
|            \P{Greek}             |                               negated Unicode character class                               |
|            **Composites**            |                                                                                             |
|                xy                |                                       x followed by y                                       |
|               x|y                |                                      x or y (prefer x)                                      |
|           **Repetitions**            |                                                                                             |
|                x*                |                                       zero or more x                                        |
|                x+                |                                        one or more x                                        |
|                x?                |                                        zero or one x                                        |
|              x{n,m}              |                             n or n+1 or …​ or m x, prefer more                              |
|              x{n,}               |                                  n or more x, prefer more                                   |
|               x{n}               |                                         exactly n x                                         |
|               x*?                |                                zero or more x, prefer fewer                                 |
|               x+?                |                                 one or more x, prefer fewer                                 |
|               x??                |                                 zero or one x, prefer zero                                  |
|             x{n,m}?              |                             n or n+1 or …​ or m x, prefer fewer                             |
|              x{n,}?              |                                  n or more x, prefer fewer                                  |
|              x{n}?               |                                         exactly n x                                         |
|             **Grouping**             |                                                                                             |
|               (re)               |                             numbered capturing group (submatch)                             |
|           (?P<name>re)           |                         named & numbered capturing group (submatch)                         |
|              (?:re)              |                                     non-capturing group                                     |
|             (?i)abc              |                        set flags within current group, non-capturing                        |
|             (?i:re)              |                             set flags during re, non-capturing                              |
|           (?i)PaTTeRN            |                              case-insensitive (default false)                               |
|          (?m)multiline           | multi-line mode: ^ and $ match begin/end line in addition to begin/end text (default false) |
|           (?s)pattern.           |                               let . match \n (default false)                                |
|            (?U)x*abc             |            ungreedy: swap meaning of x* and x*?, x+ and x+?, etc (default false)            |
|          **Empty Strings**           |                                                                                             |
|                ^                 |                            at beginning of text or line (m=true)                            |
|                $                 |                      at end of text (like \z not \Z) or line (m=true)                       |
|                \A                |                                    at beginning of text                                     |
|                \b                |           at ASCII word boundary (\w on one side and \W, \A, or \z on the other)            |
|                \B                |                                 not at ASCII word boundary                                  |
|                \z                |                                       at end of text                                        |
|         **Escape Sequences**         |                                                                                             |
|                \a                |                                     bell (same as \007)                                     |
|                \f                |                                  form feed (same as \014)                                   |
|                \t                |                                horizontal tab (same as \011)                                |
|                \n                |                                   newline (same as \012)                                    |
|                \r                |                               carriage return (same as \015)                                |
|                \v                |                            vertical tab character (same as \013)                            |
|                \*                |                         literal *, for any punctuation character *                          |
|               \123               |                          octal character code (up to three digits)                          |
|               \x7F               |                                two-digit hex character code                                 |
|            \x{10FFFF}            |                                     hex character code                                      |
|             \Q...\E              |                        literal text ... even if ... has punctuation                         |
|     **ASCII Character Classes**      |                                                                                             |
|           [[:alnum:]]            |                             alphanumeric (same as [0-9A-Za-z])                              |
|           [[:alpha:]]            |                                alphabetic (same as [A-Za-z])                                |
|           [[:ascii:]]            |                                 ASCII (same as \x00-\x7F])                                  |
|           [[:blank:]]            |                                    blank (same as [\t ])                                    |
|           [[:cntrl:]]            |                              control (same as [\x00-\x1F\x7F])                              |
|           [[:digit:]]            |                                   digits (same as [0-9])                                    |
|           [[:graph:]]            |        graphical (same as [!-~] == [A-Za-z0-9!"#$%&'()*+,\-./:;<=>?@[\\\]^_` {|}~])         |
|           [[:lower:]]            |                                 lower case (same as [a-z])                                  |
|           [[:print:]]            |                          printable (same as [ -~] == [ [:graph:]])                          |
|           [[:punct:]]            |                            punctuation (same as [!-/:-@[-`{-~])                             |
|           [[:space:]]            |                             whitespace (same as [\t\n\v\f\r ])                              |
|           [[:upper:]]            |                                 upper case (same as [A-Z])                                  |
|            [[:word:]]            |                           word characters (same as [0-9A-Za-z_])                            |
|           [[:xdigit:]]           |                               hex digit (same as [0-9A-Fa-f])                               |
| **Supported Perl Character Classes** |                                                                                             |
|                \d                |                                   digits (same as [0-9])                                    |
|                \D                |                                 not digits (same as [^0-9])                                 |
|                \s                |                              whitespace (same as [\t\n\f\r ])                               |
|                \S                |                            not whitespace (same as [^\t\n\f\r ])                            |
|                \w                |                           word characters (same as [0-9A-Za-z_])                            |
|                \W                |                         not word characters (same as [^0-9A-Za-z_])                         |

[Regular expression syntax](https://www.ibm.com/docs/en/nsm/61.1?topic=expressions-regular-expression-syntax#JL1078292394b__BABCCCCA)

| Token |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   Matches                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|-------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|   .   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                Any character.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|   ^   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 The start of a line (a zero-length string).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|   $   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        The end of a line; a new line or the end of the search buffer.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|  \<   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  The start of a word (where a word is a string of alphanumeric characters).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|  \>   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                The end of a word (the zero length string between an alphanumeric character and a non-alphanumeric character).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|  \b   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             Any word boundary (this is equivalent to (\<¦\>) ).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|  \d   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              A digit character.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|  \D   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           Any non-digit character.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|  \w   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                A word character (alphanumeric or underscore).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|  \W   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   Any character that is not a word character (alphanumeric or underscore).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|  \s   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           A whitespace character.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|  \S   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        Any non-whitespace character.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|  \c   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            Special characters and escaping. The following characters are interpreted according to the C language conventions: \0, \a, \f, \n, \r, \t, \v. To specify a character in hexadecimal, use the \xNN syntax. For example, \x41 is the ASCII character A.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|   \   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               All characters apart from those described above may be escaped using the backslash prefix. For example, to specify a plain left-bracket use \[.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|  []   | Any one of the specified characters in a set. An explicit set of characters may be specified as in [aeiou] as well as character ranges, such as [0-9A-Fa-f], which match any hexadecimal digit. The dash (-) loses its special meaning when escaped, such as in [A\-Z] or when it is the first or last character in a set, such as in [-xyz0-9].  All of the above backslash-escaping rules may be used within []. For example, the expression [\x41-\x45] is equivalent to [A-D] in ASCII. To use a closing bracket in a set, either escape it using [\]] or use it as the first character in the set, such as []xyz].  POSIX-style character classes are also allowed inside a character set. The syntax for character classes is [:class:]. The supported character classes are:  [:alnum:] - alphanumeric characters. [:alpha:] - alphabetic characters. [:blank:] - space and TAB characters. [:cntrl:] - control characters. [:digit:] - numeric characters. [:graph:] - characters that are both printable and visible. [:lower:] - lowercase alphabetic characters. [:print:] - printable characters (characters that are not control characters). [:punct:] - punctuation characters (characters that are not letters, digits, control characters, or spaces). [:space:] - space characters (such as space, TAB and form feed). [:upper:] - uppercase alphabetic characters. [:xdigit:] - characters that are hexadecimal digits.  Brackets are permitted within the set's brackets. For example, [a-z0-9!] is equivalent to [[:lower:][:digit:]!] in the C locale. |
|  [^]  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  Inverts the behavior of a character set [] as described above. For example, [^[:alpha:]] matches any character that is not alphabetical. The ^ caret symbol only has this special meaning when it is the first character in a bracket set.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|  {n}  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    Exactly n occurrences of the previous expression, where 0 <= n <= 255. For example, a{3} matches aaa.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| {n,m} |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     Between n and m occurrences of the previous expression, where 0 <= n <= m <= 255. For example, a 32-bit hexadecimal number can be described as 0x[[:xdigit:]]{1,8}.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| {n,}  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 At least n or more (up to infinity) occurrences of the previous expression.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|   *   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   Zero or more of the previous expression.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|   +   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   One or more of the previous expression.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|   ?   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   Zero or one of the previous expression.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| (exp) |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            Grouping; any series of expressions may be grouped in parentheses so as to apply a postfix or bar (¦) operator to a group of successive expressions. For example:  ab+ matches all of abbb (ab)+ matches all of ababab                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|   ¦   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       Alternate expressions (logical OR). The vertical bar (¦) has the lowest precedence of all tokens in the regular expression language. This means that ab¦cd matches all of cd but does not match abd (in this case use a(b¦c)d ).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
    
      
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

```sh
 ~/tmp  for i in {1..10}; do echo "(${RANDOM:0:3}) ${RANDOM:0:3}-${RANDOM:0:4}" >> phonelist.txt; done             INT
 ~/tmp  cat phonelist.txt                                                                                           ok
(238) 501-1131
(782) 181-1403
(170) 816-1059
(180) 984-1900
(691) 237-1956
(191) 499-5170
(246) 229-1708
(777) 282-3094
(154) 118-2033
(820) 176-1289

~/tmp  grep -Ev '^\([[:digit:]]{3}\)? [[:digit:]]{3}-[[:digit:]]{4}$' phonelist.txt
```


`zgrep '899' phonelist.tar.gz` zgrep 可查询二进制文件是否包含 
grep -rl --binary-file=binary 'exp' .

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
awk '{print}' file
awk -F':' '{print $1}' /etc/passwd
awk '/regexp/ {print $1} file
awk 'BEGIN {} {} END{}' file

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

`find / -regex '.*[^-_./0-9a-zA-Z].*'` find with regex

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

## Text Processing
cat
sort
uniq
cut
paste
join
comm
diff
patch
tr
sed
aspell

## exit status
`echo $?`

`exit` 
`exit 2`
`return 1`

## ps netstat
ps -ef|grep java
ps -aux|grep java
ps -eo pid,vsz,cmd --sort vsz|grep java

netstat -an|grep 80
netstat -an|grep 80|cut -d':' -f 2|cut -b 1-30|sort|uniq