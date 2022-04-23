---
title: JVM参数那点事儿
date: 2017-11-18 17:01:39
category: java
tags:
---
[JVM参数](https://www.cnblogs.com/edwardlauxh/archive/2010/04/25/1918603.html)
[JVM参数](https://www.cnblogs.com/redcreen/archive/2011/05/04/2037057.html)
[美团点评JVM调优实例](https://mp.weixin.qq.com/s?__biz=MjM5NjQ5MTI5OA==&mid=2651747273&idx=1&sn=7f947064a41eeecb6816a5d0838581ae&chksm=bd12aa848a65239289d5c39264e89bd175f377f6554bfe93b37ad6498cf13deff356333c5398&mpshare=1&scene=1&srcid=0108Pp81UenqcrqRmaMO1QNW&pass_ticket=w9AQASPqUnr1vwbOOlNXlTVA9QD8RoqlKcW5%2FRGKjfiKy9ShiDmnCQTcz4Z2UZQi#rd)
### JVM内存模型
在jdk8之前，JVM的内存模型是这个样子的：
![](/2017/11/18/JVM%E5%8F%82%E6%95%B0%E9%82%A3%E7%82%B9%E4%BA%8B%E5%84%BF/mem.svg)
- 程序计数器：可看作是当前线程所执行的字节码的行号指示器。在某一时刻，一个cpu（或多核cpu中的一核）只能被一个线程占用，java程序又是支持多线程的，所以必然将**程序计数器**设计成线程私有，以便于多个线程的切换/恢复。
- 虚拟机栈：同样是线程私有。它描述了Java方法执行的内存模型：每个方法执行都会创建一个栈帧（Stack Frame）用于存储局部变量表、操作数栈、动态链接、方法出口等信息，每个方法从调用到完成都对应一个栈帧从虚拟机栈中入栈到出栈的过程。(StackOverflowError: fun(){fun();})
- 本地方法栈：与虚拟机栈作用类似，区别在于虚拟机栈为虚拟机执行字节码服务，本地方法栈为虚拟机使用到的Native方法服务。HotSpot虚拟机将两栈合二为一了（这体现出JVM 规范和JVM具体实现的差异）。
- 堆：最大的一块，几乎所有对象实例都放在这里。由于垃圾收集器都采用分代收集算法，所以堆又可细分为新生代和老年代。新生代又可分为Eden空间、From Survivor空间、To Survivor空间等。
- 方法区：也被称为永久代，存储已被加载的类的信息、常量、静态变量、即时编译器编译的代码等。又叫 Non-Heap，目的与java堆区分。jdk7开始已考虑将此块去除（字符串常量池已从方法区中搬走），jdk8中已根本性去除，之前虚拟机参数-XX:PermSize、-XX:MaxPermSize均已失效，被Metaspace（元数据区）取代，Metaspace不属于JVM内存，而是本地内存（Native Memory），默认没有上限，可用-XX:MaxMetaspaceSize指定大小。之所以移除是因为-XX:MaxPermSize很难设置，容易出现内存不足。
- 直接内存（Direct Memory）：不是虚拟机规范中定义的内存区域，不受堆大小的限制，属于容易被忽略的内存，它也可能出现OutOfMemoryError。

### 内存参数
了解了虚拟机内存模型，就来看看有哪些相关的参数吧。

|Name   |  Description | Example |
|:----- | :-------: | :------ |
|-Xms   | 堆最小值    |  -Xms32m |
|-Xmx   | 堆堆大值    |  -Xmx256m |
|-Xmn   | 新生代大小   |  -Xmn128m |
|-XX:SurvivorRatio | Eden/一个Survivor | -XX:SurvivorRatio=8 |

以上就是JVM启动设置的内存参数，其它Xss、MaxMetaspaceSize等最好不要动。Xmx=Xmn+老年代，Eden与Survivor默认比例为8.可使用`jstat`命令查看具体内存使用情况。

### GC收集器参数

### GC日志参数
-XX:+PrintGC
-XX:+PrintGCDetails
-XX:+PrintGCTimeStamps
-XX:+PrintHeapAtGC
-Xloggc:filename

