```java
package org.springframework.cloud.bootstrap;

import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;
import org.springframework.boot.BootstrapContext;
import org.springframework.boot.BootstrapRegistry;
import org.springframework.boot.BootstrapRegistryInitializer;
import org.springframework.boot.context.properties.bind.Binder;
import org.springframework.cloud.bootstrap.encrypt.KeyProperties;
import org.springframework.cloud.bootstrap.encrypt.RsaProperties;
import org.springframework.cloud.bootstrap.encrypt.TextEncryptorUtils;
import org.springframework.util.ClassUtils;

/**
 * Bootstrapper.
 *
 * @author Marcin Grzejszczak
 * @since 3.0.0
 */
public class TextEncryptorConfigBootstrapper implements BootstrapRegistryInitializer {

	/**
	 * RsaSecretEncryptor present.
	 */
	public static final boolean RSA_IS_PRESENT = ClassUtils
			.isPresent("org.springframework.security.rsa.crypto.RsaSecretEncryptor", null);

	@Override
	public void initialize(BootstrapRegistry registry) {
		if (!ClassUtils.isPresent("org.springframework.security.crypto.encrypt.TextEncryptor", null)) {
			return;
		}
		/**
			@ConfigurationProperties(KeyProperties.PREFIX)
			public class KeyProperties {}
		*/
		java8 的 function interface，先在这里注册一个 function，等后面DefaultBootstrapContext用的时候把this传进来，
		这个方法保证能return一个instance
		
		这样的好处是什么？代码有点绕，难道是因为KeyProperties需要后面初始化？ KeyProperties 与 BootstrapContext 通过
		Binder 关联，那么这个binder在哪里注测到 BootstrapContext ？
		这个Binder是后面才注册到Context的，后面应该会看到
		registry.registerIfAbsent(KeyProperties.class, context -> context.get(Binder.class)
				.bind(KeyProperties.PREFIX, KeyProperties.class).orElseGet(KeyProperties::new));
		if (RSA_IS_PRESENT) {
			/**
				@ConditionalOnClass(RsaAlgorithm.class)
				@ConfigurationProperties(RsaProperties.PREFIX)
				public class RsaProperties {}
			**/
			registry.registerIfAbsent(RsaProperties.class, context -> context.get(Binder.class)
					.bind(RsaProperties.PREFIX, RsaProperties.class).orElseGet(RsaProperties::new));
		}
		向 register 中注入 TextEncryptor.class 的 provider，
		配置的 property prefix 为 ‘{cipher}’ 就可以自动解密
		TextEncryptorUtils.register(registry);
		
		// promote beans to context
		registry.addCloseListener(event -> {
			if (TextEncryptorUtils.isLegacyBootstrap(event.getApplicationContext().getEnvironment())) {
				return;
			}
			BootstrapContext bootstrapContext = event.getBootstrapContext();
			KeyProperties keyProperties = bootstrapContext.get(KeyProperties.class);
			ConfigurableListableBeanFactory beanFactory = event.getApplicationContext().getBeanFactory();
			if (keyProperties != null) {
				beanFactory.registerSingleton("keyProperties", keyProperties);
			}
			if (RSA_IS_PRESENT) {
				RsaProperties rsaProperties = bootstrapContext.get(RsaProperties.class);
				if (rsaProperties != null) {
					beanFactory.registerSingleton("rsaProperties", rsaProperties);
				}
			}
			TextEncryptorUtils.promote(bootstrapContext, beanFactory);
		});
	}

	@Deprecated
	public static boolean keysConfigured(KeyProperties properties) {
		return TextEncryptorUtils.keysConfigured(properties);
	}

	@Deprecated
	public static class FailsafeTextEncryptor extends TextEncryptorUtils.FailsafeTextEncryptor {

	}

}
```