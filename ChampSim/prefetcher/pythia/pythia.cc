#include "pythia.h"
#include <iostream>

void pythia::prefetcher_initialize() {
    std::cout << "L2 Pythia (RL Q-Learning) Prefetcher Initialized" << std::endl;
}

uint32_t pythia::prefetcher_cache_operate(champsim::address addr, champsim::address ip, uint8_t cache_hit, bool useful_prefetch, access_type type, uint32_t metadata_in) {
    uint64_t ip_val = ip.to<uint64_t>();
    uint64_t addr_val = addr.to<uint64_t>();

    if (q_table.find(ip_val) == q_table.end()) {
        q_table[ip_val] = std::vector<float>(MAX_ACTIONS, 0.0f);
        last_address[ip_val] = addr_val;
        return metadata_in;
    }

    int64_t stride = addr_val - last_address[ip_val];
    last_address[ip_val] = addr_val;
    if (stride == 0) return metadata_in;

    // Apply Reward: +10 useful, 0 hit, -1 useless/polluting
    float reward = useful_prefetch ? 10.0f : (cache_hit ? 0.0f : -1.0f);
    
    int best_action = 0;
    float max_q = q_table[ip_val][0];
    for (int a = 1; a < MAX_ACTIONS; a++) {
        if (q_table[ip_val][a] > max_q) {
            max_q = q_table[ip_val][a];
            best_action = a;
        }
    }

    // Q-Learning Update
    q_table[ip_val][best_action] = q_table[ip_val][best_action] + ALPHA * (reward + GAMMA * max_q - q_table[ip_val][best_action]);

    // Take Action (Prefetch)
    for (int i = 1; i <= best_action; i++) {
        uint64_t pf_addr_val = addr_val + (stride * i);
        if ((pf_addr_val >> 12) == (addr_val >> 12)) {
            champsim::address pf_addr{pf_addr_val};
            intern_->prefetch_line(pf_addr, true, 0);
        }
    }
    return metadata_in;
}

uint32_t pythia::prefetcher_cache_fill(champsim::address addr, long set, long way, uint8_t prefetch, champsim::address evicted_addr, uint32_t metadata_in) { return metadata_in; }
void pythia::prefetcher_cycle_operate() {}
void pythia::prefetcher_final_stats() {}
