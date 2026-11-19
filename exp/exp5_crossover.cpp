// Experiment 5 (MAIN): where does plain HLL become better than linear counting?
// Usage: exp5_crossover <seeds> <p1,p2,...> > out.csv
//
// Per (p, seed) ONE stream feeds ONE sketch; at every grid point n = t*m we
// record the raw HLL estimate and the number of empty registers V. All other
// estimators (pure LC, textbook rule, any switch rule) are pure functions of
// (raw estimate, V, m), so every method sees identical sketches. Analysis is
// done by exp/analyze_exp5.py from this raw file.
//   columns: p, seed, n, t (= n/m), est_raw, empty
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <set>
#include <sstream>
#include <string>
#include <vector>

#include "../src/gen.hpp"
#include "../src/hll.hpp"

// Grid of items-per-register t = n/m (fine around the expected crossover).
static std::vector<double> t_grid() {
  std::set<long> g;  // in units of 1/1000
  for (int i = 250; i <= 1500; i += 125) g.insert(i);   // 0.25 .. 1.5, step 0.125
  for (int i = 1500; i <= 5000; i += 50) g.insert(i);   // 1.5 .. 5.0, step 0.05
  for (int i = 5000; i <= 8000; i += 250) g.insert(i);  // 5.0 .. 8.0, step 0.25
  std::vector<double> t;
  for (long v : g) t.push_back(v / 1000.0);
  return t;
}

int main(int argc, char** argv) {
  const int seeds = argc > 1 ? std::atoi(argv[1]) : 300;
  std::string plist = argc > 2 ? argv[2] : "8,10,12,14,16";
  std::vector<int> ps;
  { std::stringstream ss(plist); std::string tok; while (std::getline(ss, tok, ',')) ps.push_back(std::atoi(tok.c_str())); }
  const std::vector<double> grid = t_grid();

  std::printf("p,seed,n,t,est_raw,empty\n");
  for (int p : ps) {
    const uint64_t m = 1ULL << p;
    std::vector<uint64_t> cps;  // checkpoints n (distinct count)
    for (double t : grid) cps.push_back(std::llround(t * double(m)));
    for (int seed = 1; seed <= seeds; ++seed) {
      HyperLogLog h(p);
      IdStream s(seed);
      size_t ci = 0;
      for (uint64_t k = 0; ci < cps.size(); ++k) {
        s.emit(k, [&](uint64_t id) { h.add(id, seed); });
        if (k + 1 == cps[ci]) {
          std::printf("%d,%d,%llu,%.4f,%.4f,%u\n", p, seed, (unsigned long long)cps[ci],
                      double(cps[ci]) / double(m), h.estimate_basic(), h.empty_registers());
          ++ci;
        }
      }
    }
  }
}
