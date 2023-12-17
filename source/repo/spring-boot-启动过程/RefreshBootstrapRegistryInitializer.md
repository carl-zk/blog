

```java

package org.springframework.cloud.bootstrap;

import org.springframework.boot.BootstrapContext;
import org.springframework.boot.BootstrapRegistry;
import org.springframework.boot.BootstrapRegistryInitializer;
import org.springframework.cloud.context.refresh.ConfigDataContextRefresher;

/**
 * BootstrapRegistryInitializer that adds the BootstrapContext to the ApplicationContext
 * for use later in {@link ConfigDataContextRefresher}.
 *
 * @author Spencer Gibb
 * @since 3.0.3
 */
public class RefreshBootstrapRegistryInitializer implements BootstrapRegistryInitializer {

	@Override
	public void initialize(BootstrapRegistry registry) {
		// promote BootstrapContext to context
		加一个监听 ApplicationListener 
		当 BootstrapContextClosedEvent 时，将 bootstrapContext bean 注册到 applicationContext 中
		即 bootstrapContext 结束，applicationContext Prepare 开始的时候
		registry.addCloseListener(event -> {
			BootstrapContext bootstrapContext = event.getBootstrapContext();
			event.getApplicationContext().getBeanFactory().registerSingleton("bootstrapContext", bootstrapContext);
		});
	}

}

```


