# -*- coding: utf-8 -*-

import math
import mmh3
from bitarray import bitarray


class BloomFilter(object):
    def __init__(self, capacity, error_rate=1e-6, fp=None):
        self.size = math.ceil(-capacity * math.log(error_rate) / math.log(2) ** 2)
        self.num_hashes = round(self.size * math.log(2) / capacity)

        if fp:
            self.array = bitarray()
            self.array.fromfile(fp)
        else:
            self.array = bitarray(self.size)
            self.array.setall(False)

    def save(self, fp):
        if fp:
            self.array.tofile(fp)

    def add(self, item):
        for i in range(self.num_hashes):
            self.array[mmh3.hash(item, i) % self.size] = True

    def __contains__(self, item):
        for i in range(self.num_hashes):
            if not self.array[mmh3.hash(item, i) % self.size]:
                return False
        return True


def main():
    pass


if __name__ == "__main__":
    main()
