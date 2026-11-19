// HyperLogLog, written from scratch so the registers are visible.
//
// One sketch gives BOTH estimates, because linear counting only changes the
// last step (the estimate), never the update:
//   estimate_basic() - raw HyperLogLog formula (the seminar baseline)
//   estimate_lc()    - raw formula, but linear counting when raw <= 2.5 m
//                      and at least one register is empty (textbook rule)
//   estimate_lc_only(), estimate_switch(c), estimate_switch_empty(f) -
//                      pure LC and configurable switch rules (crossover study)
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <stdexcept>
#include <vector>

#define XXH_INLINE_ALL
#include "../third_party/xxHash/xxhash.h"

// 64-bit hash of a 64-bit key. `seed` lets every run use a different hash.
inline uint64_t hash64(uint64_t key, uint64_t seed = 0) {
  return XXH3_64bits_withSeed(&key, sizeof(key), seed);
}

class HyperLogLog {
 public:
  explicit HyperLogLog(int p) : p_(p), m_(1u << p), reg_(m_, 0) {
    if (p < 4 || p > 18) throw std::invalid_argument("p must be in [4,18]");
  }

  int p() const { return p_; }
  uint32_t m() const { return m_; }
  const std::vector<uint8_t>& registers() const { return reg_; }

  // The first p bits choose the register, the remaining 64-p bits give the
  // position of the first 1-bit (rho = leading zeros + 1).
  void add_hash(uint64_t h) {
    const uint32_t idx = static_cast<uint32_t>(h >> (64 - p_));
    // Shift the index bits out; put a sentinel 1 just below the remaining
    // bits so an all-zero remainder gives rho = 64-p+1 instead of undefined.
    const uint64_t w = (h << p_) | (1ULL << (p_ - 1));
    const uint8_t rho = static_cast<uint8_t>(__builtin_clzll(w) + 1);
    if (rho > reg_[idx]) reg_[idx] = rho;
  }

  void add(uint64_t key, uint64_t seed = 0) { add_hash(hash64(key, seed)); }

  // Merge = register-wise max. Same result as one sketch over both streams.
  void merge(const HyperLogLog& o) {
    if (o.p_ != p_) throw std::invalid_argument("merge: different p");
    for (uint32_t i = 0; i < m_; ++i) reg_[i] = std::max(reg_[i], o.reg_[i]);
  }

  uint32_t empty_registers() const {
    uint32_t v = 0;
    for (uint8_t r : reg_) v += (r == 0);
    return v;
  }
  double empty_fraction() const { return double(empty_registers()) / m_; }

  // E = alpha_m * m^2 / sum_j 2^-M[j]
  double estimate_basic() const {
    double sum = 0.0;
    for (uint8_t r : reg_) sum += std::ldexp(1.0, -static_cast<int>(r));
    return alpha() * double(m_) * double(m_) / sum;
  }

  // Linear counting m*ln(m/V) for V empty registers. V is clamped to >= 1 so
  // the formula is defined (and capped at m*ln(m)) when no register is empty.
  static double lc_value(uint32_t m, uint32_t empty) {
    const uint32_t v = empty > 0 ? empty : 1;
    return double(m) * std::log(double(m) / double(v));
  }

  // Pure linear counting: always uses the empty-register formula.
  double estimate_lc_only() const { return lc_value(m_, empty_registers()); }

  // Switch rule on the raw estimate E: linear counting if E <= c*m and at
  // least one register is empty, otherwise the raw estimate.
  double estimate_switch(double c) const {
    const double e = estimate_basic();
    if (e <= c * m_) {
      const uint32_t v = empty_registers();
      if (v > 0) return lc_value(m_, v);
    }
    return e;
  }

  // Switch rule on the share of empty registers: linear counting while more
  // than a share f of the registers are empty, otherwise the raw estimate.
  double estimate_switch_empty(double f) const {
    const uint32_t v = empty_registers();
    if (v > 0 && double(v) / m_ > f) return lc_value(m_, v);
    return estimate_basic();
  }

  // The textbook rule: switch at E <= 2.5 m (our baseline "HLL + LC").
  double estimate_lc() const { return estimate_switch(2.5); }

  // Theory value for the standard error: 1.04 / sqrt(m).
  double theory_std_error() const { return 1.04 / std::sqrt(double(m_)); }

  // Memory with 6-bit registers (what the theory counts) vs. what we store.
  size_t bytes_packed_6bit() const { return (size_t(m_) * 6 + 7) / 8; }
  size_t bytes_stored() const { return reg_.size(); }

 private:
  double alpha() const {
    switch (m_) {
      case 16: return 0.673;
      case 32: return 0.697;
      case 64: return 0.709;
      default: return 0.7213 / (1.0 + 1.079 / double(m_));
    }
  }
  int p_;
  uint32_t m_;
  std::vector<uint8_t> reg_;
};
