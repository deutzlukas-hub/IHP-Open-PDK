# Makefile for Ngspice tests
# (c) Felix Salfelder 2024
#     Lukas Deutz 2026
# GPLv3+
NGSPICE = ngspice
DIFF = diff
# Exclude test files starting with
TEST_EXCLUDE_PREFIX = wip_
# Force rebuild on check
MAKEFLAGS += -B

REPEATS ?= 5
RUNS := $(shell seq 1 $(REPEATS))

TESTDIRS = \
	inv_chain \
	multiplier \

# Discover tests automatically: resistor/*.sp, moslv/*.sp, ...
ALL_TESTS := $(foreach d, $(TESTDIRS), $(wildcard $(d)/*.sp))
ALL_TESTS := $(foreach f,$(ALL_TESTS), $(if $(filter $(TEST_EXCLUDE_PREFIX)%,$(notdir $(f))),,$(f)))
# Each test generates an output
ALL_OUTS := $(foreach f, $(ALL_TESTS), $(dir $(f))check/$(notdir $(f)).out)

# Each test generates a log for benchmarking
ALL_LOGS := $(foreach f, $(ALL_TESTS), $(foreach n, $(RUNS), $(dir $(f))logs/$(notdir $(f)).$(n).log))

# Check all tests
check: $(ALL_OUTS)
# Bench all tests
bench: $(ALL_LOGS)

# Rule: one test file *.sp generates one output file *.sp.out
define CHECK_RULE
$(dir $(1))check/$(notdir $(1)).out: $(1)
	@mkdir -p $(dir $(1))check
	@cd "$(dir $(1))" && \
	  $(NGSPICE) -b -o /dev/null "$(notdir $(1))" > /dev/null
	@if [ -f "$(dir $(1))ref/$(notdir $(1)).out" ]; then \
	  if $(DIFF) -u "$(dir $(1))ref/$(notdir $(1)).out" "$$@" > "$$(basename $$@).diff" 2>&1; then \
	    echo "PASS $$(notdir $$<)"; \
	    rm -f "$$(basename $$@).diff"; \
	  else \
	    echo "FAIL $$(notdir $$<)"; \
	  fi; \
	else \
	  echo "MISS $$(notdir $$<)"; \
	fi
endef

# Create one output file target for each test file using TEST_RULE
$(foreach f, $(ALL_TESTS), $(eval $(call CHECK_RULE,$(f))))

# Rule: Make each test directory an aggregate target for its test
define DIR_CHECK_RULE
check-$(1): $(foreach f, $(filter $(1)/%.sp, $(ALL_TESTS)), $(dir $(f))check/$(notdir $(f)).out)
endef
# Create one aggregate per directory in TESTDIRS using DIR_RULE
$(foreach d, $(TESTDIRS), $(eval $(call DIR_CHECK_RULE,$(d))))

# Rule: one test file *.sp generates #REPEATS *.sp.{run}.log files
define BENCH_RULE
$(dir $(1))logs/$(notdir $(1)).$(2).log: $(1)
	@mkdir -p $(dir $(1))logs
	@printf "%-30s [%s/%s]\n" "$(notdir $(1))" "$(2)" "$(REPEATS)"
	@cd "$(dir $(1))" && \
	  $(NGSPICE) -b -o "logs/$(notdir $(1)).$(2).log" "$(notdir $(1))" > /dev/null
endef

# Create one log file target per run for each test
$(foreach f, $(ALL_TESTS), $(foreach run, $(RUNS), $(eval $(call BENCH_RULE,$(f),$(run)))))

# Rule: Make each test directory an aggregate target for its test
define DIR_BENCH_RULE
bench-$(1): $(foreach f, $(filter $(1)/%.sp, $(ALL_TESTS)), \
				$(foreach n, $(RUNS), \
					$(dir $(f))logs/$(notdir $(f)).$(n).log))
endef

# Create one aggregate per directory in TESTDIRS using DIR_RULE
$(foreach d, $(TESTDIRS), $(eval $(call DIR_BENCH_RULE,$(d))))

# Rule: Make each test file an aggregate target for benchmarking (bench-<testname>)
define TEST_BENCH_RULE
bench-$(basename $(notdir $(1))): $(foreach n, $(RUNS), $(dir $(1))logs/$(notdir $(1)).$(n).log)
endef

# Create one bench target per test file
$(foreach f, $(ALL_TESTS), $(eval $(call TEST_BENCH_RULE,$(f))))

clean:
	@for dir in $(TESTDIRS); do \
	  rm -rf $$dir/check; \
	done

# Help
help:
	@echo "Ngspice Test Suite"
	@echo ""
	@echo "Targets:"
	@echo "  check            - Run all tests (default)"
	@echo "  clean            - Remove all test outputs"
	@echo "  check-<testdir>  - Run tests in specified directory"
	@echo "  bench            - Run all tests REPEATS time and log performance"
	@echo "  bench-<testdir>  - Benchmark tests in specified directory"
	@echo "  bench-<testname> - Benchmark a specific test file REPEATS times"
	@echo ""
	@echo "Test directories:"
	@for dir in $(TESTDIRS); do echo "  $$dir"; done
	@echo ""
	@echo "Total tests: $(words $(ALL_TESTS))"

.PHONY: check clean $(TESTDIRS) help

