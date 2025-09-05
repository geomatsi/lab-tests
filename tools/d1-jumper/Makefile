#
#
#

CROSS_COMPILE ?= riscv64-unknown-elf-

CP = $(CROSS_COMPILE)objcopy
CC = $(CROSS_COMPILE)gcc
AS = $(CROSS_COMPILE)as
LD = $(CROSS_COMPILE)ld

BUILD ?= build

RISCV_ABI = lp64
RISCV_ELF = elf64lriscv
RISCV_ISA = rv64imac_zicsr_zifencei

ASFLAGS = -march=$(RISCV_ISA)

CCFLAGS = -march=$(RISCV_ISA) -mabi=$(RISCV_ABI) -mcmodel=medany
CCFLAGS += -ffunction-sections -fdata-sections -ffreestanding -fno-stack-protector
CCFLAGS += -Wall -Wextra -Werror -O2 -std=gnu99

LDFLAGS = -m $(RISCV_ELF)
LDFLAGS += -nostdlib --fatal-warnings --gc-sections
# FIXME: suppress warning about RWX SRAM:
LDFLAGS += --no-warn-rwx-segment

CCFLAGS += -Iinclude

ifdef FW_JUMP_FDT_OFFSET
CCFLAGS += -DFW_JUMP_FDT_OFFSET=$(FW_JUMP_FDT_OFFSET)
endif

ifdef DRAM_START
CCFLAGS += -DDRAM_START=$(DRAM_START)
endif

VPATH += src crt

all: jump1 jump2

# jump1: c + asm

JUMP1_ASRCS := start1.S
JUMP1_CSRCS := jump.c
JUMP1_OBJS := $(patsubst %, $(BUILD)/%, $(JUMP1_ASRCS:.S=.o))
JUMP1_OBJS += $(patsubst %, $(BUILD)/%, $(JUMP1_CSRCS:.c=.o))
JUMP1_LDS := ld/d1.ld

jump1: $(JUMP1_LDS) $(JUMP1_OBJS)
	$(LD) $(LDFLAGS) -T$< $(filter-out $<, $^) -o $(BUILD)/$@.elf
	$(CP) -O binary $(BUILD)/$@.elf $(BUILD)/$@.bin

# jump2: pure c

JUMP2_CSRCS := start2.c jump.c
JUMP2_OBJS := $(patsubst %, $(BUILD)/%, $(JUMP2_CSRCS:.c=.o))
JUMP2_LDS := ld/d1.ld

jump2: $(JUMP2_LDS) $(JUMP2_OBJS)
	$(LD) $(LDFLAGS) -T$< $(filter-out $<, $^) -o $(BUILD)/$@.elf
	$(CP) -O binary $(BUILD)/$@.elf $(BUILD)/$@.bin

# common

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/%.o: %.s | $(BUILD)
	$(AS) $(ASFLAGS) $< -o $@

$(BUILD)/%.o: %.c | $(BUILD)
	$(CC) $(OPTS) $(CCFLAGS) -c $< -o $@

tags:
	ctags -a -R src crt common

clean:
	rm -rf $(BUILD)

.PHONY: all clean tags
