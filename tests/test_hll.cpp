#include <cmath>
#include <cstdio>
#include <cstdlib>
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
  // TODO(slide 10): replace with the exact example from the seminar slides.
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

int main() {
  test_register_update();
  test_tiny_counts();
  test_merge();
  test_generator();
  test_accuracy_sanity();
  std::printf("\n%s (%d failures)\n", failures ? "TESTS FAILED" : "ALL TESTS PASSED", failures);
  return failures ? 1 : 0;
}
