---
title: generate class with freemarker
date: 2020-11-01 17:33:42
category:
tags: freemarker
---
[freemarker](https://freemarker.apache.org/docs/ref_directive_list.html)是一个Java template engine，可以基于模板+Data生成对应的HTML web pages, e-mails, configuration files, source code, etc.文件。

```xml
<dependency>
    <groupId>org.freemarker</groupId>
    <artifactId>freemarker</artifactId>
    <version>2.3.30</version>
</dependency>
```

```java
package freemaker.second;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import freemarker.template.Configuration;
import freemarker.template.Template;
import freemarker.template.TemplateException;
import freemarker.template.Version;

/**
 * https://dzone.com/articles/automated-webservice-code-generation-using-freemar
 */
public class WebServiceGenerator {

    private static WebServiceGenerator engine = new WebServiceGenerator();
    private Template template = null;
    Map<String, Object> dataMap = new HashMap<>();

    private WebServiceGenerator() {
        try {
            init();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void init() throws IOException {

        Configuration cfg = new Configuration(new Version(2, 3, 30));
        String path = Thread.currentThread().getContextClassLoader().getResource("templates").getPath();
        cfg.setDirectoryForTemplateLoading(new File(path));
        try {
            template = cfg.getTemplate("class.ftl");
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }

    }

    public static WebServiceGenerator get() {
        return engine;
    }

    public WebServiceGenerator buildData() {
        dataMap.put("package", this.getClass().getPackage() + ";");
        dataMap.put("name", "HelloWorldservice");
        dataMap.put("return", "String");
        dataMap.put("methodname", "hello");
        dataMap.put("params", "String name");
        dataMap.put("body", "String res= \"Hi\" + name;\n System.out.println(res);");
        dataMap.put("val", "res;");
        System.out.println("Preparing Data");


        return engine;
    }

    public void writeFile() {
        Writer file = null;
        try {
            file = new FileWriter(new File("HelloWorldservice.java"));
            template.process(dataMap, file);
            file.flush();
            System.out.println("Success");

        } catch (Exception e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        } finally {

            try {
                file.close();
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
        }

    }


    public static void main(String[] args) {

        WebServiceGenerator.get().buildData().writeFile();

    }

}
```

class.ftl
```
${package}

import javax.jws.*;

@WebService()
public class ${name}
{

@WebMethod()
public ${return} ${methodname}(${params})
{
   ${body}
   return ${val}
}

}
```

output:
```java
package freemaker.second;

import javax.jws.*;

@WebService()
public class HelloWorldservice {

    @WebMethod()
    public String hello(String name) {
        String res = "Hi" + name;
        System.out.println(res);
        return res;
    }
}
```
# reference
https://dzone.com/articles/automated-webservice-code-generation-using-freemar