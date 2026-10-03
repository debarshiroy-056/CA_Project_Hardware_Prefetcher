#include "no.h"
#include "cache.h"
#include <fstream>

namespace {
std::ofstream dump_file;
uint64_t l2_seen = 0;
uint64_t access_order = 0;
const uint64_t WARMUP_SKIP = 10000;
const uint64_t MAX_SAMPLES = 50000;
}

uint32_t no::prefetcher_cache_operate(champsim::address addr, champsim::address ip, uint8_t cache_hit, bool useful_prefetch, access_type type,
                                      uint32_t metadata_in)
{
  if (intern_->NAME.find("L2C") != std::string::npos && type == access_type::LOAD && ip.to<uint64_t>() != 0) {
    l2_seen++;
    if (l2_seen > WARMUP_SKIP && access_order < MAX_SAMPLES) {
      if (!dump_file.is_open()) {
        dump_file.open("l2_demand_sample.csv");
        dump_file << "AccessOrder,LoadPC,CacheLineAddr,Hit\n";
      }
      access_order++;
      uint64_t cl_addr = addr.to<uint64_t>() >> 6;
      dump_file << access_order << ",0x" << std::hex << ip.to<uint64_t>() << ",0x" << cl_addr << std::dec << "," << (int)cache_hit << "\n";
      if (access_order == MAX_SAMPLES) {
        dump_file.close();
      }
    }
  }
  return metadata_in;
}

uint32_t no::prefetcher_cache_fill(champsim::address addr, long set, long way, uint8_t prefetch, champsim::address evicted_addr, uint32_t metadata_in)
{
  return metadata_in;
}
