
  <meta charset="utf-8">
  
## hello
### hi

> 阅读源码是最快的学习途径

```

	@Override
	public String[] selectImports(AnnotationMetadata annotationMetadata) {
		ClassLoader classLoader = Thread.currentThread().getContextClassLoader();
		// Use names and ensure unique to protect against duplicates
		List<String> names = new ArrayList<>(
				SpringFactoriesLoader.loadFactoryNames(BootstrapConfiguration.class, classLoader));
		names.addAll(Arrays.asList(StringUtils
				.commaDelimitedListToStringArray(this.environment.getProperty("spring.cloud.bootstrap.sources", ""))));

		List<OrderedAnnotatedElement> elements = new ArrayList<>();
		for (String name : names) {
			try {
				elements.add(new OrderedAnnotatedElement(this.metadataReaderFactory, name));
			}
			catch (IOException e) {
				continue;
			}
		}
		AnnotationAwareOrderComparator.sort(elements);

		String[] classNames = elements.stream().map(e -> e.name).toArray(String[]::new);

		return classNames;
	}
```