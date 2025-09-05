/* SPDX-License-Identifier: GPL-2.0+ */

#ifndef _THEAD_CSR_H_
#define _THEAD_CSR_H_

#define CSR_MXSTATUS		0x7c0
#define CSR_MHCR		0x7c1
#define CSR_MCOR		0x7c2
#define CSR_MHINT		0x7c5

#define MXSTATUS_THEADISAEE	BIT(22) /* T-HEAD ISA extensions enable */
#define MXSTATUS_MAEE		BIT(21) /* extend MMU address attribute */
#define MXSTATUS_CLINTEE	BIT(17) /* CLINT timer/software interrupt S-mode enable */
#define MXSTATUS_UCME		BIT(16) /* execute extended cache instructions in U-mode */
#define MXSTATUS_MM		BIT(15) /* misaligned access enable */

#define MCOR_IS			BIT(0)  /* I-cache selected */
#define MCOR_DS			BIT(1)  /* D-cache selected */
#define MCOR_INV_CACHE		BIT(4)	/* invalidate selected caches */
#define MCOR_CLR_CACHE		BIT(5)  /* clean selected caches */
#define MCOR_INV_BHT		BIT(16) /* invalidate branch history tables */
#define MCOR_INV_BTB		BIT(17) /* invalidate branch target buffers */

#define MHCR_IE			BIT(0)	/* I-cache enable */
#define MHCR_DE			BIT(1)	/* D-cache enable */
#define MHCR_WA			BIT(2)	/* D-cache write allocate */
#define MHCR_WB			BIT(3)	/* D-cache write back */
#define MHCR_RS			BIT(4)	/* return stack enable */
#define MHCR_BPE		BIT(5)	/* branch prediction enable */
#define MHCR_BTB_C906		BIT(6)	/* branch target prediction enable */
#define MHCR_WBR		BIT(8)	/* write burst enable */
#define MHCR_BTB_E906		BIT(12) /* branch target prediction enable */

#define MHINT_DPLD		BIT(2)	/* D-cache prefetch enable */
#define MHINT_AMR_PAGE		(0x0 << 3)
#define MHINT_AMR_LIMIT_3	(0x1 << 3)
#define MHINT_AMR_LIMIT_64	(0x2 << 3)
#define MHINT_AMR_LIMIT_128	(0x3 << 3)
#define MHINT_IPLD		BIT(8)	/* I-cache prefetch enable */
#define MHINT_IWPE		BIT(10)	/* I-cache way prediction enable */
#define MHINT_D_DIS_PREFETCH_2	(0x0 << 13)
#define MHINT_D_DIS_PREFETCH_4	(0x1 << 13)
#define MHINT_D_DIS_PREFETCH_8	(0x2 << 13)
#define MHINT_D_DIS_PREFETCH_16	(0x3 << 13)
#define MHINT_AEE		BIT(20) /* accurate exception enable */

#endif /* _THEAD_CSR_H_ */
