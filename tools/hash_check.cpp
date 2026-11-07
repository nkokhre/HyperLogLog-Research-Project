// Quick uniformity check for the hash (decision rule from the proposal:
// "first library that looks uniform on 10^6 random keys").
// We test the HARD case too: sequential keys 0..N-1.
//   1. chi-square of the 2^14 register buckets (should be ~ df = 16383)
//   2. distribution of rho (should be N/2^r)
//   3. every one of the 64 output bits should be 1 about half the time
#include <cmath>
#include <cstdio>
#include <vector>

#include "../src/gen.hpp"
#include "../src/hll.hpp"

static bool run(const char* name, bool sequential) {
  const uint64_t N = 1000000;
  const int p = 14;
  const uint32_t m = 1u << p;
  std::vector<uint64_t> bucket(m, 0), rho(64 - p + 2, 0), ones(64, 0);
  for (uint64_t k = 0; k < N; ++k) {
    const uint64_t key = sequential ? k : splitmix_mix(k);
    const uint64_t h = hash64(key, 0);
    bucket[h >> (64 - p)]++;
    const uint64_t w = (h << p) | (1ULL << (p - 1));
    rho[__builtin_clzll(w) + 1]++;
    for (int b = 0; b < 64; ++b) ones[b] += (h >> b) & 1;
  }
  const double expct = double(N) / m;
  double chi = 0;
  for (uint64_t c : bucket) chi += (c - expct) * (c - expct) / expct;
  const double df = m - 1, z = (chi - df) / std::sqrt(2 * df);
  bool ok = std::fabs(z) < 4;
  std::printf("%-22s chi2=%.0f (df=%.0f, z=%+.2f)\n", name, chi, df, z);

  double worst_rho = 0;
  for (int r = 1; r <= 12; ++r) {
    const double e = double(N) / std::pow(2.0, r);
    const double zz = (rho[r] - e) / std::sqrt(e);
    worst_rho = std::max(worst_rho, std::fabs(zz));
  }
  std::printf("%-22s rho=1..12 worst |z| = %.2f\n", "", worst_rho);
  ok = ok && worst_rho < 4.5;

  double worst_bit = 0;
  for (int b = 0; b < 64; ++b)
    worst_bit = std::max(worst_bit, std::fabs(ones[b] - N / 2.0) / (0.5 * std::sqrt(double(N))));
  std::printf("%-22s bit balance worst |z| = %.2f\n", "", worst_bit);
  ok = ok && worst_bit < 4.5;
  std::printf("%-22s => %s\n", "", ok ? "looks uniform" : "SUSPICIOUS");
  return ok;
}

int main() {
  bool a = run("XXH3-64, random keys", false);
  bool b = run("XXH3-64, sequential", true);
  return (a && b) ? 0 : 1;
}
