### Build d1-jumper

```bash
$ make CROSS_COMPILE=/path/to/riscv64-unknown-elf-
```

### Flash software

For kernel images smaller than 32M:

```bash
sudo xfel version
sudo xfel ddr d1
sudo xfel write 0x20000 jump.bin
sudo xfel write 0x40000000 fw_jump.bin
sudo xfel write 0x42200000 sun20i-d1-mangopi-mq-pro.dtb
sudo xfel write 0x40200000 Image
sudo xfel exec 0x20000
```

If kernel image is larger than 32M, then move device tree blob high enough
to avoid overlap with the kernel image. For this purpose do the following.

1. Rebuild d1-jumper increasing FW_JUMP_FDT_OFFSET:

```bash
$ make CROSS_COMPILE=/path/to/riscv64-unknown-elf- FW_JUMP_FDT_OFFSET=0x4200000
```

2. Rebuild OpenSBI increasing FW_JUMP_FDT_OFFSET:

```bash
$ make CROSS_COMPILE=riscv64-buildroot-linux-gnu- PLATFORM=generic FW_JUMP_FDT_OFFSET=0x4200000
```

3. Modify xfel DTB load address accordingly:

```bash
sudo xfel version
sudo xfel ddr d1
sudo xfel write 0x20000 jump.bin
sudo xfel write 0x40000000 fw_jump.bin
sudo xfel write 0x44200000 sun20i-d1-mangopi-mq-pro.dtb
sudo xfel write 0x40200000 Image
sudo xfel exec 0x20000
```

