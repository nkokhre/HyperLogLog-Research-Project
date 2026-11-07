// HyperLogLog, written from scratch so the registers are visible.
//
// One sketch gives BOTH estimates, because linear counting only changes the
// last step (the estimate), never the update:
//   estimate_basic() - raw HyperLogLog formula (the seminar baseline)
//   estimate_lc()    - raw formula, but linear counting when raw <= 2.5 m
//                      and at least one register is empty
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

  // Basic estimate, switched to linear counting m*ln(m/V) for small counts.
  double estimate_lc() const {
    const double e = estimate_basic();
    if (e <= 2.5 * m_) {
      const uint32_t v = empty_registers();
      if (v > 0) return double(m_) * std::log(double(m_) / double(v));
    }
    return e;
  }

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
