---
title: Wavelet Tree
date: 2020-09-16 12:19:17
category: 数据结构
tags:
---
> 最近刷题看到一个很有意思的数据结构：小波树(Wavelet Tree)。网上搜了基本都是C++实现的，我不能完全看懂，看了很多资料，大部分都不靠谱，不是图不对就是解释泛泛，最后终于找到个靠谱的论文，让我可以根据原理用Java把它实现出来，终于对它的妙处有了一点了解。

# 初识
小波树有很多应用场景，这里就从LeetCode的一道题目说起，[1157. Online Majority Element In Subarray](https://leetcode.com/problems/online-majority-element-in-subarray/)，：
实现这个类 MajorityChecker 的一个方法，
- MajorityChecker(int[] arr)，构造函数，传入一个int数组;
- int query(int left, int right, int threshold)，查询数组中下标从left到right区间中，left <= i <= right，arr[i]相同的个数 >= threshold的值，threshold * 2 > right - left + 1，不存在则返回 -1.
例如：arr=[1,1,2,2,1,1]，则 query(0, 5, 4) = 1.

# 介绍
## 建树
构造一个小波树，需要一个数组S，和这个数组中唯一元素的有序集合alphabet。假设S是一个int数组[3,3,9,1,2,1,7,6,4,8,9,4,3,7,5,9,2,7,3,5,1,3]，则alphabet是[1,2,3,4,5,6,7,8,9].
![](/2020/09/16/Wavelet-Tree/alphabet.svg)
从lo=0, hi=alphabet.length - 1的中间值alphabet[mid] (mid=(lo + hi)/2)将S划分为左右两个数组，left child 所有元素<=alphabet[mid]，right child 所有元素 > alphabet[mid]，直至子数组中元素相同为止。在划分的过程中，用数组freq记录从index=0到该元素被划分到右子树的个数。
![](/2020/09/16/Wavelet-Tree/WT.svg)
这样建造的小波树是一个平衡树，并且叶子节点个数=alphabet.length，时间复杂度为S.length*lg(alphabet.length).

## 查询
这个数据结构很容易回答这样的问题：给定数组S，问任意区间[i, j]中第k大的值。
要回答这个问题，需要从根节点root一直找到叶子节点leaf为止，问题在于向左走还是向右走。因为每个节点都有一个freq数组，freq[j]记录了从index=0到j共有几个元素要被划到右子树（j - freq[j] + 1 则是有几个元素要被划到左子树），令c=j - freq[j] + 1, 若k<=c，则向左，否则向右。向子树寻找时i和j需要做相应的映射，我们定义两个方法
mapLeft(i) : index i 映射到左子树的下标,
mapLeft(i) : index i 映射到右子树的下标。
则 mapLeft(i) = max(i - freq[i], 0), mapRight(i) = max(freq[i] - 1, 0).
一直到叶节点，查询结束，时间复杂度为lg(alphabet.length).

至于空间复杂度，在实际场景中，一般一个节点只需要存freq，并且freq可以是bit数组，查询里面有几个1用BIT(binary index tree)。

# 代码
```java
public class MajorityChecker {
    WaveletTree wtree;

    public MajorityChecker(int[] arr) {
        this.wtree = new WaveletTree(arr);
    }

    public int query(int left, int right, int threshold) {
        return wtree.query(left, right, threshold);
    }


    private class WaveletTree {
        /**
         * original array
         */
        private int[] S;
        /**
         * distinct ordered elements in {@link S}
         */
        private int[] orderedAlphabet;
        private Node root;
        /**
         * the same value in {@link S} map to its indices (ordered)
         */
        private Map<Integer, List<Integer>> v2indices;

        public WaveletTree(int[] arr) {
            this.S = arr;
            List<Integer> indices = new ArrayList<>(arr.length);
            TreeSet<Integer> set = new TreeSet<>();
            for (int i = 0; i < arr.length; i++) {
                indices.add(i);
                set.add(arr[i]);
            }
            this.orderedAlphabet = set.stream().mapToInt(Integer::intValue).toArray();
            this.v2indices = new HashMap<>();
            this.root = build(indices, 0, this.orderedAlphabet.length - 1);
        }

        /**
         * build a WT (wavelet tree)
         *
         * @param indices indices of {@link S}
         * @param lo      start index of {@link orderedAlphabet} (include)
         * @param hi      end index of {@link orderedAlphabet} (include)
         * @return root of WT
         */
        private Node build(List<Integer> indices, int lo, int hi) {
            if (indices.size() == 0) {
                return null;
            }
            if (lo == hi) {
                Node node = new Node(lo, hi);
                this.v2indices.put(this.orderedAlphabet[lo], indices);
                return node;
            }
            Node node = new Node(lo, hi);
            int mid = lo + (hi - lo) / 2;
            List<Integer> left = new ArrayList<>(), right = new ArrayList<>();
            for (int i : indices) {
                if (S[i] <= orderedAlphabet[mid]) {
                    left.add(i);
                } else {
                    right.add(i);
                }
                node.freq.add(right.size());
            }
            node.lc = build(left, lo, mid);
            node.rc = build(right, mid + 1, hi);
            return node;
        }

        /**
         * query the kth smallest element in {@link S} from i to j
         *
         * @param root root of WT
         * @param i    start index (include)
         * @param j    end index (include)
         * @param k    the kth smallest
         * @return the node of that element
         */
        private Node quantile(Node root, int i, int j, int k) {
            if (root.lo == root.hi) {
                return root;
            }
            if (k <= countMapToLeft(root, i, j)) {
                return quantile(root.lc, mapLeft(root, i), mapLeft(root, j), k);
            } else {
                return quantile(root.rc, 0, mapRight(root, j), k - root.getFreq(j));
            }
        }

        /**
         * the number of {@link S} from i to j that mapped to left child
         *
         * @param root root of WT
         * @param i    start index (include)
         * @param j    end index (include)
         * @return number >= 0
         */
        private int countMapToLeft(Node root, int i, int j) {
            return j + 1 - root.getFreq(j) - (i - root.getFreq(i - 1));
        }

        /**
         * the index of left child WT that mapped from index i
         *
         * @param root root of WT
         * @param i    current index i
         * @return left child WT index
         */
        private int mapLeft(Node root, int i) {
            return Math.max(i - root.getFreq(i), 0);
        }

        /**
         * the index of right child WT that mapped from index i
         *
         * @param root root of WT
         * @param i    current index i
         * @return right child WT index
         */
        private int mapRight(Node root, int i) {
            return Math.max(root.getFreq(i) - 1, 0);
        }

        public int query(int left, int right, int threshold) {
            Node node = quantile(root, left, right, threshold);
            List<Integer> indices = v2indices.get(this.orderedAlphabet[node.lo]);
            if (indices.size() >= threshold) {
                int low = Collections.binarySearch(indices, left);
                if (low < 0) {
                    low = ~low;
                }
                int hi = Collections.binarySearch(indices, right);
                if (hi < 0) {
                    hi = ~hi - 1;
                }
                if (hi - low + 1 >= threshold) {
                    return orderedAlphabet[node.lo];
                }
            }
            return -1;
        }

        private class Node {
            /**
             * lo start index of {@link orderedAlphabet} (include)
             * hi end index of {@link orderedAlphabet} (include), e.g. orderedAlphabet[lo,...,hi]
             */
            public int lo, hi;
            /**
             * the number of elements that mapped to right child WT each from {@link lo} to {@link hi}
             */
            public List<Integer> freq;
            public Node lc, rc;

            public Node(int lo, int hi) {
                this.lo = lo;
                this.hi = hi;
                this.freq = new ArrayList<>();
                this.freq.add(0);
                this.lc = this.rc = null;
            }

            public int getFreq(int i) {
                return this.freq.get(i + 1);
            }
        }
    }
}
```

# 参考
[Wavelet Trees for Competitive Programming Robinson CASTRO, Nico LEHMANN, Jorge PÉREZ, Bernardo SUBERCASEAUX](https://ioinformatics.org/journal/v10_2016_19_37.pdf)