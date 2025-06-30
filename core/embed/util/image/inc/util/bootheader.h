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

#include <trezor_types.h>

#define BOOTHEADER_PQ_SIGNATURE_LEN 7856
#define BOOTHEADER_MERKLE_PATH_MAX_LEN 16

/**
 * Signed part of the boot header
 */
typedef struct {
  uint32_t magic;        // 'TRZQ'
  uint32_t hw_model;     // Hardware model, e.g. 'T3W1'
  uint32_t hw_revision;  // Hardware revision, e.g. 1
  uint32_t version;
  uint32_t fix_version;
  uint32_t monotonic_version;
  uint32_t header_size;  // Size of the header in bytes
  uint32_t code_size;    // Size of the code in bytes
  uint32_t reserved[8];
} __attribute__((packed)) bootheader_signed_t;

/**
 * Unsigned part of the boot header
 */
typedef struct {
  uint32_t merkle_path_len;
  uint8_t merkle_path[32][BOOTHEADER_MERKLE_PATH_MAX_LEN];
  uint8_t reserved[60];
  uint8_t signature1[BOOTHEADER_PQ_SIGNATURE_LEN];
  uint8_t signature2[BOOTHEADER_PQ_SIGNATURE_LEN];
} __attribute__((packed)) bootheader_unsigned_t;

/**
 * Dynamic part of the boot header filled by the bootloader at runtime.
 */
typedef struct {
  // Pointer to the bootloader image in flash
  void* bootloader_image;
  uint32_t reserved[7];
} __attribute__((packed)) bootheader_dynamic_t;

/**
 * Structure of boot header
 */
typedef struct {
  bootheader_signed_t sig;
  bootheader_unsigned_t uns;
  bootheader_dynamic_t dyn;
} __attribute__((packed)) bootheader_t;

secbool verify_bootheader(void);
