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

#include <trezor_model.h>
#include <trezor_rtl.h>

#include <sys/mpu.h>
#include <util/bootheader.h>

#ifdef BOARDLOADER
#include "api.h"  // !@# TODO: fix the path
#endif

_Static_assert(sizeof(bootheader_t) == BOOTHEADER_MAXSIZE,
               "bootheader_t size mismatch");

_Static_assert(BOOTHEADER_MAXSIZE == UPGRADEHEADER_MAXSIZE,
               "BOOTHEADER doesn't match UPGRADEHEADER size");

#ifdef BOARDLOADER

secbool verify_bootheader(void) {
  // Development public key
  static const uint8_t pk[32] = {
      0xec, 0x01, 0xe6, 0x02, 0x63, 0x02, 0x4f, 0x7e, 0x71, 0x72, 0x80,
      0x13, 0xb7, 0x31, 0xf7, 0xba, 0x12, 0x99, 0xf5, 0x18, 0xc2, 0x7b,
      0xa3, 0xed, 0x8f, 0x4a, 0x21, 0x99, 0x74, 0x12, 0x7c, 0x62};

  const bootheader_t *bootheader = (const bootheader_t *)BOOTHEADER_START;

  const uint8_t *msg = (const uint8_t *)BOOTLOADER_START;
  size_t msg_size = 1024;

  mpu_mode_t mpu_mode = mpu_reconfig(MPU_MODE_BOOTHEADER);
  int result =
      crypto_sign_verify(bootheader->uns.signature1,
                         BOOTHEADER_PQ_SIGNATURE_LEN, msg, msg_size, pk);

  mpu_restore(mpu_mode);

  return sectrue * (result == 0);
}

#endif  // BOARDLOADER
