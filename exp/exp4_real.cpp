// Experiment 4 (optional real dataset): distinct words in a public text.
// Usage: exp4_real <text file> <seeds> > out.csv
// Items = lowercase words (letters and apostrophes) between the Gutenberg
// START/END markers. True count = exact hash set. The word ORDER is fixed
// (real data); the 20 seeds only change the hash function.
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <unordered_set>
#include <vector>

#include "../src/hll.hpp"

int main(int argc, char** argv) {
  if (argc < 2) { std::fprintf(stderr, "usage: exp4_real file [seeds]\n"); return 1; }
  const int seeds = argc > 2 ? std::atoi(argv[2]) : 20;
  std::ifstream f(argv[1]);
  std::stringstream ss; ss << f.rdbuf();
  std::string txt = ss.str();
  size_t a = txt.find("*** START"); if (a != std::string::npos) a = txt.find('\n', a);
  size_t b = txt.find("*** END");
  txt = txt.substr(a == std::string::npos ? 0 : a, b == std::string::npos ? std::string::npos : b - (a == std::string::npos ? 0 : a));
  std::vector<std::string> words; std::string w;
  for (char c : txt) {
    if (std::isalpha((unsigned char)c) || c == '\'') w += char(std::tolower((unsigned char)c));
    else if (!w.empty()) { words.push_back(w); w.clear(); }
  }
  if (!w.empty()) words.push_back(w);
  std::unordered_set<std::string> exact(words.begin(), words.end());
  const double truth = double(exact.size());
  std::fprintf(stderr, "words=%zu distinct=%zu\n", words.size(), exact.size());
  std::printf("p,m,seed,total_words,true_distinct,est_basic,est_lc,empty_frac\n");
  for (int p = 8; p <= 14; ++p)
    for (int seed = 1; seed <= seeds; ++seed) {
      HyperLogLog h(p);
      for (const auto& s : words) h.add_hash(XXH3_64bits_withSeed(s.data(), s.size(), seed));
      std::printf("%d,%u,%d,%zu,%.0f,%.6f,%.6f,%.6f\n", p, h.m(), seed, words.size(), truth,
                  h.estimate_basic(), h.estimate_lc(), h.empty_fraction());
    }
}
