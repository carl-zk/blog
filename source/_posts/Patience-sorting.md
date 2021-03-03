---
title: Patience sorting
date: 2021-03-02 21:46:15
category:
    - 数据结构
tags:
---
原来叫 Patience 是因为这个排序像一个扑克牌游戏，游戏名叫“Patience”，现在流行叫“Solitaire”。可以在电脑上玩玩先。
Patience sorting 最适合解决 Longest Increasing Subsequence (LIS) 问题。
例如 arr = [1,3,3,8,6,7].
![](/blog/2021/03/02/Patience-sorting/1.svg)
长度为4。
如何计算长度为4的 LIS 的个数呢？
![](/blog/2021/03/02/Patience-sorting/2.svg)
i = 0, arr[i] = 1 : len = 1, count(0) = 1. (即count(i))
i = 1, arr[i] = 3 : len = 2, count(1) = 1 (len=1 and arr[k] < arr[i] 的所有count(k) 之和).
len = 2, count(2) = 1.
len = 3, count(3) = count(1) + count(2) = 1 + 1 = 2.
len = 3, count(4) = count(1) + count(2) = 1 + 1 = 2.
len = 4, count(5) = count(4) = 2.

```java
public int findNumberOfLIS(int[] nums) {
        if (nums.length == 0) {
            return 0;
        }
        int n = nums.length;
        int[] count = new int[n];
        count[0] = 1;
        List<List<Integer>> piles = new ArrayList<>();
        piles.add(listOf(0));
        for (int i = 1; i < n; i++) {
            int j = search(piles, nums[i], nums);
            if (j == piles.size()) {
                piles.add(listOf(i));
                count[i] = countOfLess(piles.get(j - 1), nums[i], nums, count);
            } else {
                count[i] = count[lastOf(piles.get(j))] + (j > 0 ? countOfLess(piles.get(j - 1), nums[i], nums, count) : 1);
                piles.get(j).add(i);
            }
        }
        return count[lastOf(piles.get(piles.size() - 1))];
    }

    List<Integer> listOf(int x) {
        List<Integer> list = new ArrayList<>();
        list.add(x);
        return list;
    }

    int search(List<List<Integer>> piles, int x, int[] nums) {
        int l = 0, r = piles.size() - 1;
        if (nums[lastOf(piles.get(r))] < x) {
            return r + 1;
        }
        while (l < r) {
            int mid = l + (r - l) / 2;
            if (nums[lastOf(piles.get(mid))] < x) {
                l = mid + 1;
            } else {
                r = mid;
            }
        }
        return r;
    }

    int lastOf(List<Integer> pile) {
        return pile.get(pile.size() - 1);
    }

    int countOfLess(List<Integer> pile, int x, int[] nums, int[] count) {
        int l = 0, r = pile.size() - 1;
        if (nums[pile.get(l)] < x) {
            return count[pile.get(r)];
        }
        while (l < r) {
            int mid = l + (r - l) / 2;
            if (nums[pile.get(mid)] >= x) {
                l = mid + 1;
            } else {
                r = mid;
            }
        }
        return count[lastOf(pile)] - (r > 0 ? count[pile.get(r - 1)] : 0);
    }
```
# Reference 
https://leetcode.com/problems/number-of-longest-increasing-subsequence/discuss/916196/Python-Short-O(n-log-n)-solution-beats-100-explained