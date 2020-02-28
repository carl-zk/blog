---
title: Segment Tree
date: 2020-02-28 19:27:37
category:
    - 数据结构
tags:
---
## Brief Introduction
线段树是一棵完全二叉树，它的每个节点代表一个区间，子节点的区间是父节点的区间的子区间。
![](/blog/2020/02/28/Segment-Tree/st1.svg)
如图，是一棵高度h=5的完全二叉树（即：叶节点只存在于第h和第h-1层）。每个节点保存了所涵盖的区间信息。
线段树可以用来快速查询区间信息，例如给定一个数组 arr = [10, 3, 23, 34, 2, 21, 3, 4, 9, 1]; 
1. 查询任意区间[L, R], 0 <= L <= R < arr.len 的和；
2. 修改任意一个arr[i]；

## Recursive methods for Segment Trees
完全二叉树的性质：有n个叶节点，就有n-1个非叶节点。
用数组tree[]保存线段树的节点，则给定一个len(arr)=n的数组，至少需要len(tree) >= 2\*n-1构建线段树。如果n是2的幂，则len(tree)==2\*n-1，否则len(tree) = $2 * 2^{\left\lceil\log _{2} n\right\rceil}-1$.例如：len(arr) = 4, 则线段树的结构为：
![](/blog/2020/02/28/Segment-Tree/st2.svg)
(注：绿色为叶节点，index为该节点在tree[]中的位置)
其大小len(tree) = 2 \* len(arr) - 1 = 7.
若len(arr) = 10, 则线段树的结构为：
![](/blog/2020/02/28/Segment-Tree/st3.svg)
其大小len(tree) = $2 * 2^{4} - 1$ = 31. ($\left\lceil\log _{2} len(arr)\right\rceil = 4$) 有12个无用叶节点，有2 \* len(arr) - 1 = 19个有用节点（10个叶节点+9个非叶节点）。
由此可以看出，当len(arr)为2的幂时，线段树无无用节点，最后一个叶节点的index刚好等于2\*len(arr)-1 - 1；当len(arr)不是2的幂时，树中存在无用节点，最后一个叶节点的index会大于2\*len(arr)-1（当len(arr)=10，最后一个叶节点index=24)。

## Practice
https://leetcode.com/problems/falling-squares/

## Reference
https://leetcode.com/articles/a-recursive-approach-to-segment-trees-range-sum-queries-lazy-propagation/