// Experiment 6: does the crossover also show up on real text?
// Usage: exp6_real_crossover <text file> <hash seeds> <p1,p2,...> > out.csv
//
// The words of the text are streamed in their real order. The number of
// distinct words so far is known exactly (hash set), so we can snapshot a
// sketch the moment the distinct count reaches n = t*m for every grid value
// t = n/m (same grid as exp5, cut at the text's total distinct count).
// The text and its order are fixed; the seeds change only the hash function.
//   columns: p, seed, n, t, est_raw, empty
#include <cctype>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <set>
#include <sstream>
#include <string>
#include <unordered_set>
#include <vector>

#include "../src/hll.hpp"

static std::vector<double> t_grid() {  // identical to exp5_crossover.cpp
  std::set<long> g;
  for (int i = 250; i <= 1500; i += 125) g.insert(i);
  for (int i = 1500; i <= 5000; i += 50) g.insert(i);
  for (int i = 5000; i <= 8000; i += 250) g.insert(i);
  std::vector<double> t;
  for (long v : g) t.push_back(v / 1000.0);
  return t;
}

int main(int argc, char** argv) {
  if (argc < 2) { std::fprintf(stderr, "usage: exp6_real_crossover file [seeds] [p-list]\n"); return 1; }
  const int seeds = argc > 2 ? std::atoi(argv[2]) : 200;
  std::string plist = argc > 3 ? argv[3] : "8,10,12";
  std::vector<int> ps;
  { std::stringstream ss(plist); std::string tok; while (std::getline(ss, tok, ',')) ps.push_back(std::atoi(tok.c_str())); }

  std::ifstream f(argv[1]);
  std::stringstream ss; ss << f.rdbuf();
  std::string txt = ss.str();
  size_t a = txt.find("*** START"); if (a != std::string::npos) a = txt.find('\n', a);
  size_t b = txt.find("*** END");
  const size_t from = (a == std::string::npos) ? 0 : a;
  txt = txt.substr(from, b == std::string::npos ? std::string::npos : b - from);
  std::vector<std::string> words; std::string w;
  for (char c : txt) {
    if (std::isalpha((unsigned char)c) || c == '\'') w += char(std::tolower((unsigned char)c));
    else if (!w.empty()) { words.push_back(w); w.clear(); }
  }
  if (!w.empty()) words.push_back(w);

  // distinct count after each word (exact)
  std::vector<uint32_t> distinct_after(words.size());
  { std::unordered_set<std::string> seen; for (size_t i = 0; i < words.size(); ++i) { seen.insert(words[i]); distinct_after[i] = uint32_t(seen.size()); } }
  const uint32_t total_distinct = distinct_after.back();
  std::fprintf(stderr, "words=%zu distinct=%u\n", words.size(), total_distinct);

  const std::vector<double> grid = t_grid();
  std::printf("p,seed,n,t,est_raw,empty\n");
  for (int p : ps) {
    const uint64_t m = 1ULL << p;
    std::vector<uint64_t> cps;
    for (double t : grid) { const uint64_t n = std::llround(t * double(m)); if (n <= total_distinct) cps.push_back(n); }
    for (int seed = 1; seed <= seeds; ++seed) {
      HyperLogLog h(p);
      size_t ci = 0;
      for (size_t i = 0; i < words.size() && ci < cps.size(); ++i) {
        h.add_hash(XXH3_64bits_withSeed(words[i].data(), words[i].size(), seed));
        while (ci < cps.size() && distinct_after[i] == cps[ci]) {
          std::printf("%d,%d,%llu,%.4f,%.4f,%u\n", p, seed, (unsigned long long)cps[ci],
                      double(cps[ci]) / double(m), h.estimate_basic(), h.empty_registers());
          ++ci;
        }
      }
    }
  }
}
