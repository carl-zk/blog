---
title: java html template tool
date: 2019-02-19 00:12:35
category: java
tags: freemarker
---
一个好用的处理 html template 的工具：
[freemarker](https://freemarker.apache.org/docs/pgui_quickstart_all.html)

hello.ftlh
```html
<html>
<head>
    <title>Welcome!</title>
</head>
<body>
<#-- Greet the user with his/her name -->
<h1>Welcome ${user}!</h1>
<p>We have these animals:
<ul>
    <#list animals as animal>
      <li>${animal.name} for ${animal.price} Euros
    </#list>
</ul>
</body>
</html>
```

```java
import freemarker.template.Configuration;
import freemarker.template.Template;
import freemarker.template.TemplateException;
import freemarker.template.TemplateExceptionHandler;

import java.io.File;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.util.LinkedList;
import java.util.List;

public class Main {
    public static void main(String[] args) throws IOException, TemplateException {
        Configuration cfg = new Configuration(Configuration.VERSION_2_3_28);
        cfg.setDirectoryForTemplateLoading(new File("/Users/carl/workspace/freemarker/src/main/resources/templates"));
        cfg.setDefaultEncoding("UTF-8");
        cfg.setTemplateExceptionHandler(TemplateExceptionHandler.HTML_DEBUG_HANDLER);
        cfg.setLogTemplateExceptions(false);
        cfg.setWrapUncheckedExceptions(true);

        Template temp = cfg.getTemplate("hello.ftlh");

        DataModel root = new DataModel();

        root.setUser("小红");

        List<Animal> animals = new LinkedList<Animal>();
        animals.add(new Animal("a", "12"));
        animals.add(new Animal("b", "12"));

        root.setAnimals(animals);

        Writer out = new OutputStreamWriter(System.out);
        temp.process(root, out);
    }
}

public class Animal {
    private String name;
    private String price;
}

public class DataModel {
    private String user;
    private List<Animal> animals;
}
```

console:
```sh
<html>
<head>
    <title>Welcome!</title>
</head>
<body>
<h1>Welcome 小红!</h1>
<p>We have these animals:
<ul>
      <li>a for 12 Euros
      <li>b for 12 Euros
</ul>
</body>
</html>

```