---
title: Logger 桥接模式
date: 2022-01-09 17:35:33
category:
tags: log4j2
---
> 好久不写博客了，准备水一篇。

之前写过一篇关于slf4j的文章[Log4j2手册](/blog/2017/03/28/log4j手册/)，今天就来分析一下代码。

源码：[https://github.com/carl-zk/example-logger](https://github.com/carl-zk/example-logger)

### 开始实验
首先引入 `commons-logging`  
```xml
<dependency>
    <groupId>commons-logging</groupId>
    <artifactId>commons-logging</artifactId>
    <version>1.2</version>
</dependency>
```
写一个logger
```java
@Test
public void commons_logging_directly() {
    Log log = LogFactory.getLog(Tests.class);
    log.info("commons_logging_directly");
}
```

正常打印，ok, perfect!

引入 `log4j2`
```xml
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-api</artifactId>
    <version>2.17.1</version>
</dependency>
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-core</artifactId>
    <version>2.17.1</version>
</dependency>
```

```java
@Test
public void log4j2_logging_directly() {
    Logger logger = LogManager.getLogger(Tests.class);
    logger.info("log4j2_logging_directly");
}
```

打印正常！（需添加配置文件log4j2.xml）

引入桥接 `log4j-jcl`
```xml
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-jcl</artifactId>
    <version>2.17.1</version>
</dependency>
```

它的作用是将使用commons-logging包的log记录的信息通过log4j输出出去。

```java
@Test
public void commons_logging_via_log4j() {
    Log log = LogFactory.getLog(Tests.class);
    log.info("commons_logging_via_log4j");
}
```

ok，打印的信息是log4j的输出格式，但调用的方法仍然是commons-logging的。


### 源码分析
废话不说，直接上代码！（这本身就是句废话，不知道为啥老是有人这么说，我来吐槽一下）
如图，桥接器使用[SPI](https://www.baeldung.com/java-spi)模式实现，
![](/2022/01/09/Logger-%E6%A1%A5%E6%8E%A5%E6%A8%A1%E5%BC%8F/log4j-jcl.png)

`LogFactoryImpl`继承了`org.apache.commons.logging.LogFactory`，通过`LogAdapter`来生成log。
```java
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogConfigurationException;
import org.apache.commons.logging.LogFactory;
import org.apache.logging.log4j.spi.LoggerAdapter;

/**
 * Log4j binding for Commons Logging.
 * {@inheritDoc}
 */
public class LogFactoryImpl extends LogFactory {

    private final LoggerAdapter<Log> adapter = new LogAdapter();

    private final ConcurrentMap<String, Object> attributes = new ConcurrentHashMap<>();

    @Override
    public Log getInstance(final String name) throws LogConfigurationException {
        return adapter.getLogger(name);
    }
```

`LogAdapter` 返回`Log4jLog`对象，
```java
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.spi.AbstractLoggerAdapter;
import org.apache.logging.log4j.spi.LoggerContext;
import org.apache.logging.log4j.util.StackLocatorUtil;

/**
 * Commons Logging adapter registry.
 *
 * @since 2.1
 */
public class LogAdapter extends AbstractLoggerAdapter<Log> {

    @Override
    protected Log newLogger(final String name, final LoggerContext context) {
        return new Log4jLog(context.getLogger(name));
    }

    @Override
    protected LoggerContext getContext() {
        return getContext(LogManager.getFactory().isClassLoaderDependent()
                ? StackLocatorUtil.getCallerClass(LogFactory.class)
                : null);
    }

}
```

`Log4jLog` 实现 `org.apache.commons.logging.Log` 接口，内部组合了一个`ExtendedLogger`（就是log4j的基类），接口的实现方法都是使用的它来实现。
```java
import org.apache.commons.logging.Log;
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.spi.ExtendedLogger;

/**
 *
 */
public class Log4jLog implements Log, Serializable {

    private static final long serialVersionUID = 1L;
    private static final String FQCN = Log4jLog.class.getName();

    private final ExtendedLogger logger;

    public Log4jLog(final ExtendedLogger logger) {
        this.logger = logger;
    }
    @Override
    public boolean isDebugEnabled() {
        return logger.isEnabled(Level.DEBUG, null, null);
    }
```

既然是SPI，那自然需要知道在哪里load这个`LogFactoryImpl`。
下面来看一下`org.apache.commons.logging.LogFactory`，这里的`SERVICE_ID="META-INF/services/org.apache.commons.logging.LogFactory"`，通过反射最终拿到实现类`LogFactoryImpl`。

```java
public static LogFactory getFactory() throws LogConfigurationException {
    ...
    if (factory == null) {
        if (isDiagnosticsEnabled()) {
            logDiagnostic("[LOOKUP] Looking for a resource file of name [" + SERVICE_ID +
                          "] to define the LogFactory subclass to use...");
        }
        try {
            final InputStream is = getResourceAsStream(contextClassLoader, SERVICE_ID);

            if( is != null ) {
                // This code is needed by EBCDIC and other strange systems.
                // It's a fix for bugs reported in xerces
                BufferedReader rd;
                try {
                    rd = new BufferedReader(new InputStreamReader(is, "UTF-8"));
                } catch (java.io.UnsupportedEncodingException e) {
                    rd = new BufferedReader(new InputStreamReader(is));
                }

                String factoryClassName = rd.readLine();
                rd.close();

                if (factoryClassName != null && ! "".equals(factoryClassName)) {
                    if (isDiagnosticsEnabled()) {
                        logDiagnostic("[LOOKUP]  Creating an instance of LogFactory class " +
                                      factoryClassName +
                                      " as specified by file '" + SERVICE_ID +
                                      "' which was present in the path of the context classloader.");
                    }
                    factory = newFactory(factoryClassName, baseClassLoader, contextClassLoader );
                }
            } else {
                // is == null
                if (isDiagnosticsEnabled()) {
                    logDiagnostic("[LOOKUP] No resource file with name '" + SERVICE_ID + "' found.");
                }
            }
        } catch (Exception ex) {
            // note: if the specified LogFactory class wasn't compatible with LogFactory
            // for some reason, a ClassCastException will be caught here, and attempts will
            // continue to find a compatible class.
            if (isDiagnosticsEnabled()) {
                logDiagnostic(
                    "[LOOKUP] A security exception occurred while trying to create an" +
                    " instance of the custom factory class" +
                    ": [" + trim(ex.getMessage()) +
                    "]. Trying alternative implementations...");
            }
            // ignore
        }
    }
    ...
```
另外，这个方法查找的优先级如下，查到就返回，否则顺序向下，SPI位于第二，最后一个是commons-logging自己。

- The org.apache.commons.logging.LogFactory system property.
- The JDK 1.3 Service Discovery mechanism
- Use the properties file commons-logging.properties file, if found in the class path of this class. The configuration file is in standard java.util.Properties format and contains the fully qualified name of the implementation class with the key being the system property defined above.
- Fall back to a default implementation class (org.apache.commons.logging.impl.LogFactoryImpl).

至此，在没有改动任何代码的前提下，仅仅通过引入`log4j-jcl`jar就能将`org.apache.commons.logging.LogFactory`的实现类从`org.apache.commons.logging.impl.LogFactoryImpl` 变成了`org.apache.logging.log4j.jcl.LogFactoryImpl`，从而`Log log = LogFactory.getLog(Tests.class);`获得的是`org.apache.logging.log4j.jcl.Log4jLog`，调用`log.info()`其实是`Log4jLog`的实现方法，其内部是组合了一个log4j的实现类`ExtendedLogger`，最终日志是通过log4j输出的。

要看到commons-logging的更多信息，可以加参数`-Dorg.apache.commons.logging.diagnostics.dest=STDOUT`.

由此可见，日志框架都有自己的规则：作为一个日志框架，本身要支持SPI这种模式。要兼容另一种日志框架，则另外提供一个桥接工具包，使用组合的方式将自己封装起来。slf4j作为统一的标准日志接口，其目的就是起到桥接任何日志框架的目的，最终归于一个具体实现类日志框架。后面如果自己写个框架，日志类只需引入slf4j，使用这个框架的项目只需引入`log4j-slf4j18-impl`即可。

slf4j的实现类只可以绑定一个，更多信息refer [slf4.org](https://www.slf4j.org/manual.html).

### 参考
[log4j官网](https://logging.apache.org/log4j/2.x/log4j-jcl/index.html)


