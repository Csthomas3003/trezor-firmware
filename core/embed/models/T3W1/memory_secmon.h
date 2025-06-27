/*
 * This file is part of the Trezor project, https://trezor.io/
 *
 * Copyright (c) SatoshiLabs
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#pragma once

// SHARED WITH MAKEFILE, LINKER SCRIPT etc.
// misc
#define FLASH_START (0x0C004000)

// FLASH layout
#define SECRET_START (0x0C000000)
#define SECRET_MAXSIZE (2 * 8 * 1024)  // 16 kB
#define SECRET_SECTOR_START 0x0
#define SECRET_SECTOR_END 0x1

// overlaps with secret
#define BHK_START (0x0C002000)
#define BHK_MAXSIZE (1 * 8 * 1024)  // 8 kB
#define BHK_SECTOR_START 0x1
#define BHK_SECTOR_END 0x1

#define BOARDLOADER_START (0x0C004000)
#define BOARDLOADER_MAXSIZE (12 * 8 * 1024)  // 96 kB
#define BOARDLOADER_SECTOR_START 0x2
#define BOARDLOADER_SECTOR_END 0xD

#define BOARDCAPS_START (0x0C01BF00)
#define BOARDCAPS_MAXSIZE 0x100

#define BOOTHEADER_START (0x0C01C000)
#define BOOTHEADER_MAXSIZE (2 * 8 * 1024)  // 16 kB
#define BOOTHEADER_SECTOR_START 0xE
#define BOOTHEADER_SECTOR_END 0xF

#define BOOTLOADER_START (0x0C020000)
#define BOOTLOADER_MAXSIZE (32 * 8 * 1024)  // 256 kB
#define BOOTLOADER_SECTOR_START 0x10
#define BOOTLOADER_SECTOR_END 0x2F

#define FIRMWARE_START (0x08060000)
#define FIRMWARE_START_S (0x0C060000)
#define FIRMWARE_MAXSIZE (414 * 8 * 1024)  // 3312 kB
#define FIRMWARE_SECTOR_START 0x30
#define FIRMWARE_SECTOR_END 0x1CD

#define ASSETS_START (0x0839C000)
#define ASSETS_MAXSIZE (16 * 8 * 1024)  // 128 kB
#define ASSETS_SECTOR_START 0x1CE
#define ASSETS_SECTOR_END 0x1DD

#define STORAGE_1_START (0x0C3BC000)
#define STORAGE_1_MAXSIZE (16 * 8 * 1024)  // 128 kB
#define STORAGE_1_SECTOR_START 0x1DE
#define STORAGE_1_SECTOR_END 0x1ED

#define STORAGE_2_START (0x0C3DC000)
#define STORAGE_2_MAXSIZE (16 * 8 * 1024)  // 128 kB
#define STORAGE_2_SECTOR_START 0x1EE
#define STORAGE_2_SECTOR_END 0x1FD

#define UPGRADEHEADER_START (0x0C3FC000)
#define UPGRADEHEADER_MAXSIZE (2 * 8 * 1024)  // 16 kB
#define UPGRADEHEADER_SECTOR_START 0x1FE
#define UPGRADEHEADER_SECTOR_END 0x1FF

// RAM layout
#define BOOTARGS_START (0x30000000)
#define BOOTARGS_SIZE 0x200

#define NONSECURE_RAM_START (0x20000200)
#define NONSECURE_RAM_SIZE ((768 + 64 + 768 + 832) * 1024 - 512)

#define FB1_RAM_START (0x20000200)
#define FB1_RAM_SIZE (768 * 1024 - 512)

#define MAIN_RAM_START (0x200C0000)
#define MAIN_RAM_SIZE (64 * 1024)

#define FB2_RAM_START (0x200D0000)
#define FB2_RAM_SIZE (768 * 1024)

#define AUX1_RAM_START (0x20190000)
#define AUX1_RAM_SIZE (832 * 1024)

#define SECMON_RAM_START (0x30260000)
#define SECMON_RAM_SIZE (64 * 1024)

// misc
#define CODE_ALIGNMENT 0x400
#define COREAPP_ALIGNMENT 0x2000
