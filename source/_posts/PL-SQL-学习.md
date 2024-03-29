---
title: PL/SQL 学习
date: 2017-06-21 23:41:31
category:
tags: oracle
---
[Oracle Install](http://carl-zk.github.io/blog/2017/06/17/Oracle-Install/)看起来实在有点长。

#### PL/SQL函数编写
特性：函数被调用一次之后就会被缓存在服务器！
查看有哪些函数    USER_PROCEDURES
`SELECT * FROM USER_PROCEDURES;`
`SELECT OBJECT_NAME, OBJECT_ID, OBJECT_TYPE FROM USER_PROCEDURES ORDER BY OBJECT_TYPE;`
查看具体函数source     USER_SOURCE
``
`SELECT NAME, LINE, TEXT FROM USER_SOURCE WHERE NAME='FINDGIRL';`

```SQL
--- PL/SQL 函数编写

-- 开启在屏幕显示
SET SERVEROUTPUT ON;
-- CREATE OR REPLACE
CREATE FUNCTION FINDGIRL   
-- IN OUT
(SEX IN CHAR)   
RETURN VARCHAR2
IS
BEGIN
IF SEX='1' THEN
  --DBMS_OUTPUT.PUT_LINE('HH, FIND A GIRL');
  RETURN ('GIRL');
ELSE
  --DBMS_OUTPUT.PUT_LINE('EEE, NOT SO LUCKY');
  RETURN('COW SHIT');
END IF;
END;
/

SELECT NAME, SEX, FINDGIRL(SEX) FROM STUDENT;
--删除函数
DROP FUNCTION FINDGIRL;   
EXIT;
```
#### PL/SQL游标
分为静态游标和动态游标，这里是静态游标举例。
所谓静态，就是结果集为静态，数据库中的CRUD对它没有影响。

##### 显式游标
在数据量少的情况下，可以使用FETCH ... INTO,它是一条一条赋值的。
当数据量很大的情况下，使用更高效率的FETCH ... BULK COLLECT INTO.
`注意两种方法EXIT的位置。`
```sql
-- PL/SQL 游标

-- 开启在屏幕显示
SET SERVEROUTPUT ON;

DECLARE
  CURSOR CUR_STUDENT
  IS SELECT * FROM STUDENT;
  V_STUDENT STUDENT%ROWTYPE;
BEGIN
  OPEN CUR_STUDENT;
  LOOP
    FETCH CUR_STUDENT INTO V_STUDENT;
    -- 退出
    EXIT WHEN CUR_STUDENT%NOTFOUND; 
    DBMS_OUTPUT.PUT_LINE('result : ' || V_STUDENT.NAME);
  END LOOP;
  CLOSE CUR_STUDENT;
END;
/
EXIT;
```

```sql
-- PL/SQL 游标

-- 开启在屏幕显示
SET SERVEROUTPUT ON;

DECLARE
  CURSOR CUR_STUDENT
  IS SELECT * FROM STUDENT;
  TYPE TYPE_MAP_STUDENT IS TABLE OF STUDENT%ROWTYPE;
  V_STUDENT TYPE_MAP_STUDENT;
BEGIN
  OPEN CUR_STUDENT;
  LOOP
    -- 限制一次取3条
    FETCH CUR_STUDENT BULK COLLECT INTO V_STUDENT LIMIT 3;
    FOR I IN 1..V_STUDENT.COUNT LOOP
      DBMS_OUTPUT.PUT_LINE('result : ' || V_STUDENT(I).NAME);
    END LOOP;
    -- 退出
    EXIT WHEN CUR_STUDENT%NOTFOUND; 
  END LOOP;
  CLOSE CUR_STUDENT;
END;
/
EXIT;
```
![](/2017/06/21/PL-SQL-%E5%AD%A6%E4%B9%A0/bulk.PNG)

结果集很多都需要遍历，这里有一种更简便的遍历方式，不用声明其它变量、开/关游标。
FOREACH LOOP

```sql
-- PL/SQL 游标

-- 开启在屏幕显示
SET SERVEROUTPUT ON;

DECLARE
  CURSOR CUR_STUDENT
  IS SELECT * FROM STUDENT;

BEGIN
  FOR CUR IN CUR_STUDENT LOOP
    DBMS_OUTPUT.PUT_LINE('NAME : ' || CUR.NAME);
  END LOOP;
END;
/
EXIT;
```

**显式游标的属性**
%ISOPEN
%FOUND
%NOTFOUND
%ROWCOUNT累计到当前为止，使用FETCH提取数据的行数

ISOPEN的使用
```sql
-- PL/SQL 游标

-- 开启在屏幕显示
SET SERVEROUTPUT ON;

DECLARE
  CURSOR CUR_STUDENT
  IS SELECT * FROM STUDENT;
  V_STUDENT STUDENT%ROWTYPE;
BEGIN
  IF CUR_STUDENT%ISOPEN THEN
    FETCH CUR_STUDENT INTO V_STUDENT;
      DBMS_OUTPUT.PUT_LINE('NAME : ' || V_STUDENT.NAME);
  ELSE
    DBMS_OUTPUT.PUT_LINE('cursor is not open');
  END IF;
END;
/
EXIT;
```

FOUND的使用
```sql
-- PL/SQL 游标

-- 开启在屏幕显示
SET SERVEROUTPUT ON;

DECLARE
  CURSOR CUR_STUDENT
  IS SELECT * FROM STUDENT;
  V_STUDENT STUDENT%ROWTYPE;
BEGIN
  OPEN CUR_STUDENT;
  LOOP
    FETCH CUR_STUDENT INTO V_STUDENT;
    DBMS_OUTPUT.PUT_LINE(CUR_STUDENT%ROWCOUNT || 'ROWS');
    IF CUR_STUDENT%FOUND THEN
      DBMS_OUTPUT.PUT_LINE(V_STUDENT.NAME);
    ELSE
      DBMS_OUTPUT.PUT_LINE('no data found');
      EXIT;
    END IF;
  END LOOP;
  CLOSE CUR_STUDENT;
END;
/
EXIT;
```

**带参数的游标**
找出id=1的学生。
```sql
-- PL/SQL 游标

-- 开启在屏幕显示
SET SERVEROUTPUT ON;

DECLARE
  CURSOR CUR_STUDENT (SID NUMBER)
  IS SELECT * FROM STUDENT WHERE ID=SID;
  V_STUDENT STUDENT%ROWTYPE;
BEGIN
  OPEN CUR_STUDENT(1);
  LOOP
    FETCH CUR_STUDENT INTO V_STUDENT;
    IF CUR_STUDENT%FOUND THEN
      DBMS_OUTPUT.PUT_LINE(V_STUDENT.NAME);
    ELSE
      DBMS_OUTPUT.PUT_LINE('no data found');
      EXIT;
    END IF;
  END LOOP;
  CLOSE CUR_STUDENT;
END;
/
EXIT;
```

##### 隐式游标
隐式游标由PL/SQL自动管理，默认名称为SQL。
```sql
SET SERVEROUTPUT ON;

DECLARE
  V_STUDENT STUDENT%ROWTYPE;
BEGIN
  SELECT * INTO V_STUDENT FROM STUDENT WHERE ID=2;
  IF SQL%FOUND THEN
    DBMS_OUTPUT.PUT_LINE(V_STUDENT.NAME);
  END IF;
END;
/
EXIT;
```