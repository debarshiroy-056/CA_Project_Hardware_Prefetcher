#ifndef BERTI_H
#define BERTI_H
#include "cache.h"
#include <map>

struct berti_history {
    uint64_t last_addr = 0;
    uint64_t last_cycle = 0;
    std::map<int64_t, uint32_t> delta_confidence;
    int64_t best_timely_delta = 0;
};

class berti {
public:
    CACHE* intern_;
    std::map<uint64_t, berti_history> berti_table;
    const uint32_t CONFIDENCE_THRESHOLD = 2;
    const uint64_t TARGET_LATENCY = 150;

    berti(CACHE* cache) : intern_(cache) {}
    void bind(CACHE* cache) { intern_ = cache; }

    void prefetcher_initialize();
    uint32_t prefetcher_cache_operate(champsim::address addr, champsim::address ip, uint8_t cache_hit, bool useful_prefetch, access_type type, uint32_t metadata_in);
    uint32_t prefetcher_cache_fill(champsim::address addr, long set, long way, uint8_t prefetch, champsim::address evicted_addr, uint32_t metadata_in);
    void prefetcher_cycle_operate();
    void prefetcher_final_stats();
};
#endif
