---
title: BeanUtils的性能问题
date: 2018-05-26 15:57:21
category: java
tags: reflect
---
> 2019.8.10 
> BeanUtils替代工具：[mapstruct](https://github.com/mapstruct/mapstruct)

> 由于Joe指出因测试不充分，无法验证BeanUtil是否存在性能问题，故这篇文章可以仅供参考，不作为定论！欢迎更多朋友给出指导，谢谢！

Web项目后台输出一般需要把model转换成vo输出，但是有时候为了取巧不写model转vo的方法，直接利用spring的BeanUtils拷贝字段，那么这么做对性能影响大吗？

```java
import bean.MyBeanUtils;
import bean.Skill;
import bean.User;
import bean.UserVo;
import org.springframework.beans.BeanUtils;

import java.util.*;

public class App {
    public static void main(String[] args) {
        List<Skill> skills = new LinkedList<>();
        skills.add(new Skill("游泳", 10));
        skills.add(new Skill("健身", 9));
        Set<Skill> set = new HashSet<>();
        set.add(new Skill("跑步", 11));
        set.add(new Skill("跑步", 11));
        Map<Skill, Skill> map = new HashMap<>();
        map.put(new Skill("跑步", 11), new Skill("跑步", 11));
        map.put(new Skill("跑步", 11), new Skill("跑步", 11));
        User user = new User("小红", 18, skills, set, map);
        UserVo vo = new UserVo();

        int n = 1000000;
        long now, end;


        // use BeanUtils
        now = System.currentTimeMillis();
        for (int i = 0; i < n; i++) {
            BeanUtils.copyProperties(user, vo);
        }
        end = System.currentTimeMillis();
        System.out.println(end - now);


        // use MyBeanUtils
        now = System.currentTimeMillis();
        for (int i = 0; i < n; i++) {
            MyBeanUtils.copyFields(user, vo);
        }
        end = System.currentTimeMillis();
        System.out.println(end - now);


        vo = new UserVo();
        MyBeanUtils.copyFields(user, vo, "age");
        System.out.println(vo);

        vo = new UserVo();
        MyBeanUtils.copyWhiteListFields(user, vo, new String[]{"age", "map"});
        System.out.println(vo);
    }
}

```

任何时候直接使用vo.setXX(model.getxx())都比反射来的快，BeanUtils始终无法跟它比速度。BeanUtils的实现还是比较优化的，它把Class能缓存的信息都做了缓存，即不必每次对Class做反射拿getter/setter方法。

我对BeanUtils做了进一步的缓存，这应该是把缓存用到极致了，但是只有当数据量非常庞大(n>1000000)才能显现出非常大的优势，但一般场景下BeanUtils足以应付。

MyBeanUtils比Beanutils更适合做Controller层的工具使用，在追求高并发、吞吐量的应用下，这点缓存带来的速度的飞跃是非常值得的。


```java
package bean;

import org.springframework.beans.BeanUtils;
import org.springframework.util.Assert;

import java.beans.PropertyDescriptor;
import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.ConcurrentHashMap;

public class MyBeanUtils extends BeanUtils {

    static final ConcurrentHashMap<MyKey, List<MyValue>> myCache = new ConcurrentHashMap<>();

    public static void copyWhiteListFields(Object from, Object to, String[] whiteList) {
        Assert.notNull(whiteList, "whiteList is null");
        handle(from, to, whiteList, false);
    }

    public static void copyFields(Object from, Object to, String... ignores) {
        Assert.notNull(from, "from is null");
        Assert.notNull(to, "to is null");
        handle(from, to, ignores, true);
    }

    private static void handle(Object from, Object to, String[] fields, boolean isIgnore) {
        MyKey myKey = new MyKey(from.getClass(), to.getClass(), fields, isIgnore);
        List<MyValue> list = getValueList(myKey);
        list.stream().forEach(x -> {
            try {
                x.setter.invoke(to, x.getter.invoke(from));
            } catch (Exception e) {
            }
        });
    }

    private static List<MyValue> getValueList(MyKey myKey) {
        List<MyValue> list = myCache.get(myKey);
        return list == null ? processKey(myKey) : list;
    }

    // This call is slow so we do it once.
    private static List<MyValue> processKey(MyKey myKey) {
        PropertyDescriptor[] pdsFrom = BeanUtils.getPropertyDescriptors(myKey.from);
        List<MyValue> list = new LinkedList<>();
        Arrays.stream(pdsFrom)
                .filter(pd -> !isIgnore(pd.getName(), myKey.fields, myKey.isIgnore))
                .filter(pd -> !"class".equals(pd.getName()))
                .forEach(pd -> {
                    try {
                        Method getter = pd.getReadMethod();
                        Method setter = BeanUtils.getPropertyDescriptor(myKey.to, pd.getName()).getWriteMethod();
                        setter.setAccessible(true);
                        getter.setAccessible(true);
                        list.add(new MyValue(getter, setter));
                    } catch (Exception e) {
                    }
                });
        myCache.put(myKey, list);
        return list;
    }

    private static boolean isIgnore(String name, String[] fields, boolean isIgnore) {
        if (isIgnore) {
            return fields == null ? false : Arrays.stream(fields).anyMatch(item -> item.equals(name));
        } else {
            return !Arrays.stream(fields).anyMatch(item -> item.equals(name));
        }
    }

    private static class MyKey {
        public Class from;
        public Class to;
        public String[] fields;
        public boolean isIgnore;

        public MyKey(Class from, Class to, String[] fields, boolean isIgnore) {
            this.from = from;
            this.to = to;
            this.fields = fields;
            this.isIgnore = isIgnore;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof MyKey)) return false;
            MyKey myKey = (MyKey) o;
            return isIgnore == myKey.isIgnore &&
                    Objects.equals(from, myKey.from) &&
                    Objects.equals(to, myKey.to) &&
                    Arrays.equals(fields, myKey.fields);
        }

        @Override
        public int hashCode() {
            int result = Objects.hash(from, to, isIgnore);
            result = 31 * result + Arrays.hashCode(fields);
            return result;
        }
    }

    private static class MyValue {
        public Method getter;
        public Method setter;

        public MyValue(Method getter, Method setter) {
            this.getter = getter;
            this.setter = setter;
        }
    }
}
```

类似工具：
[https://github.com/DozerMapper/dozer/](https://github.com/DozerMapper/dozer/)
不同点在于可以配置映射的字段名。
