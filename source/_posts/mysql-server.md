---
title: mysql server
date: 2018-04-06 19:21:31
category: 系统配置
tags: MySQL
---
#### 忘记 root 密码
> mysql server version : 5.7.9+

查找MySQL sever 安装位置
sudo find / -name "mysqld"

1. 停服务
ps -ef|grep mysql
sudo kill -9 pid1 pid2			
2. 重启
```
mysqld_safe --skip-grant-tables &
```
3. 登录
mysql -u root 
4. 重置密码
use mysql;
update user set authentication_string='password', password_expired = 'N' where User ='root' and Host='localhost';
flush privileges;
exit;
停服务重新登录即可
sudo mysqld -uroot &

注意：Mac 上通过 System Preferences 启动的 server，其启动参数 -u 为 _mysql，在上述第2步之后，第3步改为
mysql -u _mysql
grant all privileges on *.* to 'root'@'%' identified by 'password' with grant option;

#### 数据迁移
##### 导出工具
[MySQL数据导出](http://www.runoob.com/mysql/mysql-database-export.html)
###### mysqldump
1. 导出 sql
```sql
mysqldump -hhost -uroot -ppassword --single-transaction schema table -r 
dump.sql
```
导入：
```sql
mysql -uroot -p
>use databases;
>source /path/to/dump.sql
```
2. 导出 tab
mysqldump -hhost -uroot -ppassword --tab=/Users/hero/tmp --fields-terminated-by='^!' --lines-terminated-by='\n' --single-transaction schema table

##### 比较工具 
```
mysqldbcompare --server1=root:密码@IP:3306 --server2=root:passwd@ip:3306 --difftype=sql schema1:schema2
```
 如果schema含有非字母字符，
 --difftype=sql "\`nh-rel-x\`:\`nh-rel-x\`" --run-all-tests > ~/tmp/res.txt

#### 比较脚本
> 场景：在不影响生产的情况下拿A库与B库做比较，A与B分别在两个地方，用otter做了实时同步。但是otter有问题，不知道哪些数据同步有问题，所以需要逐表比对一下。

```sql
. /Users/hero/.zshrc
# 取所有表名
echo `mysql -uuser -ppasswd -hhost <<EOF
SELECT table_name FROM information_schema.tables where table_schema='nh-rel-x' and table_name like 'nh%' and table_name not like '%_reference';
EOF` > tables.txt

sed -E -e 's/\t/ /g' -e 's/ +/\n/g' tables.txt | tail -n +2 > alltables.txt
rm tables.txt
```

```sql
. /Users/hero/.zshrc
#from
url_from=
user_from=
password_from=
schema_from=
#to
url_to=
user_to=
password_to=
schema_to=

rm -rf from
mkdir from
rm -rf to
mkdir to
rm -rf diff
mkdir diff

for i in `cat alltables.txt`; do
  echo "`date '+%H:%M:%S'` compare table ---> "$i"\n"
  mysqldump -h$url_from -u$user_from -p$password_from --single-transaction $schema_from $i -r from/${i}
  mysqldump -h$url_to -u$user_to -p$password_to --single-transaction $schema_to $i -r to/${i}
  grep "^INSERT" from/${i} | sed -e 's/INSERT.*VALUES //g' -e 's/),/)\n/g' -e 's/);/)\n/g' > from/${i}.ok
  grep "^INSERT" to/${i} | sed -e 's/INSERT.*VALUES //g' -e 's/),/)\n/g' -e 's/);/)\n/g' > to/${i}.ok
  diff from/${i}.ok to/${i}.ok > diff/$i
done

find diff/ -empty -delete

>report.txt
tabs=`ls diff/`
for t in $tabs; do
  shanghai=`grep -c "^<" diff/$t`
  hongkong=`grep -c "^>" diff/$t`
  echo $t  $shanghai  $hongkong >> report.txt
done
sort -n -k 2 report.txt
```
#### mm
`mysql -uroot -ppassword < init.sql`
init.sql
```sql
use mydb;
#创建用户表
CREATE TABLE t_user (
    id INT auto_increment PRIMARY KEY,
        name VARCHAR(30),
        password varchar(64),
        credits INT
)ENGINE=INNODB;
#创建登录日志表
create TABLE t_login_log (
      id int auto_increment PRIMARY KEY,
        user_id int,
        ip varchar(23),
        login_datetime datetime
)ENGINE=INNODB;
```



