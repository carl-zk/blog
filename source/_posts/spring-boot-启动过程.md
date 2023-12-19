---
title: spring boot 启动过程
date: 2023-12-15 20:57:00
category:
tags:
---
> 阅读源码是最快的学习途径


```java
	public static ConfigurableApplicationContext run(Class<?>[] primarySources, String[] args) {
		return new SpringApplication(primarySources).run(args);
	}
```

```java
	public SpringApplication(ResourceLoader resourceLoader, Class<?>... primarySources) {
		this.resourceLoader = resourceLoader; // null
		Assert.notNull(primarySources, "PrimarySources must not be null");
		this.primarySources = new LinkedHashSet<>(Arrays.asList(primarySources)); // 带有@SpringBoot的主类
		this.webApplicationType = WebApplicationType.deduceFromClasspath();  //SERVLET
		/**
		通过 SpringFactoriesLoader 从默认资源路径 META-INF/spring.factories 加载
			com.learn.config.MyBootstrapRegistryInitializer
			org.springframework.cloud.bootstrap.RefreshBootstrapRegistryInitializer
			org.springframework.cloud.bootstrap.TextEncryptorConfigBootstrapper
		*/
		this.bootstrapRegistryInitializers = new ArrayList<>(
				getSpringFactoriesInstances(BootstrapRegistryInitializer.class));
		/**
			org.springframework.boot.context.config.DelegatingApplicationContextInitializer@550ee7e5
			org.springframework.boot.autoconfigure.SharedMetadataReaderFactoryContextInitializer@5f9b2141
			org.springframework.boot.context.ContextIdApplicationContextInitializer@247d8ae
			com.learn.config.MyApplicationContextInitializer@48974e45
			org.springframework.boot.context.ConfigurationWarningsApplicationContextInitializer@6a84a97d
			org.springframework.boot.rsocket.context.RSocketPortInfoApplicationContextInitializer@6c130c45
			org.springframework.boot.web.context.ServerPortInfoApplicationContextInitializer@50ad3bc1
			org.springframework.boot.autoconfigure.logging.ConditionEvaluationReportLoggingListener@223aa2f7
		*/
		setInitializers((Collection) getSpringFactoriesInstances(ApplicationContextInitializer.class));
		/**
	        org.springframework.cloud.bootstrap.BootstrapApplicationListener@7c711375
			org.springframework.cloud.bootstrap.LoggingSystemShutdownListener@57cf54e1
			org.springframework.boot.env.EnvironmentPostProcessorApplicationListener@5b03b9fe
			org.springframework.boot.context.config.AnsiOutputApplicationListener@37d4349f
			org.springframework.boot.context.logging.LoggingApplicationListener@434a63ab
			org.springframework.boot.autoconfigure.BackgroundPreinitializer@6e0f5f7f
			org.springframework.boot.context.config.DelegatingApplicationListener@2805d709
			org.springframework.cloud.context.restart.RestartListener@3ee37e5a
			org.springframework.boot.builder.ParentContextCloserApplicationListener@2ea41516
			com.learn.config.MyApplicationListener@3a44431a
			org.springframework.boot.ClearCachesApplicationListener@3c7f66c4
			org.springframework.boot.context.FileEncodingApplicationListener@194bcebf
		*/
		setListeners((Collection) getSpringFactoriesInstances(ApplicationListener.class));
		this.mainApplicationClass = deduceMainApplicationClass(); // 找 main 方法
	}
```
- **BootstrapRegistryInitializer**
	- [org.springframework.cloud.bootstrap.RefreshBootstrapRegistryInitializer](/blog/repo/spring-boot-启动过程/RefreshBootstrapRegistryInitializer)
    - [org.springframework.cloud.bootstrap.TextEncryptorConfigBootstrapper](/blog/repo/spring-boot-启动过程/TextEncryptorConfigBootstrapper)
- **ApplicationContextInitializer**
    - [org.springframework.boot.context.config.DelegatingApplicationContextInitializer@550ee7e5](/blog/repo/spring-boot-启动过程/DelegatingApplicationContextInitializer)
    - [org.springframework.boot.autoconfigure.SharedMetadataReaderFactoryContextInitializer@5f9b2141]()
    - [org.springframework.boot.context.ContextIdApplicationContextInitializer@247d8ae]()
    - [com.learn.config.MyApplicationContextInitializer@48974e45]()
    - [org.springframework.boot.context.ConfigurationWarningsApplicationContextInitializer@6a84a97d]()
    - [org.springframework.boot.rsocket.context.RSocketPortInfoApplicationContextInitializer@6c130c45]()
    - [org.springframework.boot.web.context.ServerPortInfoApplicationContextInitializer@50ad3bc1]()
    - [org.springframework.boot.autoconfigure.logging.ConditionEvaluationReportLoggingListener@223aa2f7]()
- **ApplicationListener**
	- [org.springframework.cloud.bootstrap.BootstrapApplicationListener@7c711375]()
			org.springframework.cloud.bootstrap.LoggingSystemShutdownListener@57cf54e1
			org.springframework.boot.env.EnvironmentPostProcessorApplicationListener@5b03b9fe
			org.springframework.boot.context.config.AnsiOutputApplicationListener@37d4349f
			org.springframework.boot.context.logging.LoggingApplicationListener@434a63ab
			org.springframework.boot.autoconfigure.BackgroundPreinitializer@6e0f5f7f
			org.springframework.boot.context.config.DelegatingApplicationListener@2805d709
			org.springframework.cloud.context.restart.RestartListener@3ee37e5a
			org.springframework.boot.builder.ParentContextCloserApplicationListener@2ea41516
			com.learn.config.MyApplicationListener@3a44431a
			org.springframework.boot.ClearCachesApplicationListener@3c7f66c4
			org.springframework.boot.context.FileEncodingApplicationListener@194bcebf
			public class BootstrapApplicationListener implements ApplicationListener<ApplicationEnvironmentPreparedEvent>, Ordered {}
		监听 EnvironmentPreparedEvent，从 bootstrap 加载配置，取名为 ***springCloudDefaultProperties***，高优先级
		```java
			@Override
			public void onApplicationEvent(ApplicationEnvironmentPreparedEvent event) {
				ConfigurableEnvironment environment = event.getEnvironment();
				// "spring.cloud.bootstrap.enabled=false" && isNotPresent(org.springframework.cloud.bootstrap.marker.Marker)
				// && "spring.config.use-legacy-processing=false"
				if (!bootstrapEnabled(environment) && !useLegacyProcessing(environment)) {
					return;
				}
				// don't listen to events in a bootstrap context 跳过 BootstrapContext，即只处理 ApplicationContext
				// properties.contains("bootstrap")
				if (environment.getPropertySources().contains(BOOTSTRAP_PROPERTY_SOURCE_NAME)) {
					return;
				}
				ConfigurableApplicationContext context = null;
				// 找出 bootstrap 配置
				String configName = environment.resolvePlaceholders("${spring.cloud.bootstrap.name:bootstrap}");
				for (ApplicationContextInitializer<?> initializer : event.getSpringApplication().getInitializers()) {
					if (initializer instanceof ParentContextApplicationContextInitializer) {
						context = findBootstrapContext((ParentContextApplicationContextInitializer) initializer, configName);
					}
				}
				if (context == null) {
					context = bootstrapServiceContext(environment, event.getSpringApplication(), configName);
					event.getSpringApplication().addListeners(new CloseContextOnFailureApplicationListener(context));
				}
		
				apply(context, event.getSpringApplication(), environment);
			}
		```
    - [org.springframework.cloud.bootstrap.LoggingSystemShutdownListener@57cf54e]()
    - [org.springframework.boot.env.EnvironmentPostProcessorApplicationListener@]()
    - [org.springframework.boot.context.config.AnsiOutputApplicationListener@37d]()
    - [org.springframework.boot.context.logging.LoggingApplicationListener@434a6]()
    - [org.springframework.boot.autoconfigure.BackgroundPreinitializer@6e0f5f7f]()
    - [org.springframework.boot.context.config.DelegatingApplicationListener@280]()
    - [org.springframework.cloud.context.restart.RestartListener@3ee37e5a]()
    - [org.springframework.boot.builder.ParentContextCloserApplicationListener@2]()
    - [com.learn.config.MyApplicationListener@3a44431a]()
    - [org.springframework.boot.ClearCachesApplicationListener@3c7f66c4]()
    - [org.springframework.boot.context.FileEncodingApplicationListener@194bcebf]()
