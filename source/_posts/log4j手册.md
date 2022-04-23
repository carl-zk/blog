---
title: log4j2手册
date: 2017-03-28 22:24:55
category:
tags: log4j2
---
** 参考文献 **
[官网](https://logging.apache.org/log4j/2.x/)
[http://dreamoftch.iteye.com/blog/1899948](http://dreamoftch.iteye.com/blog/1899948)
[最详细的Log4J使用教程](http://www.codeceo.com/article/log4j-usage.html)

> log4j2比log4j1.x[有显著的性能提高](https://logging.apache.org/log4j/2.x/manual/async.html#Performance)，并且增加了许多特性。所以最好使用log4j2。
推荐使用xml文件配置，可以配置一些像properties文件无法配置的功能。
[slf4](https://www.slf4j.org/)The Simple Logging Facade for Java ,是对诸多日志框架(e.g. java.util.logging, logback, log4j) 的外观模式封装，可以不修改源码只通过替换jar包来切换日志框架。

先简单介绍一下slf4j的强大吧，[legacy](https://www.slf4j.org/legacy.html)
![](/2017/03/28/log4j%E6%89%8B%E5%86%8C/slf4j.png)
如图所示，一个应用依赖了外部两个框架，这两个框架分别使用的日志框架是Commons-logging和log4j,而这个应用本身使用的日志框架是jdk14，那么问题来了，如何在我jdk14的日志里看到这两个框架的日志记录呢？
很简单，Commons-logging我使用jcl-over-slf4j.jar来桥接一下，即虽然你调用的是Commons-logging日志接口，但是内部实际使用的是slf4j接口，同理，log4j我使用log4j-over-slf4j.jar来桥接，这样它们实际调用的都是slf4j接口，那我再使用slf4j-jdk14.jar就可以调用jdk14日志了。
在maven中，可以通过这种xxx-slf4j.jar来exclusion多余的日志框架，主要是可以把不同日志框架给统一起来了。
使用时要注意版本对应。

### slf4j + log4j2
#### 依赖
```xml
<properties>
    <log4j2Version>2.8.2</log4j2Version>
</properties>

<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-api</artifactId>
    <version>${log4j2Version}</version>
</dependency>
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-core</artifactId>
    <version>${log4j2Version}</version>
</dependency>
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-slf4j-impl</artifactId>
    <version>${log4j2Version}</version>
</dependency>
```
#### xml配置文件
日志打印级别
```
OFF (most specific, no logging)
FATAL (most specific, little data)
ERROR
WARN
INFO
DEBUG
TRACE (least specific, a lot of data)
ALL (least specific, all data)
```
默认在classpath下，log4j2-test.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Configuration status="WARN">
    <Properties>
        <Property name="LOG_LEVEL" value="WARN"/>
    </Properties>
    <Appenders>
        <Console name="Console" target="SYSTEM_OUT">
            <PatternLayout pattern="%-5level %d{yy-MM-dd HH:mm:ss.SSS} [%t] %logger{36} - %msg%n"/>
        </Console>
    </Appenders>
    <Loggers>
        <Root level="INFO">
            <AppenderRef ref="Console" level="${LOG_LEVEL}"/>
        </Root>
    </Loggers>
</Configuration>
```
log4j2的语法与log4j1.x的有所不同，[log4j2配置文件语法](https://logging.apache.org/log4j/2.x/manual/configuration.html#AutomaticConfiguration)。

#### java中使用
```java
private static final Logger logger = LogManager.getLogger(MyApp.class);

logger.info("name={} passwd={} remember={}", username, password, rememberMe);
```

# @deprecated
## log4j1实例
#### 指定logger,并且不向rootLogger输出
log4j1
```xml
<!-- https://mvnrepository.com/artifact/log4j/log4j -->
<dependency>
    <groupId>log4j</groupId>
    <artifactId>log4j</artifactId>
    <version>1.2.17</version>
</dependency>
```
log4j.properties文件
```properties
log4j.rootLogger=INFO,DAILY_ROLLING_FILE,stdout
#log4j.rootLogger=ERROR,CONSOLE,DAILY_ROLLING_FILE

log4j.appender.stdout=org.apache.log4j.ConsoleAppender
log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
log4j.appender.stdout.layout.ConversionPattern=%d %p [%c] - %m%n

########################
# DailyRolling File
########################
log4j.appender.DAILY_ROLLING_FILE=org.apache.log4j.DailyRollingFileAppender
log4j.appender.DAILY_ROLLING_FILE.Append=true
log4j.appender.DAILY_ROLLING_FILE.Threshold=debug
log4j.appender.DAILY_ROLLING_FILE.Encoding=UTF-8

###\u65e5\u5fd7\u76ee\u5f55\u6587\u4ef6
log4j.appender.DAILY_ROLLING_FILE.File=/home/hero/temp/log.txt
log4j.appender.DAILY_ROLLING_FILE.DatePattern='.'yyyy-MM-dd
log4j.appender.DAILY_ROLLING_FILE.layout=org.apache.log4j.PatternLayout
log4j.appender.DAILY_ROLLING_FILE.layout.ConversionPattern=[%-5p] %d{yyyy-MM-dd HH:mm:ss,SSS} [%c] %m%n

###################
# Console Appender
###################
log4j.appender.CONSOLE=org.apache.log4j.ConsoleAppender
log4j.appender.Threshold=debug
log4j.appender.CONSOLE.Target=System.out
log4j.appender.CONSOLE.layout=org.apache.log4j.PatternLayout
log4j.appender.CONSOLE.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss} %5p (%c:%L) - %m%n

## 配置MYOWNLOG,在LogManager.getLogger("MYOWNLOG")中指定这个logger
log4j.logger.MYOWNLOG=INFO,specifylog
log4j.appender.specifylog=org.apache.log4j.FileAppender
log4j.appender.specifylog.File=/home/hero/temp/test2.log
log4j.appender.specifylog.layout=org.apache.log4j.PatternLayout
log4j.appender.specifylog.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss} %5p (%F:%L) - %m%n
log4j.appender.specifylog.Encoding=UTF-8
## 不输出到rootLogger
log4j.additivity.MYOWNLOG = false
```
```java
package common;

import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;

/**
 * Created by hero on 17-3-28.
 */
public class Log4jTest {
    static Logger logger = LogManager.getLogger(Log4jTest.class);

    public static void main(String[] args) {
        logger.info("hello");
        Logger logge = LogManager.getLogger("MYOWNLOG");
        logge.info("world");
        try {
            throw new IllegalArgumentException("abcefg");
        } catch (Exception ex) {
            logge.error("fjsdlajflaj", ex);
        }
    }
}
```