// Input generator: random 64-bit IDs with some repeats.
//
// id(base, k) = splitmix64 mix of (base + k). The mix is a bijection on
// 64-bit integers, so distinct k give distinct IDs and the TRUE distinct
// count is known by construction (no hash set needed; tests cross-check it).
#pragma once
#include <cstdint>

inline uint64_t splitmix_mix(uint64_t z) {
  z += 0x9e3779b97f4a7c15ULL;
  z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
  z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
  return z ^ (z >> 31);
}

class IdStream {
 public:
  // dup_prob: after each new ID, with this probability emit one repeat of a
  // uniformly random earlier ID. True distinct count = number of new IDs.
  explicit IdStream(uint64_t seed, double dup_prob = 0.5)
      : base_(splitmix_mix(seed * 2 + 1)),
        rng_(splitmix_mix(seed * 2 + 2)),
        dup_prob_(dup_prob) {}

  uint64_t id(uint64_t k) const { return splitmix_mix(base_ + k); }

  // Call for k = 0,1,2,...; emits the new ID, then maybe a repeat, via f.
  template <class F>
  void emit(uint64_t k, F&& f) {
    f(id(k));
    if (next_double() < dup_prob_) f(id(next_u64() % (k + 1)));
  }

 private:
  uint64_t next_u64() { return splitmix_mix(rng_++); }
  double next_double() { return (next_u64() >> 11) * (1.0 / 9007199254740992.0); }
  uint64_t base_, rng_;
  double dup_prob_;
};
