---
title: MySQL 8 window functions
date: 2020-07-15 10:12:17
category:
tags: MySQL
---
> MySQL Version: since 8.0

# Window Functions
> A window function is an SQL function where the input values are taken from a "window" of one or more rows in the results set of a SELECT statement.

一个window function 是一个SQL函数，它的input是从一个“SELECT语句结果集中一行或多行的 window”中获取。与普通聚合函数的区别在于它使用关键字 `OVER`。
window functions 不能使用`DISTINCT`关键字，同时，window functions 只能出现在结果集(result set) 和 SELECT 语句的 ORDER BY 中。

## TOP 5 each group
```sql
SELECT t1.project_id, t1.user_id FROM project_user t1 WHERE 5 > (
  SELECT COUNT(*) FROM project_user t2 WHERE t1.project_id=t2.project_id AND t1.user_id>t2.user_id
) ORDER BY project_id, user_id


SELECT * FROM (
  SELECT project_id, user_id, RANK() over (PARTITION BY project_id ORDER BY user_id) as rank_num FROM project_user ORDER BY project_id, user_id
) t WHERE rank_num <= 5 
```

# Reference
[Window Functions](https://www.sqlite.org/windowfunctions.html#:~:text=A%20window%20function%20is%20an,it%20is%20a%20window%20function.)
[MySQL Window Functions](https://www.mysqltutorial.org/mysql-window-functions/)