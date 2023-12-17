---
title: spring cloud 配置加密字段
date: 2023-12-17 19:47:50
category:
tags: 
  - spring-cloud
---
> spring cloud 源码解析系列 

[EncryptionBootstrapConfiguration](/blog/repo/spring-cloud-配置加密字段/EncryptionBootstrapConfiguration)

spring cloud rsa 加密 等效为：

```java
KeyProperties keyProperties = new KeyProperties();
keyProperties.getKeyStore()
		.setLocation(new FileUrlResource(Paths.get("src/test/resources/server.jks").toUri().toURL()));
keyProperties.getKeyStore().setAlias("mytestkey");
keyProperties.getKeyStore().setPassword(System.getenv("JKS_PASSWORD"));
keyProperties.getKeyStore().setType("jks");
RsaProperties rsaProperties = new RsaProperties();
rsaProperties.setAlgorithm(RsaAlgorithm.DEFAULT);
rsaProperties.setSalt("bloodybeaf");
rsaProperties.setStrong(false);
TextEncryptor textEncryptor = TextEncryptorUtils.createTextEncryptor(keyProperties, rsaProperties);
String text = "hello world";
String encryptedText = textEncryptor.encrypt(text);
System.out.println(encryptedText);
String decryptedText = textEncryptor.decrypt(encryptedText);
System.out.println(decryptedText);
assertEquals(text, decryptedText);
```

.jks = java keyStore
keystore type : pem / jks

jdk/bin 中自带 keytool 命令

`keytool -genkey -keyalg RSA -alias <alias/username> -keystore keystore.jks -storepass <password> -keypass <password>`


```sh
keytool -genkey -keyalg RSA -alias mytestkey -keystore server.jks -storepass xxx
```

java keystore to pem, **这个工具很好用**
[https://keystore-explorer.org/](https://keystore-explorer.org/)

.pem 为固定格式、base64 的秘钥文件

注意导出时去掉勾选加密！！！


## 避坑
运行eclipse时，添加环境变量到windows ，需要重启eclipse才可以在项目运行时获取到新添加的变量！！！
例如 在 application.properties 中配置了placeholder ${jks_pass}，未重启eclipse时，重新运行application是拿不到该变量的。