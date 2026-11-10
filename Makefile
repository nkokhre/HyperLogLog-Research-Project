CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra
BIN = build

all: $(BIN)/test_hll $(BIN)/hash_check $(BIN)/exp1 $(BIN)/exp2 $(BIN)/exp3 $(BIN)/exp4_real

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

check: $(BIN)/test_hll $(BIN)/hash_check
	$(BIN)/test_hll && $(BIN)/hash_check

coverage: tests/test_hll.cpp src/*.hpp | $(BIN)
	clang++ -std=c++17 -O0 -fprofile-instr-generate -fcoverage-mapping $< -o $(BIN)/test_cov
	LLVM_PROFILE_FILE=$(BIN)/cov.profraw $(BIN)/test_cov > /dev/null
	xcrun llvm-profdata merge -o $(BIN)/cov.profdata $(BIN)/cov.profraw
	xcrun llvm-cov report $(BIN)/test_cov -instr-profile=$(BIN)/cov.profdata src/hll.hpp src/gen.hpp

clean:
	rm -rf $(BIN)
.PHONY: all check coverage clean
