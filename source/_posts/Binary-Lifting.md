---
title: Binary Lifting
date: 2021-04-26 20:37:02
category:
    - 数据结构
tags:
---
# Kth Ancestor of a Tree Node
[1483. Kth Ancestor of a Tree Node](https://leetcode.com/problems/kth-ancestor-of-a-tree-node/)

给定一棵二叉树，给定一个 node 和 k，实现方法 `int getKthAncestor(int node, int k)` 找到该 node 第 k 个上级节点。如图：

![](/blog/2021/04/26/Binary-Lifting/tree.svg)

getKthAncestor(3, 1) = 1;
getKthAncestor(6, 2) = 0;
getKthAncestor(6, 3) = -1;  

Constraints:

1 <= k <= n <= $5\*10^4$
parent[0] == -1 indicating that 0 is the root node.
0 <= parent[i] < n for all 0 < i < n
0 <= node < n
There will be at most $5\*10^4$ queries.

思路：
令 dp[i,j] 为节点 i 的第 $2^j$ 个上级，则：
dp[i,0] = parent[i] when j == 0;
dp[i,j] = dp[dp[i,j-1],j-1] when j > 0; 

![](/blog/2021/04/26/Binary-Lifting/dp.svg)
假设有3个节点，u、w、v 的距离都为 $2^{j-1}$，则 v 的第 $2^j$ 个上级为 u；
即：dp[v,j] = dp[dp[v,j-1], j-1] = dp[w,j-1] = u

由于任意一个正整数都可以用2的幂次方表示（即二进制表示），则第 k 个上级可以表示为：
k=$2^a+2^b+...+2^z$
parent(u, k) = parent(u, $2^a+2^b+...+2^z$) = parent(w, $2^b+...+2^z$),
其中 w = parent(u, $2^a$)
parent(w, $2^b+...+2^z$) = parent(v, $2^y+2^z$),
其中 v = parent(w, $2^b+...+2^x$)
parent(v, $2^y+2^z$) = $\alpha$
即：parent(u, k) = $\alpha$.

查找的时间复杂度为：$O(n\*log_2k)$

```java
class TreeAncestor {
    int[][] dp;
    
    public TreeAncestor(int n, int[] parent) {
        dp = new int[n][17];
        for(int i = 0; i < n; i++) {
            dp[i][0] = parent[i];
        }
        for(int j = 1; j < 17; j++) {
            for(int i = 0; i < n; i++) {
                int p = dp[i][j-1];
                dp[i][j] = p == -1 ? -1 : dp[p][j-1];
            }
        }
    }
    
    public int getKthAncestor(int node, int k) {
        for(int j = 16; j >= 0; j--) {
            if(((1 << j) & k) != 0) {
                node = dp[node][j];
                if(node == -1) return -1;
            }
        }
        return node;
    }
}

/**
 * Your TreeAncestor object will be instantiated and called as such:
 * TreeAncestor obj = new TreeAncestor(n, parent);
 * int param_1 = obj.getKthAncestor(node,k);
 */
```

# Lowest Common Ancestor of a Binary Tree
[236. Lowest Common Ancestor of a Binary Tree
](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/)

# 参考
https://www.youtube.com/watch?v=oib-XsjFa-M
