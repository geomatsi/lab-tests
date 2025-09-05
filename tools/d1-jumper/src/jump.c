#include <stdint.h>

#include "riscv_encoding.h"
#include "riscv_csr.h"
#include "thead_csr.h"

#ifndef DRAM_START
#define DRAM_START 0x40000000
#endif

#ifndef FW_JUMP_FDT_OFFSET
#define FW_JUMP_FDT_OFFSET 0x2200000
#endif

typedef void (*next_boot)(long hartid, long dtb_addr, long dynamic_info_addr);

void fence_i(void)
{
	__asm__ volatile ("fence.i" : : : );
}

void jump_to(long jump_addr, long hartid, long dtb_addr, long dynamic_info_addr)
{
	next_boot opensbi = (next_boot)jump_addr;

	fence_i();

	/* OpenSBI expectations:
	 * - a0 - hartid
	 * - a1 - DTB address
	 * - a2 - struct fw_dynamic addr (only for fw_dynamic)
	 */

	opensbi(hartid, dtb_addr, dynamic_info_addr);
}

int main(void)
{
	jump_to(DRAM_START, 0x0, DRAM_START + FW_JUMP_FDT_OFFSET, 0x0);
}
