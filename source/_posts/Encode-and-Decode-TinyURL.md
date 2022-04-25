---
title: Encode and Decode TinyURL
date: 2022-04-25 20:36:39
category: leetcode
tags:
    - python
---
> 记录一些Python3库的用法

- alpha = string.ascii_letters + '0123456789' # 静态属性
- random.choice() # Choose a random element from a non-empty sequence

长url转短url，看大佬如何思考：[StefanPochmann Two solutions and thoughts](https://leetcode.com/problems/encode-and-decode-tinyurl/discuss/100268/Two-solutions-and-thoughts)
若短连接用自增数字来设计会带来一些隐患：
1. 安全，别人容易按数字遍历获取所有url
2. 对某些数字敏感的人可能不会接受
3. 同样长度的编码，纯数字的编码数量少于字母+数字组合的

### leetcode 原题：

[535. Encode and Decode TinyURL](https://leetcode.com/problems/encode-and-decode-tinyurl/)

Note: This is a companion problem to the System Design problem: Design TinyURL.
TinyURL is a URL shortening service where you enter a URL such as https://leetcode.com/problems/design-tinyurl and it returns a short URL such as http://tinyurl.com/4e9iAk. Design a class to encode a URL and decode a tiny URL.

There is no restriction on how your encode/decode algorithm should work. You just need to ensure that a URL can be encoded to a tiny URL and the tiny URL can be decoded to the original URL.

Implement the Solution class:

- Solution() Initializes the object of the system.
- String encode(String longUrl) Returns a tiny URL for the given longUrl.
- String decode(String shortUrl) Returns the original long URL for the given shortUrl. It is guaranteed that the given shortUrl was encoded by the same object.
 

Example 1:

Input: url = "https://leetcode.com/problems/design-tinyurl"
Output: "https://leetcode.com/problems/design-tinyurl"

Explanation:
Solution obj = new Solution();
string tiny = obj.encode(url); // returns the encoded tiny url.
string ans = obj.decode(tiny); // returns the original url after deconding it.


Constraints:

- 1 <= url.length <= 104
- url is guranteed to be a valid URL.

```python
import random
import string


class Codec:
    alpha = string.ascii_letters + '0123456789'

    def __init__(self):
        self.url2code = {}
        self.code2url = {}

    def encode(self, longUrl: str) -> str:
        """Encodes a URL to a shortened URL.
        """
        code = self.url2code.get(longUrl)
        while not code:
            code = ''.join(random.choice(Codec.alpha) for _ in range(6))
            if code in self.code2url:
                code = None
            else:
                self.url2code[longUrl] = code
                self.code2url[code] = longUrl
                return code
        return code

    def decode(self, shortUrl: str) -> str:
        """Decodes a shortened URL to its original URL.
        """
        return self.code2url[shortUrl]
```
