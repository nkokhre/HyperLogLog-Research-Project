// Experiment 3: time per inserted item and memory, HLL vs exact hash set.
// Usage: exp3 <reps> > out.csv
// Method: keys (all inserts, incl. repeats) are built BEFORE timing; one
// warm-up run; `reps` timed runs; every result goes into a sink so the
// compiler cannot drop the work. Timing = update only; the estimate step is
// timed separately (est_ns) to check "LC does not slow things down".
// Hash-set memory is the exact number of bytes requested from the allocator
// (counting allocator), not an estimate.
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <unordered_set>
#include <vector>

#include "../src/gen.hpp"
#include "../src/hll.hpp"

static size_t g_bytes = 0;  // live bytes held by CountingAlloc
template <class T>
struct CountingAlloc {
  using value_type = T;
  CountingAlloc() = default;
  template <class U> CountingAlloc(const CountingAlloc<U>&) {}
  T* allocate(size_t n) { g_bytes += n * sizeof(T); return std::allocator<T>().allocate(n); }
  void deallocate(T* p, size_t n) { g_bytes -= n * sizeof(T); std::allocator<T>().deallocate(p, n); }
  template <class U> bool operator==(const CountingAlloc<U>&) const { return true; }
  template <class U> bool operator!=(const CountingAlloc<U>&) const { return false; }
};
using CountedSet = std::unordered_set<uint64_t, std::hash<uint64_t>, std::equal_to<uint64_t>,
                                      CountingAlloc<uint64_t>>;

using Clock = std::chrono::steady_clock;
static volatile double g_sink = 0;  // result sink

struct Timing { double med, q1, q3; };

// Each sample repeats the run `inner` times so that every sample lasts a few
// ms even for small n (otherwise timer/frequency noise dominates).
template <class F>
static Timing time_ns_per_item(const std::vector<uint64_t>& keys, int reps, F&& run) {
  const int inner = int(std::max<size_t>(1, 3000000 / keys.size()));
  for (int i = 0; i < 3; ++i) run(keys);  // warm-up
  std::vector<double> t;
  for (int r = 0; r < reps; ++r) {
    auto a = Clock::now();
    for (int i = 0; i < inner; ++i) run(keys);
    auto b = Clock::now();
    t.push_back(std::chrono::duration<double, std::nano>(b - a).count() / (double(keys.size()) * inner));
  }
  std::sort(t.begin(), t.end());
  return {t[t.size() / 2], t[t.size() / 4], t[(3 * t.size()) / 4]};
}

int main(int argc, char** argv) {
  const int reps = argc > 1 ? std::atoi(argv[1]) : 21;
  const int p = 14;
  std::printf("n,stream_len,hll_basic_ns,hll_basic_q1,hll_basic_q3,hll_lc_ns,hll_lc_q1,hll_lc_q3,set_ns,set_q1,set_q3,est_basic_ns,est_lc_ns,"
              "hll_bytes_stored,hll_bytes_packed6,set_bytes,set_distinct\n");
  for (uint64_t n : {1000ULL, 10000ULL, 100000ULL, 1000000ULL, 10000000ULL}) {
    std::vector<uint64_t> keys;
    keys.reserve(n * 3 / 2);
    IdStream s(1);
    for (uint64_t k = 0; k < n; ++k) s.emit(k, [&](uint64_t id) { keys.push_back(id); });

    // Update cost is identical for basic and LC (same add()); we time both
    // variants as separate sketch objects to show that explicitly.
    auto run_hll = [&](const std::vector<uint64_t>& ks) {
      HyperLogLog h(p);
      for (uint64_t k : ks) h.add(k, 1);
      g_sink = g_sink + h.registers()[0] + h.registers()[h.m() / 2];
    };
    auto run_hll_lc = [&](const std::vector<uint64_t>& ks) {
      HyperLogLog h(p);
      for (uint64_t k : ks) h.add(k, 1);
      g_sink = g_sink + h.estimate_lc();  // final step differs only here
    };
    auto run_set = [&](const std::vector<uint64_t>& ks) {
      std::unordered_set<uint64_t> st;
      for (uint64_t k : ks) st.insert(k);
      g_sink = g_sink + st.size();
    };
    const Timing t_basic = time_ns_per_item(keys, reps, run_hll);
    const Timing t_lc = time_ns_per_item(keys, reps, run_hll_lc);
    const Timing t_set = time_ns_per_item(keys, reps, run_set);

    // estimate step cost (per call, ns)
    HyperLogLog h(p);
    for (uint64_t k : keys) h.add(k, 1);
    auto est_time = [&](bool lc) {
      std::vector<double> t;
      for (int r = 0; r < 101; ++r) {
        auto a = Clock::now();
        g_sink = g_sink + (lc ? h.estimate_lc() : h.estimate_basic());
        auto b = Clock::now();
        t.push_back(std::chrono::duration<double, std::nano>(b - a).count());
      }
      std::sort(t.begin(), t.end());
      return t[t.size() / 2];
    };
    const double e_b = est_time(false), e_l = est_time(true);

    g_bytes = 0;
    size_t distinct;
    size_t set_bytes;
    {
      CountedSet st;
      for (uint64_t k : keys) st.insert(k);
      distinct = st.size();
      set_bytes = g_bytes;  // buckets + nodes, exactly as requested
    }
    std::printf("%llu,%zu,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.0f,%.0f,%zu,%zu,%zu,%zu\n",
                (unsigned long long)n, keys.size(), t_basic.med, t_basic.q1, t_basic.q3, t_lc.med, t_lc.q1, t_lc.q3, t_set.med, t_set.q1, t_set.q3, e_b, e_l,
                h.bytes_stored(), h.bytes_packed_6bit(), set_bytes, distinct);
    std::fflush(stdout);
  }
}
