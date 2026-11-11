#ifndef IMPROVED_STRIDE_H
#define IMPROVED_STRIDE_H
#include "cache.h"
#include <map>

struct tracker_entry {
    uint64_t last_addr = 0;
    int64_t last_stride = 0;
    uint32_t confidence = 0;
    uint32_t degree = 1;
    uint32_t useful_pfs = 0;
    uint32_t total_pfs = 0;
};

class improved_stride {
public:
    CACHE* intern_;
    std::map<uint64_t, tracker_entry> fdp_stride_table;
    const uint32_t MAX_DEGREE = 4;
    const uint32_t CONFIDENCE_THRESHOLD = 2;

    improved_stride(CACHE* cache) : intern_(cache) {}
    void bind(CACHE* cache) { intern_ = cache; } 

    void prefetcher_initialize();
    uint32_t prefetcher_cache_operate(champsim::address addr, champsim::address ip, uint8_t cache_hit, bool useful_prefetch, access_type type, uint32_t metadata_in);
    uint32_t prefetcher_cache_fill(champsim::address addr, long set, long way, uint8_t prefetch, champsim::address evicted_addr, uint32_t metadata_in);
    void prefetcher_cycle_operate();
    void prefetcher_final_stats();
};
#endif
