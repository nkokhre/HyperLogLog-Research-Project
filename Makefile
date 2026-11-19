CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra
BIN = build

all: $(BIN)/test_hll $(BIN)/hash_check $(BIN)/exp1 $(BIN)/exp2 $(BIN)/exp3 $(BIN)/exp4_real $(BIN)/exp5_crossover $(BIN)/exp6_real_crossover

$(BIN):
	mkdir -p $(BIN)

$(BIN)/test_hll: tests/test_hll.cpp src/*.hpp | $(BIN)
	$(CXX) $(CXXFLAGS) $< -o $@
$(BIN)/hash_check: tools/hash_check.cpp src/*.hpp | $(BIN)
	$(CXX) $(CXXFLAGS) $< -o $@
$(BIN)/exp1: exp/exp1.cpp src/*.hpp | $(BIN)
	$(CXX) $(CXXFLAGS) -O3 $< -o $@
$(BIN)/exp2: exp/exp2.cpp src/*.hpp | $(BIN)
	$(CXX) $(CXXFLAGS) -O3 $< -o $@
$(BIN)/exp3: exp/exp3.cpp src/*.hpp | $(BIN)
	$(CXX) $(CXXFLAGS) -O3 $< -o $@
$(BIN)/exp4_real: exp/exp4_real.cpp src/*.hpp | $(BIN)
	$(CXX) $(CXXFLAGS) -O3 $< -o $@
$(BIN)/exp5_crossover: exp/exp5_crossover.cpp src/*.hpp | $(BIN)
	$(CXX) $(CXXFLAGS) -O3 $< -o $@
$(BIN)/exp6_real_crossover: exp/exp6_real_crossover.cpp src/*.hpp | $(BIN)
	$(CXX) $(CXXFLAGS) -O3 $< -o $@

check: $(BIN)/test_hll $(BIN)/hash_check
	$(BIN)/test_hll && $(BIN)/hash_check

check-analysis:
	python3 tests/test_analysis.py

coverage: tests/test_hll.cpp src/*.hpp | $(BIN)
	clang++ -std=c++17 -O0 -fprofile-instr-generate -fcoverage-mapping $< -o $(BIN)/test_cov
	LLVM_PROFILE_FILE=$(BIN)/cov.profraw $(BIN)/test_cov > /dev/null
	xcrun llvm-profdata merge -o $(BIN)/cov.profdata $(BIN)/cov.profraw
	xcrun llvm-cov report $(BIN)/test_cov -instr-profile=$(BIN)/cov.profdata src/hll.hpp src/gen.hpp

clean:
	rm -rf $(BIN)
.PHONY: all check check-analysis coverage clean exp5-run plots slides pdfs

# Main experiment (crossover): raw data -> analysis -> plots -> slides.  Takes ~1 minute.
exp5-run: $(BIN)/exp5_crossover $(BIN)/exp6_real_crossover
	$(BIN)/exp5_crossover 500 8,10,12,14,16 | gzip -9n > results/exp5_raw.csv.gz
	$(BIN)/exp6_real_crossover data/war_and_peace.txt 200 8,10,12 | gzip -9n > results/exp6_real_raw.csv.gz
	python3 exp/analyze_exp5.py
	$(MAKE) plots slides

plots:
	python3 exp/plot_exp5.py
	python3 exp/plot_schematics.py
	python3 exp/plot_extra.py

slides:
	python3 report/make_slides.py

# PDFs from the HTML sources (needs Google Chrome; set CHROME=... on other systems)
CHROME ?= /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
pdfs:
	"$(CHROME)" --headless=new --disable-gpu --allow-file-access-from-files --no-pdf-header-footer --print-to-pdf="$(CURDIR)/report.pdf" "file://$(CURDIR)/report/report.html"
	"$(CHROME)" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="$(CURDIR)/proposal.pdf" "file://$(CURDIR)/report/proposal.html"
