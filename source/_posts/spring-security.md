---
title: spring-security
date: 2019-02-18 20:15:22
category:
tags: spring
---
好久不更新blog了，慵懒了！
> 为了搞清楚 Spring Security 是如何工作了，特地翻了下源代码，查了许多文档，因为我比较在意细节，例如从何时起SS做认证(Authentication)，从何时做授权(Authorization)，如何定制SS。

### Spring Security Filters
Spring Security 框架主要利用 Filter 来实现对 HTTP 请求的认证和授权，掌握了 Filter 就弄明白了SS。

Spring Security 的所有 Filter 都放在 FilterChainProxy 的 `List<SecurityFilterChain>` 中，Spring-boot 启动时通过 SecurityFilterAutoConfiguration 自动注册 Spring Security's Filter;

![](/2019/02/18/spring-security/flow.svg)

FilterChainProxy
```java
    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
            FilterChain chain) throws IOException, ServletException {
        boolean clearContext = request.getAttribute(FILTER_APPLIED) == null;
        if (clearContext) {
            try {
                request.setAttribute(FILTER_APPLIED, Boolean.TRUE);
                doFilterInternal(request, response, chain);
            }
            finally {
                SecurityContextHolder.clearContext();
                request.removeAttribute(FILTER_APPLIED);
            }
        }
        else {
            doFilterInternal(request, response, chain);
        }
    }
```
可以看出 doFilterInternal(request, response, chain) 就包含了 Spring Security 的认证和授权，认证结果保存着 SecurityContextHolder中，FilterChain 结束后清除。

#### Authentication
AbstractAuthenticationProcessingFilter
```java
public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {

        ...

        Authentication authResult;

        try {
            authResult = attemptAuthentication(request, response);
            if (authResult == null) {
                return;
            }
            // 认证成功，依据session策略进行处理，默认无session
            sessionStrategy.onAuthentication(authResult, request, response);
        }
        catch (AuthenticationException failed) {
            unsuccessfulAuthentication(request, response, failed);
            return;
        }

        // successfulAuthentication(request, response, chain, authResult);

        SecurityContextHolder.getContext().setAuthentication(authResult);

        // 记住认证结果，一般在 cookie 或 redis 
        rememberMeServices.loginSuccess(request, response, authResult);

        // Fire event
        if (this.eventPublisher != null) {
            eventPublisher.publishEvent(new InteractiveAuthenticationSuccessEvent(
                    authResult, this.getClass()));
        }

        // 认证成功后，默认跳转到指定 target url
        successHandler.onAuthenticationSuccess(request, response, authResult);
    }
```

attemptAuthentication(request, response) 需要子类具体实现认证过程，调用 this.getAuthenticationManager().authenticate(Authentication auth) 方法。
AuthenticationManager包含 `List<AuthenticationProvider>`, AuthenticationProvider 提供具体的认证过程。
概括一下就是 Filter 调用 AuthenticationManager 进行认证，认证成功后保存 Authentication 到 SecurityContextHolder。

#### Authorization
FilterSecurityInterceptor 是最后一个 SS Filter，一般情况下用户不需要DIY这部分，因为认证成功后会将 Principle (登录对象) 和 Roles 一同保存在 SecurityContextHolder 中，授权过程就成了根据 request 从 Map<RequestMatcher, Collection<ConfigAttribute>> 获取该 uri 所需角色列表，交给 AccessDecisionManager（类似的，它包含 `List<AccessDecisionVoter>`, 由 voter 投票） 来决定是否有权限访问，只要有一个 voter 不通过，则无权访问。

[code](https://github.com/carl-zk/JavaJava/tree/master/security2)

