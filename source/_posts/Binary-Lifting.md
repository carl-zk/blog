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

在一棵二叉树上找到两个节点 u 和 v 的最低公共父节点。

方法：

- 构造 dp[i][j], 即 节点 i 的第 $2^j$ 个父级节点；
- 若 level[u] < level[v], swap(u, v);
- 则 diff = level[u] - level[v], u 上移 diff 层与 v 达到同级；
- 若 u == v 则 return u;
- j 从 $log_2n$ 到 0 遍历，若 dp[u][j] != dp[v][j] 则 u = dp[u][j]; v = dp[v][j];
- 返回 dp[u][0]

核心在于将 u 和 v 置于同级，初始搜索空间为[0, h]（二叉树高度 h）：
1. 若其父级节点不同，则更新 u、v，其搜索空间变为 [0, h/2];
2. 否则其搜索空间变为 [h/2, h];

![](/blog/2021/04/26/Binary-Lifting/search.svg)

如图：
若 u、v 同在第 h 层且 u != v，
第一次取 p = parent(u, h/2)，q = parent(v, h/2)， p != q，则 u = p, v  = q，其搜索区间变为 [0, h/2]；
第二次取 p = parent(u, h/4), q = parent(v, h/4)，p == q，其搜索区间变为 [h/4, h/2];
同理，第三次 p != q, 则 u = p, v = q，其搜索区间变为 [h/4, h3/8];
最终 u != v 但 parent(u) == parent(v).

查找的时间复杂度为 $O(log_2h)$.

类比二分查找：
用二分查找 arr = {1, 1, 1, 2, 2, 2, 2, 2, 2} 中最后一个1的位置。
一般的二分查找写法：
```java
int binarySearchLastIndexOf1(int[] arr) {
    int l = 0, r = arr.length - 1;
    while (l <= r) {
        int mid = (l + r) >> 1;
        if (arr[mid] == 1) {
            l = mid + 1;
        } else {
            r = mid - 1;
        }
    }
    return r;
}
```

Binary Lifting 写法：
```java
int binSearchLastIndexOf1(int[] arr) {
    int n = arr.length, h = (int) (Math.log(n) / Math.log(2));
    int i = n - 1;
    if (arr[i] == 1) return i;
    for (int j = h; j >= 0; j--) { // 每次搜索步长为 2^j
        if ((1 << j) < i && arr[i - (1 << j)] != 1) { // 如果arr[k] != 1，上移i到k
            i -= 1 << j;
        }
    }
    //arr[i] != 1，但 arr[i-1] == 1
    return i - 1;
}

public static void main(String[] args) {
    Solution solution = new Solution();
    int[][] arrs = {{1, 1, 1, 2, 2, 2, 2, 2, 2}, {1, 1, 1, 1, 1, 2, 2, 2}, {1, 2, 2, 2}};
    for (int[] arr : arrs) {
        System.out.println(solution.binarySearchLastIndexOf1(arr) + "; " + solution.binSearchLastIndexOf1(arr));
    }
}
```

Binary Lifting 也是将搜索空间分为两半，每搜索一次空间减半，虽然不如二分查找直观。有兴趣的可以把下面的代码（Binary Lifting方式）改成普通二分查找方式。


```java
/**
 * Definition for a binary tree node.
 * public class TreeNode {
 *     int val;
 *     TreeNode left;
 *     TreeNode right;
 *     TreeNode(int x) { val = x; }
 * }
 */
class Solution {
    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        List<TreeNode> nodes = new ArrayList<>();
        List<Integer> P = new ArrayList<>();
        int[] ids = new int[]{-1, -1}, levs = new int[]{0, 0};
        dfs(root, 0, nodes, P, p, q, ids, levs, 0);
        if (levs[0] < levs[1]) {
            swap(ids);
            swap(levs);
        }
        int n = nodes.size(), lg = (int) (Math.log(n) / Math.log(2)), diff = levs[0] - levs[1];
        int[][] dp = new int[n][lg + 1];
        for (int i = 0; i < n; i++) {
            dp[i][0] = P.get(i);
        }
        for (int l = 1; l <= lg; l++) {
            for (int i = 0; i < n; i++) {
                int par = dp[i][l - 1];
                if (par >= 0) {
                    dp[i][l] = dp[par][l - 1];
                } else {
                    dp[i][l] = -1;
                }
            }
        }
        for (int j = lg; j >= 0; j--) {
            if (((1 << j) & diff) != 0) {
                ids[0] = dp[ids[0]][j];
            }
        }
        if (ids[0] == ids[1]) {
            return nodes.get(ids[0]);
        }
        for (int j = lg; j >= 0; j--) {
            if (dp[ids[0]][j] != dp[ids[1]][j]) {
                ids[0] = dp[ids[0]][j];
                ids[1] = dp[ids[1]][j];
            }
        }
        return nodes.get(dp[ids[0]][0]);
    }

    void swap(int[] arr) {
        int tmp = arr[0];
        arr[0] = arr[1];
        arr[1] = tmp;
    }

    void dfs(TreeNode node, int parent, List<TreeNode> nodes, List<Integer> parents, TreeNode p, TreeNode q, int[] ids, int[] levs, int lev) {
        if (node == null) {
            return;
        }
        if (p == node) {
            ids[0] = nodes.size();
            levs[0] = lev;
        }
        if (q == node) {
            ids[1] = nodes.size();
            levs[1] = lev;
        }
        nodes.add(node);
        parents.add(parent);
        int par = nodes.size() - 1;
        dfs(node.left, par, nodes, parents, p, q, ids, levs, lev + 1);
        dfs(node.right, par, nodes, parents, p, q, ids, levs, lev + 1);
    }
}
```

# 参考
https://www.youtube.com/watch?v=oib-XsjFa-M
https://www.geeksforgeeks.org/lca-in-a-tree-using-binary-lifting-technique/