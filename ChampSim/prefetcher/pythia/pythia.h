#ifndef PYTHIA_H
#define PYTHIA_H
#include "cache.h"
#include <map>
#include <vector>

class pythia {
public:
    CACHE* intern_;
    std::map<uint64_t, std::vector<float>> q_table;
    std::map<uint64_t, uint64_t> last_address;
    
    const int MAX_ACTIONS = 4; 
    const float ALPHA = 0.1f; 
    const float GAMMA = 0.9f; 

    pythia(CACHE* cache) : intern_(cache) {}
    void bind(CACHE* cache) { intern_ = cache; }

    void prefetcher_initialize();
    uint32_t prefetcher_cache_operate(champsim::address addr, champsim::address ip, uint8_t cache_hit, bool useful_prefetch, access_type type, uint32_t metadata_in);
    uint32_t prefetcher_cache_fill(champsim::address addr, long set, long way, uint8_t prefetch, champsim::address evicted_addr, uint32_t metadata_in);
    void prefetcher_cycle_operate();
    void prefetcher_final_stats();
};
#endif
