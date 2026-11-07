// Experiment 1: relative error vs true count n (basic vs linear counting).
// Usage: exp1 <p> <seeds> <max_n> > out.csv
//
// For each seed ONE stream is fed to ONE sketch, and we snapshot at the
// checkpoints n. (Linear counting only changes the last step, so the same
// registers give both estimates -> both versions see identical input.)
// Note: snapshots of one seed share a stream, so points at different n for
// the same seed are correlated; different seeds are independent.
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <set>
#include <vector>

#include "../src/gen.hpp"
#include "../src/hll.hpp"

int main(int argc, char** argv) {
  const int p = argc > 1 ? std::atoi(argv[1]) : 14;
  const int seeds = argc > 2 ? std::atoi(argv[2]) : 20;
  const uint64_t max_n = argc > 3 ? std::strtoull(argv[3], nullptr, 10) : 10000000ULL;

  // log grid (8 points/decade) + dense grid around the 2.5m hand-over
  std::set<uint64_t> grid;
  for (int j = 8; j <= 56; ++j) grid.insert(std::llround(std::pow(10.0, j / 8.0)));
  const uint64_t m = 1ULL << p;
  for (double f = 0.5; f <= 3.01; f += 0.125) grid.insert(std::llround(f * 2.5 * m / 1.0));
  std::vector<uint64_t> cps;
  for (uint64_t n : grid) if (n >= 10 && n <= max_n) cps.push_back(n);

  std::printf("p,m,seed,n,est_basic,est_lc,empty_frac\n");
  for (int seed = 1; seed <= seeds; ++seed) {
    HyperLogLog h(p);
    IdStream s(seed);
    size_t ci = 0;
    for (uint64_t k = 0; ci < cps.size(); ++k) {
      s.emit(k, [&](uint64_t id) { h.add(id, seed); });
      if (k + 1 == cps[ci]) {
        std::printf("%d,%u,%d,%llu,%.6f,%.6f,%.6f\n", p, h.m(), seed,
                    (unsigned long long)cps[ci], h.estimate_basic(),
                    h.estimate_lc(), h.empty_fraction());
        ++ci;
      }
    }
  }
}
