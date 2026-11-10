// Experiment 2: error vs number of registers (p = 4..16) at fixed n.
// Usage: exp2 <seeds> <n> > out.csv
// Same stream per seed for every p (all versions see the same input).
#include <cstdio>
#include <cstdlib>
#include <vector>

#include "../src/gen.hpp"
#include "../src/hll.hpp"

int main(int argc, char** argv) {
  const int seeds = argc > 1 ? std::atoi(argv[1]) : 20;
  const uint64_t n = argc > 2 ? std::strtoull(argv[2], nullptr, 10) : 1000000ULL;
  std::printf("p,m,seed,n,est_basic,est_lc,empty_frac,bytes_stored,bytes_packed6\n");
  for (int seed = 1; seed <= seeds; ++seed) {
    std::vector<HyperLogLog> hs;
    for (int p = 4; p <= 16; ++p) hs.emplace_back(p);
    IdStream s(seed);
    for (uint64_t k = 0; k < n; ++k)
      s.emit(k, [&](uint64_t id) {
        const uint64_t h = hash64(id, seed);
        for (auto& x : hs) x.add_hash(h);
      });
    for (auto& h : hs)
      std::printf("%d,%u,%d,%llu,%.6f,%.6f,%.6f,%zu,%zu\n", h.p(), h.m(), seed,
                  (unsigned long long)n, h.estimate_basic(), h.estimate_lc(),
                  h.empty_fraction(), h.bytes_stored(), h.bytes_packed_6bit());
  }
}
