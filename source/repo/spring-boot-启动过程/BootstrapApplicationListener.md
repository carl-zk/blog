```java

package org.springframework.cloud.bootstrap;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.springframework.beans.factory.ListableBeanFactory;
import org.springframework.boot.Banner.Mode;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.WebApplicationType;
import org.springframework.boot.builder.ParentContextApplicationContextInitializer;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.context.event.ApplicationEnvironmentPreparedEvent;
import org.springframework.boot.context.event.ApplicationFailedEvent;
import org.springframework.boot.context.logging.LoggingApplicationListener;
import org.springframework.boot.env.OriginTrackedMapPropertySource;
import org.springframework.boot.origin.Origin;
import org.springframework.boot.origin.OriginLookup;
import org.springframework.cloud.bootstrap.encrypt.EnvironmentDecryptApplicationInitializer;
import org.springframework.cloud.bootstrap.support.OriginTrackedCompositePropertySource;
import org.springframework.context.ApplicationContextInitializer;
import org.springframework.context.ApplicationEvent;
import org.springframework.context.ApplicationListener;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.context.event.SmartApplicationListener;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.AnnotationAwareOrderComparator;
import org.springframework.core.annotation.Order;
import org.springframework.core.env.AbstractEnvironment;
import org.springframework.core.env.CompositePropertySource;
import org.springframework.core.env.ConfigurableEnvironment;
import org.springframework.core.env.MapPropertySource;
import org.springframework.core.env.MutablePropertySources;
import org.springframework.core.env.PropertySource;
import org.springframework.core.env.PropertySource.StubPropertySource;
import org.springframework.core.env.SystemEnvironmentPropertySource;
import org.springframework.util.ReflectionUtils;
import org.springframework.util.StringUtils;

import static org.springframework.cloud.util.PropertyUtils.bootstrapEnabled;
import static org.springframework.cloud.util.PropertyUtils.useLegacyProcessing;

/**
 * A listener that prepares a SpringApplication (e.g. populating its Environment) by
 * delegating to {@link ApplicationContextInitializer} beans in a separate bootstrap
 * context. The bootstrap context is a SpringApplication created from sources defined in
 * spring.factories as {@link BootstrapConfiguration}, and initialized with external
 * config taken from "bootstrap.properties" (or yml), instead of the normal
 * "application.properties".

用来Prepare SpringApplication的，（比如：产出 Environment）
 
bootstrap context 由 bootstrap.properties 配置初始化，非 application.properties 

用 @BootstrapConfiguration 可以过滤 spring.factories 中的一些 class 不加载
  
 * @author Dave Syer
 *
 */
public class BootstrapApplicationListener implements ApplicationListener<ApplicationEnvironmentPreparedEvent>, Ordered {
    监听 ApplicationEnvironmentPreparedEvent

	/**
	 * Property source name for bootstrap.
	 */
	public static final String BOOTSTRAP_PROPERTY_SOURCE_NAME = "bootstrap";

	/**
	 * The default order for this listener.
	 */
	public static final int DEFAULT_ORDER = Ordered.HIGHEST_PRECEDENCE + 5;

	/**
	 * The name of the default properties.
	 */
	public static final String DEFAULT_PROPERTIES = "springCloudDefaultProperties";

	private int order = DEFAULT_ORDER;

	@Override
	public void onApplicationEvent(ApplicationEnvironmentPreparedEvent event) {
		ConfigurableEnvironment environment = event.getEnvironment();
		if (!bootstrapEnabled(environment) && !useLegacyProcessing(environment)) {
		/**
			public static boolean bootstrapEnabled(Environment environment) {
				// BOOTSTRAP_ENABLED_PROPERTY = "spring.cloud.bootstrap.enabled"
				/**
					MARKER_CLASS_EXISTS 有意思
					它在 spring-cloud-starter-bootstrap-4.0.0.jar 中
					package org.springframework.cloud.bootstrap.marker;

					/**
					 * A marker class, so that, if present, spring cloud bootstrap is enable similar to how
					 * 'spring.cloud.bootstrap.enabled=true' works.
					 *  专门写了一个class，起到和配置一样的作用而已
					 *  与只有配置相比，哪怕spring.cloud.bootstrap.enabled=false,照样初始化
					 */
					public abstract class Marker {
					
						private Marker() {
						}
					
					}
				*/
				return environment.getProperty(BOOTSTRAP_ENABLED_PROPERTY, Boolean.class, false) || MARKER_CLASS_EXISTS;
			}
		*/
			return;
		}
		// don't listen to events in a bootstrap context
		if (environment.getPropertySources().contains(BOOTSTRAP_PROPERTY_SOURCE_NAME)) {
		/**
			BOOTSTRAP_PROPERTY_SOURCE_NAME = "bootstrap"
			这个类只处理 application context
			我终于明白为啥会有 bootstrap context 了，因为 application context 无法启动它自己，需要有个 parent context 来拉起它
		*/
			return;
		}
		ConfigurableApplicationContext context = null;
		String configName = environment.resolvePlaceholders("${spring.cloud.bootstrap.name:bootstrap}");
		for (ApplicationContextInitializer<?> initializer : event.getSpringApplication().getInitializers()) {
		/**
			event.getSpringApplication()
			没注意过，居然包含了 启动类
		*/
			if (initializer instanceof ParentContextApplicationContextInitializer) {
			// 找到 parent initializer
				context = findBootstrapContext((ParentContextApplicationContextInitializer) initializer, configName);
				// 通过reflection获取到 initializer.parent，即 parent context
			}
		}
		if (context == null) {
			context = bootstrapServiceContext(environment, event.getSpringApplication(), configName);
			/**
				完整的 bootstrap context 从0到1的创建过程
				"${spring.cloud.bootstrap.location:}"
				"${spring.cloud.bootstrap.additional-location:}"
				spring.cloud.bootstrap.sources
			*/
			event.getSpringApplication().addListeners(new CloseContextOnFailureApplicationListener(context));
		}

		apply(context, event.getSpringApplication(), environment);
		/**
			当application没有被拉起时，对应前面 context == null 的情况，则加载 bootstrap properties、initializers
		*/
	}

	private ConfigurableApplicationContext findBootstrapContext(ParentContextApplicationContextInitializer initializer,
			String configName) {
		Field field = ReflectionUtils.findField(ParentContextApplicationContextInitializer.class, "parent");
		ReflectionUtils.makeAccessible(field);
		ConfigurableApplicationContext parent = safeCast(ConfigurableApplicationContext.class,
				ReflectionUtils.getField(field, initializer));
		if (parent != null && !configName.equals(parent.getId())) {
			parent = safeCast(ConfigurableApplicationContext.class, parent.getParent());
		}
		return parent;
	}

	private <T> T safeCast(Class<T> type, Object object) {
		try {
			return type.cast(object);
		}
		catch (ClassCastException e) {
			return null;
		}
	}

	private ConfigurableApplicationContext bootstrapServiceContext(ConfigurableEnvironment environment,
			final SpringApplication application, String configName) {
		ConfigurableEnvironment bootstrapEnvironment = new AbstractEnvironment() {
		};
		MutablePropertySources bootstrapProperties = bootstrapEnvironment.getPropertySources();
		String configLocation = environment.resolvePlaceholders("${spring.cloud.bootstrap.location:}");
		String configAdditionalLocation = environment
				.resolvePlaceholders("${spring.cloud.bootstrap.additional-location:}");
		Map<String, Object> bootstrapMap = new HashMap<>();
		bootstrapMap.put("spring.config.name", configName);
		// if an app (or test) uses spring.main.web-application-type=reactive, bootstrap
		// will fail
		// force the environment to use none, because if though it is set below in the
		// builder
		// the environment overrides it
		bootstrapMap.put("spring.main.web-application-type", "none");
		if (StringUtils.hasText(configLocation)) {
			bootstrapMap.put("spring.config.location", configLocation);
		}
		if (StringUtils.hasText(configAdditionalLocation)) {
			bootstrapMap.put("spring.config.additional-location", configAdditionalLocation);
		}
		bootstrapProperties.addFirst(new MapPropertySource(BOOTSTRAP_PROPERTY_SOURCE_NAME, bootstrapMap));
		for (PropertySource<?> source : environment.getPropertySources()) {
			if (source instanceof StubPropertySource) {
				continue;
			}
			bootstrapProperties.addLast(source);
		}
		// TODO: is it possible or sensible to share a ResourceLoader?
		SpringApplicationBuilder builder = new SpringApplicationBuilder().profiles(environment.getActiveProfiles())
				.bannerMode(Mode.OFF).environment(bootstrapEnvironment)
				// Don't use the default properties in this builder
				.registerShutdownHook(false).logStartupInfo(false).web(WebApplicationType.NONE);
		final SpringApplication builderApplication = builder.application();
		if (builderApplication.getMainApplicationClass() == null) {
			// gh_425:
			// SpringApplication cannot deduce the MainApplicationClass here
			// if it is booted from SpringBootServletInitializer due to the
			// absense of the "main" method in stackTraces.
			// But luckily this method's second parameter "application" here
			// carries the real MainApplicationClass which has been explicitly
			// set by SpringBootServletInitializer itself already.
			builder.main(application.getMainApplicationClass());
		}
		if (environment.getPropertySources().contains("refreshArgs")) {
			// If we are doing a context refresh, really we only want to refresh the
			// Environment, and there are some toxic listeners (like the
			// LoggingApplicationListener) that affect global static state, so we need a
			// way to switch those off.
			builderApplication.setListeners(filterListeners(builderApplication.getListeners()));
		}
		builder.sources(BootstrapImportSelectorConfiguration.class);
		final ConfigurableApplicationContext context = builder.run();
		// gh-214 using spring.application.name=bootstrap to set the context id via
		// `ContextIdApplicationContextInitializer` prevents apps from getting the actual
		// spring.application.name
		// during the bootstrap phase.
		context.setId("bootstrap");
		// Make the bootstrap context a parent of the app context
		addAncestorInitializer(application, context);
		// It only has properties in it now that we don't want in the parent so remove
		// it (and it will be added back later)
		bootstrapProperties.remove(BOOTSTRAP_PROPERTY_SOURCE_NAME);
		mergeDefaultProperties(environment.getPropertySources(), bootstrapProperties);
		return context;
	}

	private Collection<? extends ApplicationListener<?>> filterListeners(Set<ApplicationListener<?>> listeners) {
		Set<ApplicationListener<?>> result = new LinkedHashSet<>();
		for (ApplicationListener<?> listener : listeners) {
			if (!(listener instanceof LoggingApplicationListener)
					&& !(listener instanceof LoggingSystemShutdownListener)) {
				result.add(listener);
			}
		}
		return result;
	}

	private void mergeDefaultProperties(MutablePropertySources environment, MutablePropertySources bootstrap) {
		String name = DEFAULT_PROPERTIES;
		if (bootstrap.contains(name)) {
			PropertySource<?> source = bootstrap.get(name);
			if (!environment.contains(name)) {
				environment.addLast(source);
			}
			else {
				PropertySource<?> target = environment.get(name);
				if (target instanceof MapPropertySource && target != source && source instanceof MapPropertySource) {
					Map<String, Object> targetMap = ((MapPropertySource) target).getSource();
					Map<String, Object> map = ((MapPropertySource) source).getSource();
					for (String key : map.keySet()) {
						if (!target.containsProperty(key)) {
							targetMap.put(key, map.get(key));
						}
					}
				}
			}
		}
		mergeAdditionalPropertySources(environment, bootstrap);
	}

	private void mergeAdditionalPropertySources(MutablePropertySources environment, MutablePropertySources bootstrap) {
		PropertySource<?> defaultProperties = environment.get(DEFAULT_PROPERTIES);
		ExtendedDefaultPropertySource result = defaultProperties instanceof ExtendedDefaultPropertySource
				? (ExtendedDefaultPropertySource) defaultProperties
				: new ExtendedDefaultPropertySource(DEFAULT_PROPERTIES, defaultProperties);
		for (PropertySource<?> source : bootstrap) {
			if (!environment.contains(source.getName())) {
				result.add(source);
			}
		}
		for (String name : result.getPropertySourceNames()) {
			bootstrap.remove(name);
		}
		addOrReplace(environment, result);
		addOrReplace(bootstrap, result);
	}

	private void addOrReplace(MutablePropertySources environment, PropertySource<?> result) {
		if (environment.contains(result.getName())) {
			environment.replace(result.getName(), result);
		}
		else {
			environment.addLast(result);
		}
	}

	private void addAncestorInitializer(SpringApplication application, ConfigurableApplicationContext context) {
		boolean installed = false;
		for (ApplicationContextInitializer<?> initializer : application.getInitializers()) {
			if (initializer instanceof AncestorInitializer) {
				installed = true;
				// New parent
				((AncestorInitializer) initializer).setParent(context);
			}
		}
		if (!installed) {
			application.addInitializers(new AncestorInitializer(context));
		}

	}

	@SuppressWarnings("unchecked")
	private void apply(ConfigurableApplicationContext context, SpringApplication application,
			ConfigurableEnvironment environment) {
		if (application.getAllSources().contains(BootstrapMarkerConfiguration.class)) {
			return;
		}
		application.addPrimarySources(List.of(BootstrapMarkerConfiguration.class));
		@SuppressWarnings("rawtypes")
		Set target = new LinkedHashSet<>(application.getInitializers());
		target.addAll(getOrderedBeansOfType(context, ApplicationContextInitializer.class));
		application.setInitializers(target);
		addBootstrapDecryptInitializer(application);
	}

	@SuppressWarnings("unchecked")
	private void addBootstrapDecryptInitializer(SpringApplication application) {
		DelegatingEnvironmentDecryptApplicationInitializer decrypter = null;
		Set<ApplicationContextInitializer<?>> initializers = new LinkedHashSet<>();
		for (ApplicationContextInitializer<?> ini : application.getInitializers()) {
			if (ini instanceof EnvironmentDecryptApplicationInitializer) {
				@SuppressWarnings("rawtypes")
				ApplicationContextInitializer del = ini;
				decrypter = new DelegatingEnvironmentDecryptApplicationInitializer(del);
				initializers.add(ini);
				initializers.add(decrypter);
			}
			else if (ini instanceof DelegatingEnvironmentDecryptApplicationInitializer) {
				// do nothing
			}
			else {
				initializers.add(ini);
			}
		}
		ArrayList<ApplicationContextInitializer<?>> target = new ArrayList<>(initializers);
		application.setInitializers(target);
	}

	private <T> List<T> getOrderedBeansOfType(ListableBeanFactory context, Class<T> type) {
		List<T> result = new ArrayList<>();
		for (String name : context.getBeanNamesForType(type)) {
			result.add(context.getBean(name, type));
		}
		AnnotationAwareOrderComparator.sort(result);
		return result;
	}

	@Override
	public int getOrder() {
		return this.order;
	}

	public void setOrder(int order) {
		this.order = order;
	}

	private static class BootstrapMarkerConfiguration {

	}

	private static class AncestorInitializer
			implements ApplicationContextInitializer<ConfigurableApplicationContext>, Ordered {

		private ConfigurableApplicationContext parent;

		AncestorInitializer(ConfigurableApplicationContext parent) {
			this.parent = parent;
		}

		public void setParent(ConfigurableApplicationContext parent) {
			this.parent = parent;
		}

		@Override
		public int getOrder() {
			// Need to run not too late (so not unordered), so that, for instance, the
			// ContextIdApplicationContextInitializer runs later and picks up the merged
			// Environment. Also needs to be quite early so that other initializers can
			// pick up the parent (especially the Environment).
			return Ordered.HIGHEST_PRECEDENCE + 5;
		}

		@Override
		public void initialize(ConfigurableApplicationContext context) {
			while (context.getParent() != null && context.getParent() != context) {
				context = (ConfigurableApplicationContext) context.getParent();
			}
			reorderSources(context.getEnvironment());
			new ParentContextApplicationContextInitializer(this.parent).initialize(context);
		}

		private void reorderSources(ConfigurableEnvironment environment) {
			PropertySource<?> removed = environment.getPropertySources().remove(DEFAULT_PROPERTIES);
			if (removed instanceof ExtendedDefaultPropertySource defaultProperties) {
				environment.getPropertySources()
						.addLast(new MapPropertySource(DEFAULT_PROPERTIES, defaultProperties.getSource()));
				for (PropertySource<?> source : defaultProperties.getPropertySources().getPropertySources()) {
					if (!environment.getPropertySources().contains(source.getName())) {
						environment.getPropertySources().addBefore(DEFAULT_PROPERTIES, source);
					}
				}
			}
		}

	}

	/**
	 * A special initializer designed to run before the property source bootstrap and
	 * decrypt any properties needed there (e.g. URL of config server).
	 */
	@Order(Ordered.HIGHEST_PRECEDENCE + 9)
	private static class DelegatingEnvironmentDecryptApplicationInitializer
			implements ApplicationContextInitializer<ConfigurableApplicationContext> {

		private ApplicationContextInitializer<ConfigurableApplicationContext> delegate;

		DelegatingEnvironmentDecryptApplicationInitializer(
				ApplicationContextInitializer<ConfigurableApplicationContext> delegate) {
			this.delegate = delegate;
		}

		@Override
		public void initialize(ConfigurableApplicationContext applicationContext) {
			this.delegate.initialize(applicationContext);
		}

	}

	private static class ExtendedDefaultPropertySource extends SystemEnvironmentPropertySource
			implements OriginLookup<String> {

		private final OriginTrackedCompositePropertySource sources;

		private final List<String> names = new ArrayList<>();

		ExtendedDefaultPropertySource(String name, PropertySource<?> propertySource) {
			super(name, findMap(propertySource));
			this.sources = new OriginTrackedCompositePropertySource(name);
		}

		@SuppressWarnings("unchecked")
		private static Map<String, Object> findMap(PropertySource<?> propertySource) {
			if (propertySource instanceof MapPropertySource) {
				return (Map<String, Object>) propertySource.getSource();
			}
			return new LinkedHashMap<>();
		}

		public CompositePropertySource getPropertySources() {
			return this.sources;
		}

		public List<String> getPropertySourceNames() {
			return this.names;
		}

		public void add(PropertySource<?> source) {
			// Only add map property sources added by boot, see gh-476
			if (source instanceof OriginTrackedMapPropertySource && !this.names.contains(source.getName())) {
				this.sources.addPropertySource(source);
				this.names.add(source.getName());
			}
		}

		@Override
		public Object getProperty(String name) {
			if (this.sources.containsProperty(name)) {
				return this.sources.getProperty(name);
			}
			return super.getProperty(name);
		}

		@Override
		public boolean containsProperty(String name) {
			if (this.sources.containsProperty(name)) {
				return true;
			}
			return super.containsProperty(name);
		}

		@Override
		public String[] getPropertyNames() {
			List<String> names = new ArrayList<>();
			names.addAll(Arrays.asList(this.sources.getPropertyNames()));
			names.addAll(Arrays.asList(super.getPropertyNames()));
			return names.toArray(new String[0]);
		}

		@Override
		public Origin getOrigin(String name) {
			return this.sources.getOrigin(name);
		}

	}

	private static class CloseContextOnFailureApplicationListener implements SmartApplicationListener {

		private final ConfigurableApplicationContext context;

		CloseContextOnFailureApplicationListener(ConfigurableApplicationContext context) {
			this.context = context;
		}

		@Override
		public boolean supportsEventType(Class<? extends ApplicationEvent> eventType) {
			return ApplicationFailedEvent.class.isAssignableFrom(eventType);
		}

		@Override
		public void onApplicationEvent(ApplicationEvent event) {
			if (event instanceof ApplicationFailedEvent) {
				this.context.close();
			}

		}

	}

}

```