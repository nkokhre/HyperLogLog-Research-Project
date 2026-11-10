#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>
#include <unordered_set>

#include "../src/gen.hpp"
#include "../src/hll.hpp"

static int failures = 0;
#define CHECK(cond, msg)                                         \
  do {                                                           \
    if (!(cond)) {                                               \
      std::printf("  FAIL: %s  [%s]\n", msg, #cond);             \
      ++failures;                                                \
    } else {                                                     \
      std::printf("  ok:   %s\n", msg);                          \
    }                                                            \
  } while (0)

// Build a hash from (register index, number of leading zeros after it).
static uint64_t make_hash(int p, uint32_t idx, int zeros) {
  uint64_t h = uint64_t(idx) << (64 - p);
  if (zeros < 64 - p) h |= 1ULL << (64 - p - 1 - zeros);
  return h;
}

static void test_register_update() {
  std::puts("register update (hand-made hashes, p=4)");
  HyperLogLog h(4);
  h.add_hash(make_hash(4, 3, 0));  // first bit after index is 1 -> rho 1
  CHECK(h.registers()[3] == 1, "rho=1 when next bit is 1");
  h.add_hash(make_hash(4, 3, 5));  // 5 zeros then 1 -> rho 6
  CHECK(h.registers()[3] == 6, "rho=6 after 5 leading zeros");
  h.add_hash(make_hash(4, 3, 2));  // smaller rho must not lower the register
  CHECK(h.registers()[3] == 6, "register keeps the maximum");
  h.add_hash(make_hash(4, 15, 60));  // all remaining 60 bits zero
  CHECK(h.registers()[15] == 61, "all-zero remainder gives rho = 64-p+1");
  CHECK(h.empty_registers() == 14, "other 14 registers still empty");
}

// Worked example (hand-computed, p=4, m=16, alpha=0.673). Stands in for the
// seminar's slide-10 example, whose numbers we do not have; same method:
// register values -> harmonic mean -> estimate -> linear counting.
static void test_worked_example() {
  std::puts("worked example (p=4, hand-computed)");
  const int rho[16] = {1, 1, 2, 1, 3, 1, 1, 2, 1, 1, 1, 2, 1, 4, 0, 0};
  HyperLogLog h(4);
  for (int i = 0; i < 16; ++i)
    if (rho[i] > 0) h.add_hash(make_hash(4, i, rho[i] - 1));
  // sum 2^-M = 9*(1/2) + 3*(1/4) + 1/8 + 1/16 + 2*1 = 7.4375
  // E = 0.673 * 16^2 / 7.4375 = 23.1648
  CHECK(h.empty_registers() == 2, "2 registers empty");
  CHECK(std::fabs(h.estimate_basic() - 23.1648) < 1e-3, "basic estimate = 23.1648");
  // E <= 2.5*16 = 40 and V = 2 > 0 -> linear counting: 16 * ln(16/2) = 33.2711
  CHECK(std::fabs(h.estimate_lc() - 33.2711) < 1e-3, "linear counting = 16 ln 8 = 33.2711");
}

static void test_tiny_counts() {
  std::puts("counts 0, 1, 2");
  const int p = 14;
  HyperLogLog h(p);
  const double m = h.m();
  CHECK(h.estimate_lc() == 0.0, "0 items: linear counting gives exactly 0");
  const double b0 = h.estimate_basic();
  std::printf("        (basic estimate for 0 items = %.1f = alpha*m, "
              "not 0)\n", b0);
  CHECK(std::fabs(b0 / m - 0.7213 / (1 + 1.079 / m)) < 1e-9,
        "0 items: basic gives alpha*m (the known small-count flaw)");
  h.add(42);
  CHECK(std::fabs(h.estimate_lc() - 1.0) < 1e-3, "1 item: LC ~ 1");
  for (int i = 0; i < 1000; ++i) h.add(42);
  CHECK(std::fabs(h.estimate_lc() - 1.0) < 1e-3, "repeating an item changes nothing");
  h.add(43);
  CHECK(std::fabs(h.estimate_lc() - 2.0) < 1e-2, "2 items: LC ~ 2");
}

static void test_merge() {
  std::puts("merge equals one sketch over everything");
  for (int p : {4, 10, 14}) {
    HyperLogLog a(p), b(p), all(p);
    for (uint64_t k = 0; k < 50000; ++k) {
      const uint64_t id = splitmix_mix(k);
      all.add(id, 7);
      if (k % 3 == 0 || k % 5 == 0) a.add(id, 7);  // overlapping parts
      if (k % 3 != 0) b.add(id, 7);
    }
    a.merge(b);
    char msg[64];
    std::snprintf(msg, sizeof msg, "p=%d: registers identical after merge", p);
    CHECK(a.registers() == all.registers(), msg);
  }
}

static void test_generator() {
  std::puts("generator: true distinct count matches a real hash set");
  IdStream s(123);
  std::unordered_set<uint64_t> set;
  uint64_t len = 0;
  for (uint64_t k = 0; k < 200000; ++k)
    s.emit(k, [&](uint64_t id) { set.insert(id); ++len; });
  CHECK(set.size() == 200000, "distinct count == number of new IDs");
  CHECK(len > 200000, "stream contains repeats");
}

static void test_accuracy_sanity() {
  std::puts("accuracy sanity (single seed, loose bounds)");
  const int p = 14;
  {  // n = 1,000: basic should be ~12x too big, LC close
    HyperLogLog h(p);
    IdStream s(1);
    for (uint64_t k = 0; k < 1000; ++k) s.emit(k, [&](uint64_t id) { h.add(id, 1); });
    const double b = h.estimate_basic(), l = h.estimate_lc();
    std::printf("        n=1000: basic=%.0f (x%.1f), LC=%.1f (err %.2f%%)\n", b,
                b / 1000, l, 100 * (l - 1000) / 1000);
    CHECK(b / 1000 > 8 && b / 1000 < 16, "basic is roughly 12x too big");
    CHECK(std::fabs(l - 1000) / 1000 < 0.05, "LC within 5%");
  }
  {  // n = 10^6: within 5 sigma of 1.04/sqrt(m)
    HyperLogLog h(p);
    IdStream s(2);
    for (uint64_t k = 0; k < 1000000; ++k) s.emit(k, [&](uint64_t id) { h.add(id, 2); });
    const double e = h.estimate_lc();
    const double rel = (e - 1e6) / 1e6;
    std::printf("        n=1e6: est=%.0f rel err %.3f%% (theory sigma %.3f%%)\n",
                e, 100 * rel, 100 * h.theory_std_error());
    CHECK(std::fabs(rel) < 5 * h.theory_std_error(), "n=10^6 within 5 sigma");
  }
}


static bool throws_invalid(int p) {
  try { HyperLogLog h(p); return false; } catch (const std::invalid_argument&) { return true; }
}

static void test_construction_and_helpers() {
  std::puts("construction, constants, memory helpers");
  CHECK(throws_invalid(3) && throws_invalid(19), "p outside [4,18] is rejected");
  CHECK(!throws_invalid(4) && !throws_invalid(18), "p = 4 and p = 18 are accepted");
  HyperLogLog a(4), b(5);
  bool threw = false;
  try { a.merge(b); } catch (const std::invalid_argument&) { threw = true; }
  CHECK(threw, "merging sketches with different p is rejected");
  // empty sketch: basic estimate = alpha * m for the three special alphas
  CHECK(std::fabs(HyperLogLog(4).estimate_basic() - 0.673 * 16) < 1e-9, "alpha(16) = 0.673");
  CHECK(std::fabs(HyperLogLog(5).estimate_basic() - 0.697 * 32) < 1e-9, "alpha(32) = 0.697");
  CHECK(std::fabs(HyperLogLog(6).estimate_basic() - 0.709 * 64) < 1e-9, "alpha(64) = 0.709");
  HyperLogLog h(14);
  CHECK(h.p() == 14 && h.m() == 16384, "p=14 gives m=16384");
  CHECK(h.bytes_stored() == 16384, "stored: 1 byte per register (16 KB)");
  CHECK(h.bytes_packed_6bit() == 12288, "packed 6-bit: 12 KB");
  CHECK(HyperLogLog(4).bytes_packed_6bit() == 12, "p=4 packed 6-bit: 12 bytes");
  CHECK(std::fabs(h.theory_std_error() - 0.008125) < 1e-9, "theory error at p=14 is 0.8125%");
  CHECK(h.empty_fraction() == 1.0, "new sketch: all registers empty");
}

static void test_register_index_extremes() {
  std::puts("register index extremes (p=4)");
  HyperLogLog h(4);
  h.add_hash(make_hash(4, 0, 0));
  h.add_hash(make_hash(4, 15, 3));
  CHECK(h.registers()[0] == 1, "index 0 is used");
  CHECK(h.registers()[15] == 4, "index m-1 is used");
  CHECK(h.empty_registers() == 14, "nothing else touched");
  CHECK(std::fabs(h.empty_fraction() - 14.0 / 16) < 1e-12, "empty fraction = 14/16");
}

static void test_lc_switch_rules() {
  std::puts("linear-counting switch rules (p=4, m=16)");
  {  // no empty register: LC must NOT be used even if raw <= 2.5m
    HyperLogLog h(4);
    for (int i = 0; i < 16; ++i) h.add_hash(make_hash(4, i, 0));  // all registers = 1
    CHECK(h.empty_registers() == 0, "all registers filled");
    CHECK(h.estimate_basic() <= 2.5 * 16, "raw estimate is below 2.5m");
    CHECK(h.estimate_lc() == h.estimate_basic(), "no empty register -> basic formula is kept");
  }
  {  // raw above 2.5m: LC must NOT be used even though some registers are empty
    HyperLogLog h(4);
    for (int i = 0; i < 15; ++i) h.add_hash(make_hash(4, i, 5));  // 15 registers = 6, one empty
    CHECK(h.empty_registers() == 1, "one register empty");
    CHECK(h.estimate_basic() > 2.5 * 16, "raw estimate is above 2.5m");
    CHECK(h.estimate_lc() == h.estimate_basic(), "raw > 2.5m -> basic formula is kept");
  }
}

static void test_determinism_and_order() {
  std::puts("determinism, seeds, order and duplicates");
  HyperLogLog a(10), b(10), c(10), d(10);
  const uint64_t N = 20000;
  for (uint64_t k = 0; k < N; ++k) a.add(splitmix_mix(k), 5);
  for (uint64_t k = N; k-- > 0;) b.add(splitmix_mix(k), 5);       // reverse order
  for (uint64_t k = 0; k < N; ++k) { c.add(splitmix_mix(k), 5); c.add(splitmix_mix(k), 5); }  // duplicates
  for (uint64_t k = 0; k < N; ++k) d.add(splitmix_mix(k), 6);     // other hash seed
  CHECK(a.registers() == b.registers(), "insertion order does not matter");
  CHECK(a.registers() == c.registers(), "duplicates change nothing");
  CHECK(a.registers() != d.registers(), "a different hash seed gives different registers");
  HyperLogLog e = a; e.merge(a);
  CHECK(e.registers() == a.registers(), "merging a sketch with itself changes nothing");
  HyperLogLog f(10), g(10);
  for (uint64_t k = 0; k < 500; ++k) f.add(splitmix_mix(k), 5);
  for (uint64_t k = 300; k < 900; ++k) g.add(splitmix_mix(k), 5);
  HyperLogLog fg = f; fg.merge(g);
  HyperLogLog gf = g; gf.merge(f);
  CHECK(fg.registers() == gf.registers(), "merge is commutative");
}

static void test_handover_bias_is_real() {
  std::puts("hand-over region: basic HLL is biased upward near n = 2.5m (p=12)");
  const int p = 12;
  const double m = 1 << p;
  const uint64_t n = uint64_t(2.5 * m);
  double sum_rel = 0;
  const int seeds = 40;
  for (int sd = 1; sd <= seeds; ++sd) {
    HyperLogLog h(p);
    IdStream s(sd);
    for (uint64_t k = 0; k < n; ++k) s.emit(k, [&](uint64_t id) { h.add(id, sd); });
    sum_rel += (h.estimate_basic() - double(n)) / double(n);
  }
  const double mean = sum_rel / seeds;
  std::printf("        mean basic error at n=2.5m: %+.2f%%\n", 100 * mean);
  CHECK(mean > 0.005 && mean < 0.06, "mean basic error is positive (between 0.5% and 6%)");
}

int main() {
  test_register_update();
  test_construction_and_helpers();
  test_register_index_extremes();
  test_lc_switch_rules();
  test_determinism_and_order();
  test_worked_example();
  test_tiny_counts();
  test_merge();
  test_generator();
  test_accuracy_sanity();
  test_handover_bias_is_real();
  std::printf("\n%s (%d failures)\n", failures ? "TESTS FAILED" : "ALL TESTS PASSED", failures);
  return failures ? 1 : 0;
}
