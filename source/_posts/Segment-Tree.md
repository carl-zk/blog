---
title: Segment Tree
date: 2020-02-28 19:27:37
category:
    - 数据结构
tags: 
    - python
---
## Brief Introduction
线段树是一棵完全二叉树，它的每个节点代表一个区间，子节点的区间是父节点的区间的子区间。
![](/2020/02/28/Segment-Tree/st1.svg)
如图，是一棵高度h=5的完全二叉树（即：叶节点只存在于第h和第h-1层）。每个节点保存了所涵盖的区间信息。
线段树可以用来快速查询区间信息，例如给定一个数组 arr = [10, 3, 23, 34, 2, 21, 3, 4, 9, 1]; 
1. 查询任意区间[L, R], 0 <= L <= R < arr.len 的和；
2. 修改任意一个arr[i]；

如查询[2, 7]之间的和，只需sum([2, 2] + [3, 4] + [5, 7])三个节点之和即可。
如修改arr[2]，只需修改节点[0, 9] [0, 4] [0, 2] [2, 2] 四个节点即可。
查询和修改的时间复杂度都为O(logN),N=len(arr)，即arr的长度。而建树的时间复杂度为O(N).

## Recursive methods for Segment Trees
二叉树一般用数组存储，且如果父节点的下标为i，则：左孩子的下标为2\*i+1，右孩子下标为2\*i+2。
完全二叉树的性质：有n个叶节点，就有n-1个非叶节点。
用数组tree[]保存线段树的节点，则给定一个len(arr)=n的数组，至少需要len(tree) >= 2\*n-1构建线段树。如果n是2的幂，则len(tree)=2\*n-1，否则len(tree) = {% katex %}2 * 2^{\left\lceil\log _{2} n\right\rceil}-1{% endkatex %}.例如：len(arr) = 4, 则线段树的结构为：
![](/2020/02/28/Segment-Tree/st2.svg)
(注：绿色为叶节点，index为该节点在tree[]中的位置)
其大小len(tree) = 2 \* len(arr) - 1 = 7.
若len(arr) = 10, 则线段树的结构为：
![](/2020/02/28/Segment-Tree/st3.svg)
其大小len(tree) = {% katex %}2 * 2^{4} - 1{% endkatex %} = 31. ({% katex %}\left\lceil\log _{2} len(arr)\right\rceil = 4{% endkatex %}) 有12个无用叶节点，有2 \* len(arr) - 1 = 19个有用节点（10个叶节点+9个非叶节点）。
由此可以看出，当len(arr)为2的幂时，线段树无无用节点，最后一个叶节点的index刚好等于2\*len(arr)-1 - 1；当len(arr)不是2的幂时，树中存在无用节点，最后一个叶节点的index可能大于2\*len(arr)-1（当len(arr)=10，最后一个叶节点index=24)，除非无用节点只出现在最底层末端（例如len(arr)=3、5or7时）。无用节点必然成对儿存在。（因为有一个叶节点就有两个无用节点）

### Build Segment Tree
```java
class SegmentTree {
    int[] arr;
    int[] tree;  // 保存区间和

    public SegmentTree(int[] arr) {
        this.arr = arr;
        int n = arr.length;
        int h = 1;
        while(h < n) h <<= 1;
        this.tree = new int[2 * h - 1];
        build(0, 0, n - 1);
    }

    private void build(int treeIndex, int range_left, int range_right) {
        if(range_left == range_right) {
            tree[treeIndex] = arr[range_left];
            return;
        }
        int mid = range_left + (range_right - range_left) / 2;
        build(2 * treeIndex + 1, range_left, mid);
        build(2 * treeIndex + 2, mid + 1, range_right);
        tree[treeIndex] = merge(tree[2 * treeIndex + 1], tree[2 * treeIndex + 2]);
    }

    private int merge(int nodeA, int nodeB) {
        return nodeA + nodeB;
    } 
}

```
递归构建，range from 0 to n-1，即n个叶节点，同时有n-1个非叶节点，build()总共被调用2*n-1次，所以时间复杂度为O(logn).

### Query
```java
public int query(int treeIndex, int range_left, int range_right, int query_left, int query_right) {
    if(range_left > query_right || range_right < query_left) return 0;
    if(query_left <= range_left && range_right <= query_right) return tree[treeIndex];
    int mid = range_left + (range_right - range_left) / 2;
    if(mid >= query_right) return query(2 * treeIndex + 1, range_left, mid, query_left, query_right);
    else if(mid < query_left) return query(2 * treeIndex + 2, mid + 1, query_left, query_right);
    return merge(res_left, res_right);
    int res_left = query(2 * treeIndex + 1, range_left, mid, query_left, query_right);
    int res_right = query(2 * treeIndex + 2, mid + 1, query_left, query_right);
    return merge(res_left, res_right);
}

```

### Update
```java
public void update(int treeIndex, int range_left, int range_right, int arrIndex, int val) {
    if(range_left == range_right) {
        tree[treeIndex] = val;
        arr[arrIndex] = val;
        return;
    }
    int mid = range_left + (range_right - range_left) / 2;
    if(mid >= arrIndex) update(2 * treeIndex + 1, range_left, mid, arrIndex, val);
    else update(2 * treeIndex + 2, mid + 1, range_right, val);
    tree[treeIndex] = merge(tree[2 * treeIndex + 1], tree[2 * treeIndex + 2]);
}
```
查询和更新的时间复杂度都为O(logn).

## Lazy Propagation
延迟传播是线段树的延伸。
上面的update()只是更新某一个值，时间复杂度是O(logn)。如果要更新一个范围的值，效率自然就低了。因为：
1. 可能对某个父节点更新多次；
2. 频繁更新的某些节点并不在query范围内；

延迟传播就是解决这两个问题，一个节点只更新一次，不在query范围内的节点不会更新。它的时间复杂度仍是O(logn)。
延迟传播正如它的名字所言，它的更新操作是延迟的，即只有当该节点被access/query时再更新。如上述求区间和问题，我们增加一个数组lazy[]，lazy[i]不为0表示该节点有增量。

### Update
```java
/**
val : 增量
*/
public void lazyUpdate(int treeIndex, int range_left, int range_right, int lo, int hi, int val) {
    if(range_left > hi || range_right < lo) return;
    if(lazy[treeIndex] != 0) {
        tree[treeIndex] += (range_right - range_left + 1) * lazy[treeIndex];
        if(range_left != range_right) {
            lazy[2 * treeIndex + 1] += lazy[treeIndex];
            lazy[2 * treeIndex + 2] += lazy[treeIndex];
        }
        lazy[treeIndex] = 0;
    }
    if(lo <= range_left && range_right <= hi) {
        tree[treeIndex] += val;
        if(range_left != range_right) {
            lazy[2 * treeIndex + 1] += val;
            lazy[2 * treeIndex + 2] += val;
        }
        return;
    }
    int mid = range_left + (range_right - range_left) / 2;
    lazyUpdate(2 * treeIndex + 1, range_left, mid, lo, hi, val);
    lazyUpdate(2 * treeIndex + 2, mid, range_right, lo, hi, val);
    tree[treeIndex] = merge(tree[2 * treeIndex + 1], tree[2 * treeIndex + 2]);
}
```

### Query
```java
public int lazyQuery(int treeIndex, int range_left, int range_right, int lo, int hi) {
    if(range_left > hi || range_right < lo) return;
    if(lazy[treeIndex] != 0) {
        tree[treeIndex] += (range_right - range_left + 1) * lazy[treeIndex];
        if(range_left != range_right) {
            lazy[2 * treeIndex + 1] += lazy[treeIndex];
            lazy[2 * treeIndex + 2] += lazy[treeIndex];
        }
        lazy[treeIndex] = 0;
    }
    if(lo <= range_left && range_right <= hi) return tree[treeIndex];
    int mid = range_left + (range_right - range_left) / 2;
    if(mid >= hi) return lazyQuery(2 * treeIndex + 1, range_left, mid, lo, hi);
    else if(mid < lo) return lazyQuery(2 * treeIndex + 2, mid + 1, range_right, lo, hi);
    return merge(lazyQuery(2 * treeIndex + 1, range_left, mid, lo, hi), lazyQuery(2 * treeIndex + 2, mid + 1, range_right, lo, hi));
}
```

## Practice
https://leetcode.com/problems/falling-squares/
题：给一组俄罗斯方块，都是正方形，每个方块用[i, len]表示，i表示该方块左下角坠落的x轴坐标，len表示边长。求每个方块坠落后，最高方块的y轴坐标。
例1：
Input: [[1, 2], [2, 3], [6, 1]]
Output: [2, 5, 5]
例2：
Input: [[100, 100], [200, 100]]
Output: [100, 100]

1 <= positions.length <= 1000.
1 <= positions[i][0] <= 10^8.
1 <= positions[i][1] <= 10^6.

```java
class Solution {
    public List<Integer> fallingSquares(int[][] positions) {
        int range_left = Integer.MAX_VALUE, range_right = 0;
        for(int[] pos : positions) {
            range_left = Math.min(range_left, pos[0]);
            range_right = Math.max(range_right, pos[0] + pos[1]);
        }
        Node root = new Node(range_left, range_right - 1);
        List<Integer> ans = new ArrayList<>(positions.length);
        for(int[] pos : positions) {
            int h = search(root, pos);
            update(root, pos, h + pos[1]);
            ans.add(root.height);
        }
        return ans;
    }
    
    private int search(Node root, int[] pos) {
        if(root.range_right < pos[0] || root.range_left > pos[0] + pos[1] - 1) return 0;
        if(root.lazy_height != 0) {
            root.height = Math.max(root.height, root.lazy_height);
            if(root.range_left != root.range_right) {
                root.getLeft().lazy_height = Math.max(root.getLeft().lazy_height, root.lazy_height);
                root.getRight().lazy_height = Math.max(root.getRight().lazy_height, root.lazy_height);
            }
            root.lazy_height = 0;
        }
        if(pos[0] <= root.range_left && root.range_right <= pos[0] + pos[1] - 1) return root.height;
        return Math.max(search(root.getLeft(), pos), search(root.getRight(), pos));
    }
    
    private void update(Node root, int[] pos, int h) {
        if(root.range_right < pos[0] || root.range_left > pos[0] + pos[1] - 1) return;
        if(root.lazy_height != 0) {
            root.height = Math.max(root.height, root.lazy_height);
            if(root.range_left != root.range_right) {
                root.getLeft().lazy_height = Math.max(root.getLeft().lazy_height, root.lazy_height);
                root.getRight().lazy_height = Math.max(root.getRight().lazy_height, root.lazy_height);
            }
            root.lazy_height = 0;
        }      
        root.height = Math.max(root.height, h);
        if(pos[0] <= root.range_left && root.range_right <= pos[0] + pos[1] - 1) {
            if(root.range_left != root.range_right) {
                root.getLeft().lazy_height = Math.max(root.getLeft().lazy_height, h);
                root.getRight().lazy_height = Math.max(root.getRight().lazy_height, h);
            }
            return;
        }
        update(root.getLeft(), pos, h);
        update(root.getRight(), pos, h);
    }
    
    class Node {
        int range_left, range_right;
        int height;
        int lazy_height;
        Node left, right;
        
        public Node(int range_left, int range_right) {
            this.range_left = range_left;
            this.range_right = range_right;
        }
        
        public int getRangeMiddle() {
            return range_left + (range_right - range_left) / 2;
        }
        
        public Node getLeft() {
            if(left == null) left = new Node(range_left, getRangeMiddle());
            return left;
        }
        
        public Node getRight() {
            if(right == null) right = new Node(getRangeMiddle() + 1, range_right);
            return right;
        }
    }
}
```

上面的写法使用了坐标的最大最小值，其范围可达 10^8，而数组长度仅1000，所以坐标最多2000个，使用坐标压缩可以将区间范围从10^8缩小到10^3.

```java
class Solution {
    public List<Integer> fallingSquares(int[][] positions) {
        Set<Integer> coords = new HashSet<>();
        for(int[] pos : positions) {
            coords.add(pos[0]);
            coords.add(pos[0] + pos[1] - 1);
        }
        List<Integer> sortedCoords = new ArrayList<>(coords);
        Collections.sort(sortedCoords);
        Map<Integer, Integer> index = new HashMap<>();
        int n = 0;
        for(int i : sortedCoords) index.put(i, n++);
        SegmentTree stree = new SegmentTree(n);
        List<Integer> ans = new ArrayList<>(positions.length);
        for(int[] pos : positions) {
            int i = index.get(pos[0]);
            int j = index.get(pos[0] + pos[1] - 1);
            int h = stree.query(0, 0, n - 1, i, j) + pos[1];
            stree.update(0, 0, n - 1, i, j, h);
            ans.add(stree.tree[0]);
        }
        return ans;
    }
    
    class SegmentTree {
        int[] tree;
        int[] lazy;
        
        public SegmentTree(int n) {
            int t = 1;
            while(t < n) t <<= 1;
            tree = new int[2 * t - 1];
            lazy = new int[tree.length];
        }
        
        public int query(int treeIndex, int lo, int hi, int i, int j) {
            if(lo > j || hi < i) return 0;
            if(lazy[treeIndex] != 0) {
                tree[treeIndex] = Math.max(tree[treeIndex], lazy[treeIndex]);
                if(lo != hi) {
                    lazy[2 * treeIndex + 1] = lazy[treeIndex];
                    lazy[2 * treeIndex + 2] = lazy[treeIndex];
                }
                lazy[treeIndex] = 0;
            }
            if(i <= lo && hi <= j) return tree[treeIndex];
            int mid = lo + (hi - lo) / 2;
            return Math.max(query(2 * treeIndex + 1, lo, mid, i, j), query(2 * treeIndex + 2, mid + 1, hi, i, j));
        }

        public void update(int treeIndex, int lo, int hi, int i, int j, int height) {
            if(lo > j || hi < i) return;
            if(lazy[treeIndex] != 0) {
                tree[treeIndex] = Math.max(tree[treeIndex], lazy[treeIndex]);
                if(lo != hi) {
                    lazy[2 * treeIndex + 1] = Math.max(lazy[2 * treeIndex + 1], lazy[treeIndex]);
                    lazy[2 * treeIndex + 2] = Math.max(lazy[2 * treeIndex + 2], lazy[treeIndex]);
                }
                lazy[treeIndex] = 0;
            }
            if(i <= lo && hi <= j) {
                tree[treeIndex] = Math.max(tree[treeIndex], height);
                if(lo != hi) {
                    lazy[2 * treeIndex + 1] = Math.max(lazy[2 * treeIndex + 1], height);
                    lazy[2 * treeIndex + 2] = Math.max(lazy[2 * treeIndex + 2], height);
                }
                return;
            }
            int mid = lo + (hi - lo) / 2;
            update(2 * treeIndex + 1, lo, mid, i, j, height);
            update(2 * treeIndex + 2, mid + 1, hi, i, j, height);
            tree[treeIndex] = Math.max(tree[2 * treeIndex + 1], tree[2 * treeIndex + 2]);
        }
    }
}
```

[2251. Number of Flowers in Full Bloom](https://leetcode.com/problems/number-of-flowers-in-full-bloom/)
```python
class Solution:
    def fullBloomFlowers(self, flowers: List[List[int]], persons: List[int]) -> List[int]:
        points = set()
        for x, y in flowers:
            points.add(x)
            points.add(y)
        for x in persons:
            points.add(x)
        sorted_points = sorted(points)
        mp = {x: i for i, x in enumerate(sorted_points)}
        root = Node(0, len(sorted_points))
        for x, y in flowers:
            insert(root, mp[x], mp[y], 1)
        ans = []
        for x in persons:
            i = mp[x]
            ans.append(query(root, i, i))
        return ans


class Node:
    __slots__ = 'l', 'r', 'v', 'lazy', 'left', 'right'

    def __init__(self, l: int, r: int, v: int = 0, lazy: int = 0):
        self.l = l
        self.r = r
        self.v = v
        self.lazy = lazy
        self.left = None if l == r else Node(l, self._mid())
        self.right = None if l == r else Node(self._mid() + 1, r)

    def _mid(self):
        return (self.l + self.r) >> 1


def insert(root: Node, l: int, r: int, v: int):
    if root.r < l or r < root.l:
        return
    elif l <= root.l and root.r <= r:
        root.v += v
        if l != r:
            root.lazy += v
    else:
        insert(root.left, l, r, v)
        insert(root.right, l, r, v)
        root.v += root.left.v + root.right.v


def query(root: Node, l: int, r: int):
    if root.r < l or r < root.l:
        return 0
    elif l <= root.l and root.r <= r:
        return root.v
    else:
        if root.lazy > 0:
            root.left.v += root.lazy
            root.right.v += root.lazy
            if root.left.l != root.left.r:
                root.left.lazy += root.lazy
            if root.right.l != root.right.r:
                root.right.lazy += root.lazy
            root.lazy = 0
        return query(root.left, l, r) + query(root.right, l, r)        
```

## Reference
https://leetcode.com/articles/a-recursive-approach-to-segment-trees-range-sum-queries-lazy-propagation/