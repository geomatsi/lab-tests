/*
 * Startup code for D1 SoC SRAM
 *
 * Copyright (c) 2025 geomatsi@gmail.com
 */

	.section .init, "ax", @progbits
	.globl _start
	.globl main
	.align 1

_start:
	/* setup c906 CSR registers: caches, prefetchers, etc */

        li t1, 0x638000
        csrs 0x7c0, t1

        li t1, 0x70013
        csrs 0x7c2, t1

        li t1, 0x11ff
        csrs 0x7c1, t1

        li t1, 0x16e30c
        csrs 0x7c5, t1

	/* setup sp and fp */

	la sp, _estack
	la s0, _estack

	/* clear bss section */

	la a0, _sbss
	la a1, _ebss
	bgeu a0, a1, 2f
1:
	sw zero, (a0)
	addi a0, a0, 4
	bltu a0, a1, 1b
2:

	/* fill stack region with 0xaa canaries */

	la a0, _sstack
	la a1, _estack
	bgeu a0, a1, 2f
	li t0, 0xaaaaaaaa
1:
	sw t0, (a0)
	addi a0, a0, 4
	bltu a0, a1, 1b
2:

	/* setup mtvec */

	la t0, m_trap_entry
	csrw mtvec, t0

	/* setup stvec */
	la t0, s_trap_entry
	csrw stvec, t0

	/* main */

	jal main

	/* unreachable */
1:
	wfi
	j 1b

	.section .init, "ax", @progbits
	.weak m_trap_handler
	.align 4

m_trap_entry:
	j m_trap_handler

m_trap_handler:
1:
	wfi
	j 1b

	.section .init, "ax", @progbits
	.weak s_trap_handler
	.align 4

s_trap_entry:
	j s_trap_handler

s_trap_handler:
1:
	wfi
	j 1b
