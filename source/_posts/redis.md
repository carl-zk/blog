---
title: redis
date: 2018-04-26 09:14:31
category:
tags: redis
---
> docker run --rm -p 6379:6379 redis --requirepass "password"
> 注意：redis-cli 连接需密码的server时，不输密码也可以进入命令模式，只有当执行命令时才报错。

## Redis 安装启动
[download](https://redis.io/download)
```sh
mv redis.tar.gz /redis
tar xvzf redis.tar.gz
mv redis-4.0 server
cd server
make
make test
cd ..
cp server/redis.conf .
cp server/utils/redis_init_script .
```

目录结构：
```
/redis
    /server
    /storage
    redis.conf
    redis_init_script
    start
    stop
```

redis.conf
```sh
port 6397
pidfile /redis/redis_${port}.pid
logfile "/redis/my.log"
dir /redis/storage
#bind 127.0.0.1
requirepass password

```

redis_init_script
```sh
#!/bin/sh
#
# Simple Redis init.d script conceived to work on Linux systems
# as it does use of the /proc filesystem.

REDISPORT=6397
PASSWORD=password
EXEC=/redis/server/src/redis-server
CLIEXEC=/redis/server/src/redis-cli

PIDFILE=/redis/redis_${REDISPORT}.pid
CONF="/redis/redis.conf"

case "$1" in
    start)
        if [ -f $PIDFILE ]
        then
                echo "$PIDFILE exists, process is already running or crashed"
        else
                echo "Starting Redis server..."
                $EXEC $CONF
        fi
        ;;
    stop)
        echo "Stopping ..."
        $CLIEXEC -p $REDISPORT -a $PASSWORD shutdown
        while [ -x /proc/${PID} ]; do
            echo "Waiting for Redis to shutdown ..."
            sleep 1
            done
        echo "Redis stopped"
        ;;
    *)
        echo "Please use start or stop as first argument"
        ;;
esac
```
运行起来没有看到pid文件，所以修改了stop分支。(原来只有daemonize yes时才有pid文件)

start
```sh
#!/bin/sh

/redis/redis_init_script start &

ps -ef | grep redis-server
```

stop
```sh
#!/bin/sh

/redis/redis_init_script stop

ps -ef | grep redis-server
```

### 主从复制
Redis-Server(Main)
 - Redis-Server(Slave)
 - Redis-Server(Slave)
 - Redis-Server(Slave)
一台主机作为写入，三台从机作为读取，这样就缓解了主机的压力。
Redis支持两种方式的主从配置：
1. redis.conf；
2. cli.slaveOf(ip:port)


实验中发现即使kill -9 主机，从机还是可以读到值。只能证明Redis能处理kill方式的停机，并不能保证宕机时也能如此优雅。

[Redis集群](https://blog.csdn.net/u011204847/article/details/51307044)
大神的博客，需要好好拜读。

## Redis实现锁的简单方法
[SET](http://redisdoc.com/string/set.html)
参考[Redis分布式锁的正确实现方式](https://mp.weixin.qq.com/s/XoXcqpehhXSQlRxgCBtDcw)

`SET key value [EX seconds] [PX milliseconds] [NX|XX]`
```
EX second ：设置键的过期时间为 second 秒。 SET key value EX second 效果等同于 SETEX key second value 。
PX millisecond ：设置键的过期时间为 millisecond 毫秒。 SET key value PX millisecond 效果等同于 PSETEX key millisecond value 。
NX ：只在键不存在时，才对键进行设置操作。 SET key value NX 效果等同于 SETNX key value 。
XX ：只在键已经存在时，才对键进行设置操作。
```

```java
package moc.oreh.common;

import redis.clients.jedis.Jedis;

import java.util.concurrent.TimeUnit;

/**
 * Stateless Redis Lock
 * <p>
 * examples:
 * 1. tryLock
 * <p>
 * boolean got = JedisLock.tryLock(key, token, time, TimeUnit, jedis);
 * if (got) {
 * try {
 * // do something
 * } finally {
 * JedisLock.unlock(key, token, jedis);
 * }
 * }
 * <p>
 * 2. lock
 * <p>
 * JedisLock.lock(key, token, jedis);
 * try {
 * <p>
 * } finally {
 * JedisLock.unlock(key, token, jedis);
 * }
 */
public class JedisLock {
    /**
     * @param key
     * @param token
     * @param jedis
     */
    public static boolean unlock(String key, String token, Jedis jedis) {
        String script = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end";
        Object result = jedis.eval(script, Collections.singletonList(lockKey), Collections.singletonList(requestId));

        if (RELEASE_SUCCESS.equals(result)) {
            return true;
        }
        return false;
    }

    /**
     * @param key
     * @param token
     * @param jedis
     * @return 
     */
    public static void lock(String key, String token, Jedis jedis) {
        isValidKey(key, jedis);
        while (!tryLock(key, token, jedis)) {
            try {
                TimeUnit.MILLISECONDS.sleep(INTERVAL_IN_MILLIS);
            } catch (InterruptedException e) {
            }
        }
    }

    private static void isValidKey(String key, Jedis jedis) {
        long ttl = jedis.ttl(key);
        if (ttl == -1) {
            String val = jedis.get(key);
            throw new Error("redis lock encounter an unexpired key : " + key + ", value : " + val);
        }
    }

    private static final int INTERVAL_IN_MILLIS = 1;

    /**
     * @param key
     * @param token
     * @param timeout
     * @param timeUnit
     * @param jedis
     * @return
     */
    public static boolean tryLock(String key, String token, long timeout, TimeUnit timeUnit, Jedis jedis) {
        timeout = TimeUnit.MILLISECONDS.convert(timeout, timeUnit);
        boolean got = tryLock(key, token, jedis);

        while (!got && timeout > 0) {
            try {
                TimeUnit.MILLISECONDS.sleep(1);
            } catch (InterruptedException e) {
                return false;
            }
            got = tryLock(key, token, jedis);
            timeout -= INTERVAL_IN_MILLIS;
        }
        return got;
    }

    public static final int EXPIRED_TIME_IN_SECONDS = 60;

    private static boolean tryLock(String key, String token, Jedis jedis) {
        String got = jedis.set(key, token, "NX", "EX", EXPIRED_TIME_IN_SECONDS);
        return "OK".equals(got);
    }
}

```
此锁的特点：
1. 独占式、不可重入；
2. tryLock 响应中断的方式为直接返回false；
3. EXPIRED_TIME_IN_SECONDS 为 60，可根据业务场景做相应修改；

为什么会这样设计？
借助Redis的set实现的锁，旨在于保持Redis高速特性的同时具有一定的并发控制，
1. 没有重入场景；
2. 没有wait、notify机制，并且wait具有时效性，可以不响应中断，但是为了方便停服务，所以直接return false；
3. 为什么不使用set(key, token, "NX")而要给锁加一个过期时间？是因为如果a、b共用一个Redis server，其中a突然挂了，那么a设置的key就永远都不过期，b就永远拿不到这个key的锁。
4. redis server单节点，多节点情况下不保证一致性，所以一般使用zookeeper。

适用于竞争不激烈的场景，如果对锁的竞争很激烈，或者需要重入，请使用Redisson。

Redis 连接池
```java
JedisPoolConfig config = new JedisPoolConfig();
config.setMaxTotal(100);
config.setMaxIdle(50);
config.setMinIdle(10);
pool = new JedisPool(config, "localhost", 6397);

Jedis jedis = pool.getResource();        
```
[JedisTest](/blog/2018/04/26/redis/JedisTest.txt)

## Redis-Client
[redis client jedis](https://github.com/xetorthio/jedis/wiki/AdvancedUsage)
small、easy to use.

[redis client redisson](https://github.com/redisson/redisson)
感觉就像是对着jdk的API重写了一遍Redis版的实现一样。为了实现tryLock(time, timeUnit)接口，它在内部使用了Redis的pub/sub框架，这样就可以实现wait/notify机制，虽然原本我也想这么搞来着，但是这样的实现太“重”，现有业务暂时用不到。

[redis client lettuce-core](https://github.com/lettuce-io/lettuce-core)
看粉丝的数量远不如redisson，但是它跟redisson的功能不同，它更适合事件驱动的应用，底层用了netty。事件驱动的应用最适合用它了。









