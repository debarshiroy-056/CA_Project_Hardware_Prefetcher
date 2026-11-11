#include "berti.h"
#include <iostream>

void berti::prefetcher_initialize() {
    std::cout << "L2 Berti (Timeliness-Aware) Prefetcher Initialized" << std::endl;
}

uint32_t berti::prefetcher_cache_operate(champsim::address addr, champsim::address ip, uint8_t cache_hit, bool useful_prefetch, access_type type, uint32_t metadata_in) {
    // FIXED: Added () to current_cycle
    uint64_t current_cycle = intern_->current_cycle(); 
    uint64_t ip_val = ip.to<uint64_t>();
    uint64_t addr_val = addr.to<uint64_t>();
    
    if (berti_table.find(ip_val) != berti_table.end()) {
        int64_t delta = addr_val - berti_table[ip_val].last_addr;
        uint64_t latency = current_cycle - berti_table[ip_val].last_cycle;

        if (delta != 0) {
            berti_table[ip_val].delta_confidence[delta]++;
            if (latency > (TARGET_LATENCY / 2) && latency < (TARGET_LATENCY * 2)) {
                berti_table[ip_val].delta_confidence[delta] += 2;
                berti_table[ip_val].best_timely_delta = delta;
            }
        }

        int64_t prefetch_delta = berti_table[ip_val].best_timely_delta != 0 ? berti_table[ip_val].best_timely_delta : delta;

        if (berti_table[ip_val].delta_confidence[prefetch_delta] >= CONFIDENCE_THRESHOLD) {
            uint64_t pf_addr_val = addr_val + prefetch_delta;
            if ((pf_addr_val >> 12) == (addr_val >> 12)) {
                champsim::address pf_addr{pf_addr_val};
                intern_->prefetch_line(pf_addr, true, 0);
            }
        }
    }
    berti_table[ip_val].last_addr = addr_val;
    berti_table[ip_val].last_cycle = current_cycle;
    return metadata_in;
}

uint32_t berti::prefetcher_cache_fill(champsim::address addr, long set, long way, uint8_t prefetch, champsim::address evicted_addr, uint32_t metadata_in) {
    return metadata_in;
}
void berti::prefetcher_cycle_operate() {}
void berti::prefetcher_final_stats() {}
