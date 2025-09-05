/*
 * Startup code in C for D1 SoC with XuanTie C906 RV64 core
 * Based on startup files of the libopencm3 project.
 *
 * Copyright (C) 2010 Piotr Esden-Tempski <piotr@esden.net>,
 * Copyright (C) 2012 chrysn <chrysn@fsfe.org>
 * Copyright (C) 2025 Sergey Matyukevich <geomatsi@gmail.com>
 */

#include <stdint.h>

#include "riscv_encoding.h"
#include "riscv_csr.h"
#include "thead_csr.h"

/* variables from linker script */

extern unsigned _sstack, _estack;
extern unsigned _sbss, _ebss;

/* misc functions declarations */

void _start(void) __attribute__((naked, section(".init")));
int main(void);

/* startup sequence */

void _start(void)
{
	volatile unsigned *ptr;

	/* setup c906 CSR registers: invalidate/reset/setup caches/branch_predictors/prefetchers/etc */

#if 1
	csr_set(CSR_MXSTATUS, MXSTATUS_THEADISAEE | MXSTATUS_MAEE | MXSTATUS_CLINTEE | MXSTATUS_UCME | MXSTATUS_MM);
	csr_write(CSR_MCOR, MCOR_IS | MCOR_DS | MCOR_INV_CACHE | MCOR_INV_BHT | MCOR_INV_BTB);
	csr_write(CSR_MHCR, MHCR_IE | MHCR_DE | MHCR_WA | MHCR_WB | MHCR_RS | MHCR_BPE | MHCR_BTB_C906 | MHCR_WBR | MHCR_BTB_E906);
	csr_write(CSR_MHINT, MHINT_DPLD | MHINT_AMR_LIMIT_3 | MHINT_IPLD | MHINT_D_DIS_PREFETCH_16 | MHINT_AEE);
#else
        csr_set(CSR_MXSTATUS, 0x638000);
        csr_write(CSR_MCOR, 0x70013);
        csr_write(CSR_MHCR, 0x11ff);
        csr_write(CSR_MHINT, 0x16e30c);
#endif

	/* setup sp and fp */

	__asm__ volatile(
		"mv	sp, %0\n\t"
		"add 	s0, sp, zero\n\t"
		: : "r"(&_estack) : );

	/* clear bss section */

	for (ptr= &_sbss; ptr < &_ebss; ptr++) {
		*ptr = 0x0;
	}

	/* fill stack region with 0xaa canaries */

	for (ptr = &_sstack; ptr < &_estack; ptr++) {
		*ptr = 0xaaaaaaaa;
	}

	/* jump to main */

	__asm__ volatile("jr %0\n\t" : : "r"(main) : );

	/* unreachable */

	while (1) {
		__asm__ volatile("wfi");
	}
}
