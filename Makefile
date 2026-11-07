CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra
BIN = build

all: $(BIN)/test_hll $(BIN)/hash_check $(BIN)/exp1

$(BIN):
	mkdir -p $(BIN)

$(BIN)/test_hll: tests/test_hll.cpp src/*.hpp | $(BIN)
	$(CXX) $(CXXFLAGS) $< -o $@
$(BIN)/hash_check: tools/hash_check.cpp src/*.hpp | $(BIN)
	$(CXX) $(CXXFLAGS) $< -o $@
$(BIN)/exp1: exp/exp1.cpp src/*.hpp | $(BIN)
	$(CXX) $(CXXFLAGS) -O3 $< -o $@

check: $(BIN)/test_hll $(BIN)/hash_check
	$(BIN)/test_hll && $(BIN)/hash_check

clean:
	rm -rf $(BIN)
.PHONY: all check clean
