.POSIX:
.SUFFIXES:

CONT_RUNNER = podman
CONT_BUILDER = podman
CONT_IMAGE_TAG = nethack_external_pokedex_ssh
CONT_IIDFILE = $(CONT_IMAGE_TAG).iidfile
CONT_PORT_ARGS = -p 3722:22
PROJECT_ROOT = ..
CONT_BUILD_CTX = $(PROJECT_ROOT)
SRC_DIR = $(PROJECT_ROOT)
SOURCES = \
	$(SRC_DIR)/main.py \
	$(SRC_DIR)/filters.py \
	$(SRC_DIR)/checker.py \
	$(SRC_DIR)/make_card.py \
	$(SRC_DIR)/parse.py \
	$(SRC_DIR)/utils.py \
	$(SRC_DIR)/nhconstants_atk.py \
	$(SRC_DIR)/nhconstants_common.py \
	$(SRC_DIR)/nhconstants_flags.py \
	$(SRC_DIR)/nhconstants_flags_raw.py
DATA_DIR = $(PROJECT_ROOT)/data
DATA_FILES = \
	$(DATA_DIR)/dnh.csv \
	$(DATA_DIR)/eh09.csv \
	$(DATA_DIR)/nh343.csv \
	$(DATA_DIR)/nh367.csv \
	$(DATA_DIR)/nh370.csv \
	$(DATA_DIR)/se007.csv \
	$(DATA_DIR)/un6.csv \
	$(DATA_DIR)/xnh9.csv
DEPLOY_DIR = $(PROJECT_ROOT)/deploy

.PHONY: container_image all clean run
all: container_image
run: container_image
	$(CONT_RUNNER) run $(CONT_PORT_ARGS) $(CONT_IMAGE_TAG)
container_image: $(CONT_IIDFILE)
$(CONT_IIDFILE): $(DEPLOY_DIR)/Containerfile $(SOURCES) $(DATA_FILES)
	$(CONT_BUILDER) build -t $(CONT_IMAGE_TAG) -f "$(DEPLOY_DIR)/Containerfile" \
	    --iidfile "$(CONT_IIDFILE)" \
		"$(CONT_BUILD_CTX)"
clean:
	rm -f "$(CONT_IIDFILE)"
