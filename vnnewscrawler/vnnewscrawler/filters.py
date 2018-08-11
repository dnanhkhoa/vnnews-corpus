# -*- coding: utf-8 -*-

import os
import logging
from bloomfilter import ScalableBloomFilter, SizeGrowthRate
from scrapy.dupefilters import RFPDupeFilter


class DupeFilter(RFPDupeFilter):
    def __init__(self, checkpoint_dir=None, persistent=False, debug=False):
        self.checkpoint_dir = checkpoint_dir
        self.persistent = persistent
        self.debug = debug
        self.logdupes = True
        self.logger = logging.getLogger(__name__)
        self.filename = os.path.join(checkpoint_dir, "requests.seen")
        if self.persistent and os.path.isfile(self.filename):
            with open(self.filename, "rb") as fp:
                self.fingerprints = ScalableBloomFilter.load(fp)
        else:
            self.fingerprints = ScalableBloomFilter(
                initial_size=1000,
                initial_fp_prob=1e-7,
                size_growth_rate=SizeGrowthRate.LARGE,
                fp_prob_rate=0.9,
            )

    def close(self, reason):
        if self.persistent:
            os.makedirs(self.checkpoint_dir, exist_ok=True)
            with open(self.filename, "wb") as fp:
                self.fingerprints.save(fp)

    @classmethod
    def from_settings(cls, settings):
        return cls(
            checkpoint_dir=settings.get("CHECKPOINT_DIR", "checkpoints"),
            persistent=settings.getbool("DUPEFILTER_PERSISTENT_ENABLED"),
            debug=settings.getbool("DUPEFILTER_DEBUG"),
        )

    def request_seen(self, request):
        fp = self.request_fingerprint(request)
        if fp in self.fingerprints:
            return True
        self.fingerprints.add(fp)
