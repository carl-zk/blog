---
title: understanding-oauth2
date: 2019-03-18 20:53:12
category:
tags: oauth2
---
> 头一次尝试翻译一篇文章，不准确处请指正，谢谢！
> [https://github.com/carl-zk/JavaJava/tree/master/oauth2](https://github.com/carl-zk/JavaJava/tree/master/oauth2)

Source: [http://www.bubblecode.net/en/2016/01/22/understanding-oauth2/](http://www.bubblecode.net/en/2016/01/22/understanding-oauth2/)
如果OAuth2对你来说仍是一个模糊的概念或者你只想验证一下自己理解的是否准确，那么这篇文章就是为你准备的。

## 什么是 OAuth2?
[OAuth2](https://oauth.net/2/) 就是，你可以先猜一下，the OAuth Protocol (also called framework) 的第2版。
此协议允许第三方应用程序代表资源所有者授予对HTTP服务的有限访问权限，或允许第三方应用程序代表自己获取访问权限。访问权限由客户端（client）发起，它可以是一个网站或手机应用等。
第2版协议致力于简化上一版本并促进不同应用间的交互。
规范([Specifications](https://tools.ietf.org/html/rfc6749)) 仍处于起草期并且在不断被完善，但这并不能阻止它被实现并受到互联网大佬的青睐，像 Google、Facebook。
> 译者注：很好奇 spring-security-oauth2 是对 RFC 哪个版本的实现，大概是 6749和6750 版，最新的更新是 8252 版（for Native Apps），不知道区别在哪里。

## 基础知识
### Roles（角色）
OAuth2 定义了4种角色：
- 资源所属者（Resource Owner）：一般指你自己。
- 资源服务器（Resource Server）：托管（你的）私有数据的服务器（比如托管你个人资料和信息的Google）。
- 客户端（Client）：向资源服务器发起请求的应用（PHP 网站、Javascript 应用或手机应用）。
- 认证服务器（Authorization Server）：向客户端下发token的服务器。这个token可以让客户端访问资源服务器。This server can be the same as the authorization server (same physical server and same application), and it is often the case.（不知道这句怎么翻译）

### Tokens
Tokens 是认证服务器随机生成的字符串，当客户端来请求时下发的。
Token 分为两种：
- Access Token：这个非常重要，因为它可以让第三方应用访问资源服务器上的用户数据。它放在客户端请求的Header或参数中。它不是永久的，认证服务器会规定它的过期时间。通常要尽可能保证它不被泄露，但这又很难做到，尤其是客户端是web浏览器而且是用JavaScript去请求。
- Refresh Token：这个token会跟Access Token一起下发，但不同于后者，不是客户端每次发起请求到资源服务器都会携带。它只是用来当Access Token过期时客户端向认证服务器获取新的Access Token。出于安全考虑，可能并不会获取到Refresh Token，我们后面会讲到时在什么场景下拿不到它。

### Access Token scope（AT 作用范围）
作用范围是指Access token有哪些访问权限。认证服务器会定义一个作用范围列表。客户端必须指定它所请求的范围。所申请的范围越小，被授权的几率就越大。
> 更多：[http://tools.ietf.org/html/rfc6749#section-3.3](http://tools.ietf.org/html/rfc6749#section-3.3)

### HTTPS
OAuth2 要求客户端和认证服务器之间使用HTTPS协议，因为会有敏感信息（tokens或证书等）。事实上并没有强制你这样做，但你要知道不这样会有很大的安全漏洞。

## 注册成为客户端
既然你想通过OAuth2从资源服务器访问数据，你首先要向认证服务器注册成为一个客户端。
每个提供者都可以自由实现这一点。OAuth2只是定义了客户端必须的参数和认证服务器返回的参数。
下面是规定的参数：
**客户端注册**
- 应用名字：即客户端应用名。
- 跳转URLs：收到authorization code和access token后客户端的跳转地址。
- 授权类型（Grant Type(s)）：客户端申请的授权类型。
- Javascript Origin (可选)：通过XMLHttpRequest访问资源服务器时指定的hostname。

**认证服务器返回**
- 客户端ID（Client Id）：唯一的随机字符串。
- 客户端秘钥 (Client Secret)：必须保密的秘钥。
> 更多：[RFC 6749 — Client Registration](https://tools.ietf.org/html/rfc6749#section-2)

## 授权类型
根据客户端的位置和性质，OAuth2定义了4种类型。
### 授权码模式（Authorization Code Grant）
1. 何时应使用？
当客户端是web服务器时应该使用。它允许你获取一个长期有效的token，因为你可以用refresh token去刷新它（如果认证服务器允许的话）。
2. 例如：
- 资源拥有者：你。
- 资源服务器：a Google Server.
- 客户端：任何web服务器。
- 认证服务器：a Google Server.
3. 场景：
    1. 一个web应用想要获取你的Google信息。
    2. 你在此web应用上被跳转到Google的授权页面。
    3. 如果你点允许，Google会发一个authorization code给web的回调接口。
    4. 然后，web应用用这个code从认证服务器（Google）获取一个access token。
    5. web应用这时可以通过access token访问资源服务器（Google）上的你的资料。  

你并不能见到access token，它会被保存在web（例如session）中。Google还会发送其他信息，比如token过期时间甚至一个refresh token.  
这是个理想的场景，并且相对安全点，因为access token没有在client端（web浏览器）传递。
> 更多[Authorization Code Grant](https://tools.ietf.org/html/rfc6749#section-4.1)

时序图：
![](/2019/03/18/understanding-oauth2/auth_code_flow.png)

### 简化模式（Implicit Grant）
1. 何时使用？
一般用在当客户端是用像JavaScript脚本语言写的浏览器端应用。这个类型不允许下发refresh token。
2. 例如：
- 资源拥有者：你。
- 资源服务器：a Facebook Server.
- 客户端：AngularJS web应用。
- 认证服务器：a Facebook Server.
3. 场景：
    1. 客户端（AngularJS）想获取你在Facebook的资料。
    2. 你被重定向到认证服务器（Facebook）。
    3. 如果你同意授权，就会携带者access token重定向回客户端，access token直接放在了URI上（并不是发送给web server）。例如： http://example.com/oauthcallback#access_token=MzJmNDc3M2VjMmQzN.
    4. 这个token可以被客户端（AngularJS）拿到，去访问资源服务器（Facebook）。例如： https://graph.facebook.com/me?access_token=MzJmNDc3M2VjMmQzN.

也许你会疑问为什么客户端可以用JavaScript直接请求Facebook API而不被block，[Same Origin Policy](http://en.wikipedia.org/wiki/Same_origin_policy) 吗?这要归功于Facebook授权了此类跨域访问请求，因为它的响应头中有`Access-Control-Allow-Origin`。
> 更多跨域资源分享[Cross-Origin Resource Sharing(CORS)](https://developer.mozilla.org/en-US/docs/HTTP/Access_control_CORS#The_HTTP_response_headers)

> **警告**：这个类型只用在别无选择时，因为它完全暴露在客户端，是最不安全的一种。

> 更多：[Implicit Grant](https://tools.ietf.org/html/rfc6749#section-4.2)

时序图：
![](/2019/03/18/understanding-oauth2/implicit_flow.png)

### 密码模式（Resource Owner Password Credentials Grant）
1. 何时使用？
使用这种方式，证书（即密码）会经过客户端发送给认证服务器。这势必在客户端和认证服务器都可靠的情况下进行的（因为你要先把密码输入到client，然后client去请求啊）。通过用于客户端和认证服务器都是同一个开发团队的情况。例如，我们试想一个web网站*example.com*想去访问它的子域名*api.example.com*下的资源。用户当然会毫不犹豫的在*example.com*网站上输入自己的用户名/密码，因为这个账号就是在这个网站创建的嘛。
2. 例如：
- 资源拥有者：你有一个Acme公司网站*acme.com*上的一个账号。
- 资源服务器：Acme公司对外提供的API *api.acme.com*。
- 客户端：Acme公司的网站 *acme.com*。
- 认证服务器：an Acme Server.
3. 场景：
    1. Acme公司认为业务运营的不错，想暴露个RESTfull API给第三方应用。
    2. 公司想使用现有的API以免重复造轮子。
    3. 需要一个access token才能访问API.
    4. 为此，公司会先要求你输入账号密码，通过HTML表单，像往常一样。
    5. *acme.com*的服务器后台会用你的账号去认证服务器换取个access token。
    6. 这样*acme.com*就可以拿着access token 去访问资源服务器*api.acme.com*了。

> 更多：[Resource Owner Password Credentials Grant]( Resource Owner Password Credentials Grant)

时序图：
![](/2019/03/18/understanding-oauth2/password.png)

### 客户端模式（Client Credentials Grant）
1. 何时使用？
通常客户端即是资源拥有者。它无需做任何认证申请。
2. 例如：
- 资源拥有者：任何web网站。
- 资源服务器：Google Cloud Storage.
- 客户端：资源拥有者。
- 认证服务器：a Google Server.
3. 场景：
    1. 网站存储着任何Google Cloud Storage类型的文件。
    2. 网站必须通过Google API获取或修改它们，并且必须先经过认证服务器认证。
    3. 一旦认证完，web网站就可以获取资源服务器的资源。

即，客户端要访问资源服务器时不必认证自己是否有权限。
> 更多：[Client Credentials Grant](https://tools.ietf.org/html/rfc6749#section-4.4)

时序图：
![](/2019/03/18/understanding-oauth2/client_credentials_flow.png)

## Access token 的使用
access token有几种使用方法。
### 请求参数（GET or POST）
例如GET请求：https://api.example.com/profile?access_token=MzJmNDc3M2VjMmQzN
这并不推荐，因为它可以在服务器的access log中被看到。

### Authorization header
GET /profile HTTP/1.1
Host: api.example.com
Authorization: Bearer MzJmNDc3M2VjMmQzN

这看上去很优雅，但是所有资源服务器都禁止这样。

## 安全
OAuth2有时被指责存在侵入性，但这都是对协议的不良实现造成的。有些误区需要规避，下面是一些例子。

### Authorization Code Grant 的漏洞
在一些特定场景下攻击者会窃取到用户的账号。这个漏洞经常遇到并且发生在很多知名网站上（Pinterest, SoundCloud, Digg, ...），是由于它们并没有正确的实现这个协议流程导致的。

例如：
- 受害者在A网站上有一个账号。
- A网站允许使用Facebook登录或注册，并且A网站之前已在Facebook OAuth2 认证服务器端注册为一个客户端。
- 你点击Facebook按钮，但是不去跳转，这多亏了Firefox的NoRedirect或使用Burp完成。（callback 看起来是这样的：http://site-internet-a.com/facebook/login?code=OGI2NmY2NjYxN2Y4YzE3）
- 你拿到这个即将跳转的url(包含一个authorization code)。
- 现在你必须强迫受害者通过网站的隐藏iframe或邮箱中的图片来访问这个url。
- 如果受害者已经登录了网站A，恭喜你！你可以用Facebook账号来访问受害者在网站A的资料了。你只需点击Facebook的按钮然后就关联上了受害者账号。

解决方法：
有一种解决途径，增加个“state"参数。这只是推荐而非强制在规范中的。当客户端请求authorization code时带有state时，认证服务器会原样在response中返回，客户端会在换取access token之前对state进行校验。这个参数一般是一串唯一的随机数存在用户session中。例如PHP: `sha1(uniqid(mt_rand(), true))`.
在上面的例子中，如果有"state"参数，ta就会发现回调返回的hash跟session保存的不一致，因此就会阻止受害者的账号被窃取。
> 更多：[Cross-Site Request Forgery](https://tools.ietf.org/html/rfc6749#section-10.12)

### Implicit Grant 的漏洞
这种类型的认证是最不安全的，因为它暴露了access token给客户端（多数情况下指JavaScript）。被众所周知的一个漏洞是源自客户端不能分辨这个access token是否是为ta生成的（[Confused Deputy Problem](http://en.wikipedia.org/wiki/Confused_deputy_problem)）。这就方便了攻击者去窃取。

例如：
- 攻击者想要窃取受害者在网站A的账号。这个网站允许你用Facebook账号以Implicit方式认证。
- 攻击者创造了网站B，也允许Facebook账号登录。
- 受害者使用Facebook登录网站B，因此Implicit就给它生成了一个access token。
- 攻击者拿到了这个网站B上的access token，修改了URI片段用在了网站A。如果网站A没有防止这种攻击，那么受害者的账号就沦陷了。

解决方法：
为了避免这种漏洞，认证服务器必须提供一个获取该access token信息的API。这样，网站A就可以比较access token跟攻击者自己的的client_id。由于这个窃取的access token来自网站B，因此与网站A的client_id不同，因此访问网站A时会受到拒绝。

Google在它的API文档中这样描述的：
[https://developers.google.com/accounts/docs/OAuth2Login#validatingtoken](https://developers.google.com/accounts/docs/OAuth2Login#validatingtoken).

> 更多：[http://tools.ietf.org/html/rfc6819#section-4.4.2.6](http://tools.ietf.org/html/rfc6819#section-4.4.2.6)

### 点击劫持（Clickjacking）
攻击者会将授权页面放在iframe中，隐藏在一个链接下面诱导受害者点击，点击的地方正好是授权页的“允许”按钮。

例如：
![](/2019/03/18/understanding-oauth2/oauth2_clickjacking.png)

解决方法：
认证服务器在授权页面的返回头中增加key为`X-Frame-Options` value为`DENY`or`SAMEORIGIN`。这就防止了授权页面被放在iframe（DENY）或要求主页面的域名要和iframe的`src`值保持一致（SAMEORIGIN）.

这个header不是标准的，但是在下面的浏览器中都支持：IE8+, Firefox3.6.9+, Opera10.5+, Safari4+, Chrome 4.1.249.1042+.

> 更多：[https://developer.mozilla.org/en-US/docs/HTTP/X-Frame-Options](https://developer.mozilla.org/en-US/docs/HTTP/X-Frame-Options).

> 这是RFC中列举的漏洞和对应的方法：[http://tools.ietf.org/html/rfc6819](http://tools.ietf.org/html/rfc6819).

## 结论
无论怎样，OAuth2几年来似乎加强了自身作为对不同应用间授权的标准。
我希望自己帮助了你了解了它的工作原理。接下来我们会看到如何用Symfony2来创建自己的OAuth2认证服务器。
++原谅我蹩脚的英语。（译者注：作者原话）

> 译者注：这篇文章对授权码模式的描述不太具体，阮一峰的写的很好。

## 参考
[OAuth 2.0 Security Best Current Practice](https://tools.ietf.org/id/draft-ietf-oauth-security-topics-06.html)
[springboot2-with-oauth2-integration](https://pattern-match.com/blog/2018/10/17/springboot2-with-oauth2-integration/)
[Spring Boot and OAuth2](https://spring.io/guides/tutorials/spring-boot-oauth2/)
[阮一峰 理解OAuth 2.0](https://www.ruanyifeng.com/blog/2014/05/oauth_2_0.html)
[Using Spring Security 5 to integrate with OAuth 2-secured services such as Facebook and GitHub](https://spring.io/blog/2018/03/06/using-spring-security-5-to-integrate-with-oauth-2-secured-services-such-as-facebook-and-github)

