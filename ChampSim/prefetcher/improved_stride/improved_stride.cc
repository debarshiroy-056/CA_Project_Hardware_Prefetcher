#include "improved_stride.h"
#include <iostream>

void improved_stride::prefetcher_initialize() {
    std::cout << "L2 FDP-Stride (Improved) Prefetcher Initialized" << std::endl;
}

uint32_t improved_stride::prefetcher_cache_operate(champsim::address addr, champsim::address ip, uint8_t cache_hit, bool useful_prefetch, access_type type, uint32_t metadata_in) {
    uint64_t ip_val = ip.to<uint64_t>();
    uint64_t addr_val = addr.to<uint64_t>();

    if (useful_prefetch && fdp_stride_table.find(ip_val) != fdp_stride_table.end()) {
        fdp_stride_table[ip_val].useful_pfs++;
        if (fdp_stride_table[ip_val].total_pfs > 10) {
            double accuracy = (double)fdp_stride_table[ip_val].useful_pfs / fdp_stride_table[ip_val].total_pfs;
            if (accuracy > 0.75 && fdp_stride_table[ip_val].degree < MAX_DEGREE) {
                fdp_stride_table[ip_val].degree++;
            } else if (accuracy < 0.30 && fdp_stride_table[ip_val].degree > 0) {
                fdp_stride_table[ip_val].degree--;
            }
            fdp_stride_table[ip_val].useful_pfs = 0;
            fdp_stride_table[ip_val].total_pfs = 0;
        }
    }

    int64_t current_stride = addr_val - fdp_stride_table[ip_val].last_addr;
    if (current_stride == fdp_stride_table[ip_val].last_stride && current_stride != 0) {
        fdp_stride_table[ip_val].confidence++;
    } else {
        fdp_stride_table[ip_val].confidence = 0;
        fdp_stride_table[ip_val].last_stride = current_stride;
    }
    fdp_stride_table[ip_val].last_addr = addr_val;

    if (fdp_stride_table[ip_val].confidence >= CONFIDENCE_THRESHOLD && fdp_stride_table[ip_val].degree > 0) {
        for (uint32_t i = 1; i <= fdp_stride_table[ip_val].degree; i++) {
            uint64_t pf_addr_val = addr_val + (current_stride * i);
            if ((pf_addr_val >> 12) != (addr_val >> 12)) break;
            champsim::address pf_addr{pf_addr_val};
            bool success = intern_->prefetch_line(pf_addr, true, 0);
            if (success) fdp_stride_table[ip_val].total_pfs++;
        }
    }
    return metadata_in;
}

uint32_t improved_stride::prefetcher_cache_fill(champsim::address addr, long set, long way, uint8_t prefetch, champsim::address evicted_addr, uint32_t metadata_in) {
    return metadata_in;
}
void improved_stride::prefetcher_cycle_operate() {}
void improved_stride::prefetcher_final_stats() {}
