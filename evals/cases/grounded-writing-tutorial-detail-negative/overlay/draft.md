# Why this cache uses a linked list

The cache combines a hash map with a doubly linked list. The map locates an entry; the list records recency. A hit moves the entry to the front. When capacity is exceeded, the tail is evicted from both structures.

With capacity two and recency order A, B, reading B changes the order to B, A. Inserting C then evicts A. Both structures must be updated together so an evicted key cannot still be found in the map.
