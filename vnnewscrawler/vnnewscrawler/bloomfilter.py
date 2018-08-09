# -*- coding: utf-8 -*-

import mmh3
import math
from bitarray import bitarray


class BloomFilter(object):
    def __init__(self, capacity, error_rate=1e-6):
        self.size = math.ceil(-capacity * math.log(error_rate) / math.log(2) ** 2)
        self.num_hashes = round(self.size * math.log(2) / capacity)

    def add(self, item):
        pass

    def contains(self, item):
        pass


def main():
    bf = BloomFilter(50000000, 1e-6)
    print(bf.size, bf.num_hashes)


if __name__ == "__main__":
    main()
