```java
package org.springframework.cloud.bootstrap.encrypt;

import org.springframework.beans.factory.NoSuchBeanDefinitionException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.condition.ConditionOutcome;
import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingClass;
import org.springframework.boot.autoconfigure.condition.SpringBootCondition;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.cloud.context.encrypt.EncryptorFactory;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ConditionContext;
import org.springframework.context.annotation.Conditional;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.env.Environment;
import org.springframework.core.type.AnnotatedTypeMetadata;
import org.springframework.security.crypto.encrypt.TextEncryptor;
import org.springframework.security.rsa.crypto.RsaSecretEncryptor;
import org.springframework.util.StringUtils;

/**
 * @author Dave Syer
 *
 */
@Configuration(proxyBeanMethods = false)
@ConditionalOnClass({ TextEncryptor.class })
@EnableConfigurationProperties
public class EncryptionBootstrapConfiguration {

	/**
		@EnableConfigurationProperties 和 @ConfigurationProperties(KeyProperties.PREFIX) 一起，
		就可以从配置文件读配置来初始化 KeyProperties，非常有用
		KeyProperties 要放到 @Configuration 下，+ @Bean
		两种初始化模式：setter / constructor
		constructer 时， 在构造方法上加 @ContructorBinding 
	*/
	@Bean
	@ConditionalOnMissingBean
	public KeyProperties keyProperties() {
		prefix : encrypt
		对称加密 
		return new KeyProperties();
	}

	@Bean
	public EnvironmentDecryptApplicationInitializer environmentDecryptApplicationListener(
			ConfigurableApplicationContext context, KeyProperties keyProperties) {
		TextEncryptor encryptor;
		try {
			以 rsa 配置为例，就是拿 RsaSecretEncryptor
			encryptor = context.getBean(TextEncryptor.class);
		}
		catch (NoSuchBeanDefinitionException e) {
			encryptor = new TextEncryptorUtils.FailsafeTextEncryptor();
		}
		开始初始化 applicationContext 时，它负责把加密的字段解密
		EnvironmentDecryptApplicationInitializer listener = new EnvironmentDecryptApplicationInitializer(encryptor);
		listener.setFailOnError(keyProperties.isFailOnError());
		return listener;
	}

	@Configuration(proxyBeanMethods = false)
	@Conditional(KeyCondition.class)
	@ConditionalOnClass(RsaSecretEncryptor.class)
	@EnableConfigurationProperties
	protected static class RsaEncryptionConfiguration {

		@Bean
		@ConditionalOnMissingBean
		public RsaProperties rsaProperties() {
			encrypt.rsa
			非对称加密
			return new RsaProperties();
		}

		@Bean
		@ConditionalOnMissingBean(TextEncryptor.class)
		public TextEncryptor textEncryptor(KeyProperties keyProperties, RsaProperties rsaProperties) {
			核心：
			根据加密配置生成加密Bean
			上面 EnvironmentDecryptApplicationInitializer Bean 就是拿的它
			return TextEncryptorUtils.createTextEncryptor(keyProperties, rsaProperties);
		}

	}

	@Configuration(proxyBeanMethods = false)
	@Conditional(KeyCondition.class)
	@ConditionalOnMissingClass("org.springframework.security.rsa.crypto.RsaSecretEncryptor")
	protected static class VanillaEncryptionConfiguration {
		在缺失 RsaSecretEncryptor.class 的情况下，满足加密条件时
		@Autowired
		private KeyProperties key;

		@Bean
		@ConditionalOnMissingBean(TextEncryptor.class)
		public TextEncryptor textEncryptor() {
            aes 加密
			return new EncryptorFactory(this.key.getSalt()).create(this.key.getKey());
		}

	}

	/**
	 * A Spring Boot condition for key encryption.
	 */
	public static class KeyCondition extends SpringBootCondition {

		显然，有对应配置启动对应初始类，分为 async / sync 两种加密方式
		@Override
		public ConditionOutcome getMatchOutcome(ConditionContext context, AnnotatedTypeMetadata metadata) {
			Environment environment = context.getEnvironment();
			if (hasProperty(environment, "encrypt.key-store.location")) {
				if (hasProperty(environment, "encrypt.key-store.password")) {
					return ConditionOutcome.match("Keystore found in Environment");
				}
				return ConditionOutcome.noMatch("Keystore found but no password in Environment");
			}
			else if (hasProperty(environment, "encrypt.key")) {
				return ConditionOutcome.match("Key found in Environment");
			}
			return ConditionOutcome.noMatch("Keystore nor key found in Environment");
		}

		private boolean hasProperty(Environment environment, String key) {
			String value = environment.getProperty(key);
			if (value == null) {
				return false;
			}
			return StringUtils.hasText(environment.resolvePlaceholders(value));
		}

	}

}
```

spring cloud 项目如果需要配置某些敏感字段，可以考虑使用一下，不需要依赖 spring cloud config
 
```sh
encrypt.key-store.location=classpath:server.jks
encrypt.key-store.password=${JKS_PASSWORD}
encrypt.key-store.alias=mytestkey
encrypt.rsa.salt=bloodybeaf
encrypt.key-store.type=jks
```

`my.secret.sex={cipher}AQASVNNzJ/9t1+t+1Laj5eAhWHV6QbLyq1EYPQ8lNHJ++5SGZ5WIv8RQkT4ztTqZ8Rx/dQVKSaBWK3GgVyVsZvlN9pKQZomJCw/EHX2njSzTYQuPimNVGQejR4zs3EkEK011OOf38OPNJFyBSIkwFxC+yOrB9Qa9Ib2qiWbF796io0FiXWQTchxfc1SxZ5jOBKDSB8T987x17B/Ds54Rp6tf5MyaAOpPZKdbJrMzXgMYy8znDXXlWYD2ZGDZYTTd7D3eYyhRYcljUe+gRwu6tRTvvfL/UjdEabYb5gcK7qoIV7ciQ1sGzFkr0VslpWViBKD4DGkKEMVf36G1KA8WqsshqN+29GCRtYekPUl1dvfBH6qZtrU+az4QPlj8KHiApRg=
`