---
title: SkipList
date: 2020-03-05 20:09:10
category:
    - 数据结构
tags:
---

This article will bring you into a fancy world of Skip Lists, come with me and enjoy your journey. 

## Start from Binary Search
### 1-d array
Give you a sorted array a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], query if number x exists. Which algorithm would you like to use? Binary Search, right? The time complexity is $O(\lg n)$. e.g. search number 10, the way is:
![](/blog/2020/03/05/SkipList/img1.svg)
6 ---> 9 ---> 10, Find!
You always choose the middle one to compare. Easy right?! But why binary search is so fast? Caus every time you search, you can just jump/skip a half of numbers.
### 2-d array
Now give you 2-d sorted array, like:
[[1, 20, 30, 40, 50],
 [1, 20, 34, 42, 55],
 [4, 25, 36, 49, 58]]
 
-  a[i][j] is no less than a[i][j-1]
- a[i+1][j] is no less than a[i][j]
- a[i+1][j] is no bigger than a[i][j+1]

search if number x exists. Still Binary Search? let's say row = m, column = n, then time complexity would be $O(m \lg n)$. However, there is another way to search in $O(m+n)$. This way is to start from top left to the bottom right one by one, when you reach the end or the next number bigger than x, go down to the next level. e.g. x = 49, the search way is:
![](/blog/2020/03/05/SkipList/img2.svg)
It seems like a better way to choose, much faster than binary search generally. Now let change array to linked list, so it's a 2-d linked list matrix, you can't use binary search anymore, $O(m+n)$ is your best performance.
Now let's delete some numbers, I'll give you a sparse 2-d linked list matrix, like this:
![](/blog/2020/03/05/SkipList/img3.svg)
From top to bottom, let's say, level 2 to level 0.
You can search much faster. Because level 2 only has 3 numbers, level 1 only has four numbers, you can 'jump' (skip some numbers than level 0)  at these levels. How fast it could be? To be simple, I'll give you a matrix that each level has half count of the next level's numbers:

level $\lg n$: 1 numbers
...
level k: $\frac {n}{2^k}$ numbers
...
level 2: $\frac {n}{2^2}$ numbers
level 1: $\frac {n}{2^1}$ numbers
level 0: n numbers

So the level's hight is $\lg n$, let's say each level you would most visit 2 numbers (if you visit more, then you would jump/skip more next levels), then the time complexity is $2 * \lg n = O(\lg n)$, same as using binary search. Oh my god, did I just search the bottom linked list in $O(\lg n)$? That's the essence of Skip Lists you've just learned.

## Skip Lists
The real skip list is just a single linked list, each node has two fields, key and forward[],
```java
class Node {
    int key;
    Node[] forward;

    public Node(int key, int level) {
        this.key = key;
        this.forward = new Node[level + 1];
    }
}
```
each node has different levels height, a.k.a different forward array length, node.forward[i] reference/linked to the next bigger number, like this:
![](/blog/2020/03/05/SkipList/eg1.svg)

How to search? we start from header, from top level to bottom, 
```java
public boolean search(int target) {
    Node e = head;
    for (int i = level; i >= 0; i--) {
        while (e.forward[i] != null && e.forward[i].key < target) {
            e = e.forward[i];
        }
    }
    return e.forward[0] != null && e.forward[0].key == target;
}
```
at each level, if we can move forward, then go, else we move down to the next level, until level 0.

Why each node has a different level? Because 'perfect skip lists' don't exist. Make each level is exactly half of the next level would be extremely complicated. So to maintain $O(\lg n)$ still possible, we can distribute each node randomly at different level and keep the possibility of each node would be at level 1 is $\frac {1}{2}$, at level 2 is $\frac {1}{2^2}$, ..., at level k is $\frac {1}{2^k}$, more higher more spare, then we can treat this skip list as a full binary tree. Think about this, 
level 0: every node at this level.
level 1: every two nodes, one would be at this level, because the possibility is $\frac {1}{2}$.
level 2: every four nodes, one would be at this level.
...
level $\lg n$: would be only one node at this level.
See, when level upper one layer, the numbers would cut a half, like a binary tree.

How to make this possibility happen? we call it flip a coin. You will get head in possibility 1/2 when flipping only one time, get two continuous head in 1/4, get three continuous head in 1/8. A node gets more continuous head would be at a more higher level. e.g. there are 64 nodes at level 0, then 32 nodes would be at level 1, 16 at level 2, 8 at level 3, 4 at level 4, 2 at level 5, 1 at level 6.
```java
private int randomLevel() {
    int lev = 0;
    while (random.nextInt(2) == 0) {
        lev++;
    }
    return lev;
}
```

Now we get the random level generator we want, how do we build a skip list? Similar to search, but we have to keep the trace when we move down, then backtrace from bottom to upper to connect them to the new node.
```java
public void add(int num) {
    int newLevel = randomLevel();
    if (newLevel > this.level) {
        adjustHead(newLevel);
    }
    Node[] update = new Node[this.level + 1];
    Node e = this.head;
    for (int i = this.level; i >= 0; i--) {
        while (e.forward[i] != null && e.forward[i].key < num) {
            e = e.forward[i];
        }
        update[i] = e;
    }
    Node node = new Node(num, newLevel);
    for (int i = 0; i <= newLevel; i++) {
        node.forward[i] = update[i].forward[i];
        update[i].forward[i] = node;
    }
}
```

remove is similar to add, I just post the full code here.
```java
public class Skiplist {
    Node head;
    int level;
    Random random;

    public Skiplist() {
        this.head = new Node(-1, 0);
        this.level = -1;
        this.random = new Random();
    }

    public boolean search(int target) {
        Node e = head;
        for (int i = level; i >= 0; i--) {
            while (e.forward[i] != null && e.forward[i].key < target) {
                e = e.forward[i];
            }
        }
        return e.forward[0] != null && e.forward[0].key == target;
    }

    public void add(int num) {
        int newLevel = randomLevel();
        if (newLevel > this.level) {
            adjustHead(newLevel);
        }
        Node[] update = new Node[this.level + 1];
        Node e = this.head;
        for (int i = this.level; i >= 0; i--) {
            while (e.forward[i] != null && e.forward[i].key < num) {
                e = e.forward[i];
            }
            update[i] = e;
        }
        Node node = new Node(num, newLevel);
        for (int i = 0; i <= newLevel; i++) {
            node.forward[i] = update[i].forward[i];
            update[i].forward[i] = node;
        }
    }

    private int randomLevel() {
        int lev = 0;
        while (random.nextInt(2) == 0) {
            lev++;
        }
        return lev;
    }

    private void adjustHead(int newLevel) {
        head.forward = Arrays.copyOf(head.forward, (this.level = newLevel) + 1);
    }

    public boolean erase(int num) {
        Node e = head;
        Node[] delete = new Node[this.level + 1];
        for (int i = level; i >= 0; i--) {
            while (e.forward[i] != null && e.forward[i].key < num) {
                e = e.forward[i];
            }
            delete[i] = e;
        }
        Node del;
        if ((del = e.forward[0]) == null || del.key != num) {
            return false;
        }
        for (int i = 0; i < del.forward.length; i++) {
            delete[i].forward[i] = del.forward[i];
        }
        return true;
    }

    class Node {
        int key;
        Node[] forward;

        public Node(int key, int level) {
            this.key = key;
            this.forward = new Node[level + 1];
        }
    }
}
```

Skip Lists is a useful structure in many ways. When I first saw it, it comes out a 2-d binary search in my mind. And I don't know what's flip coins means, and why it can be so fast as red-black tree. Then I google it and learned, write my own thoughts here, hope to be helpful.




## References
https://www.cs.cmu.edu/~ckingsf/bioinfo-lectures/skiplists.pdf
https://opendsa-server.cs.vt.edu/ODSA/Books/CS3/html/SkipList.html