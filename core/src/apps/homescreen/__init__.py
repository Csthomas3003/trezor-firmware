from typing import Coroutine

import storage
import storage.cache
import storage.device
import trezorui_api
from trezor import config, utils, wire
from trezor.enums import MessageType
from trezor.ui.layouts.homescreen import Busyscreen, Homescreen, Lockscreen

from apps.base import busy_expiry_ms, lock_device
from apps.common.authorization import is_set_any_session


async def busyscreen() -> None:
    obj = Busyscreen(busy_expiry_ms())
    try:
        await obj.get_result()
    finally:
        obj.__del__()


async def homescreen() -> None:
    obj = _create_homescreen_obj()
    try:
        res = await obj.get_result()
    finally:
        obj.__del__()

    await _handle_device_menu(res)
    lock_device()


async def _lockscreen(screensaver: bool = False) -> None:
    from apps.base import unlock_device
    from apps.common.request_pin import can_lock_device

    # Only show the lockscreen UI if the device can in fact be locked, or if it is
    # and OLED device (in which case the lockscreen is a screensaver).
    if can_lock_device() or screensaver:
        obj = _create_lockscreen_obj()
        try:
            await obj.get_result()
        finally:
            obj.__del__()
    # Otherwise proceed directly to unlock() call. If the device is already unlocked,
    # it should be a no-op storage-wise, but it resets the internal configuration
    # to an unlocked state.
    try:
        await unlock_device()
    except wire.PinCancelled:
        pass


def lockscreen() -> Coroutine[None, None, None]:
    return _lockscreen()


def screensaver() -> Coroutine[None, None, None]:
    return _lockscreen(screensaver=True)


if utils.USE_POWER_MANAGER:

    async def _chargingscreen() -> None:
        """Show lockscreen/homescreen for 4 seconds when waking up from power event.

        If user interacts within the timeout, proceed with normal unlock flow.
        If timeout occurs, return to suspend.
        """
        from trezor import loop

        from apps.base import unlock_device
        from apps.common.request_pin import can_lock_device

        if can_lock_device():
            obj = _create_lockscreen_obj()
        else:
            obj = _create_homescreen_obj()

        try:
            # Race between user interaction and timeout
            result = await loop.race(obj.get_result(), loop.sleep(4000))

            if isinstance(result, int):  # sleep() returns an int (deadline)
                # Timeout occurred - go back to suspend
                from apps.base import suspend_device

                suspend_device()
                return

            # Proceed with user interaction
            await _handle_device_menu(result)
            try:
                await unlock_device()
            except wire.PinCancelled:
                pass

        finally:
            obj.__del__()

    def chargingscreen() -> Coroutine[None, None, None]:
        return _chargingscreen()


def _get_homescreen_notification() -> tuple[str | None, int]:
    """Get notification text and level for homescreen display."""
    from trezor import TR

    notification = None
    notification_level = 1  # 0 = strong warning, 1 = warning, 2 = info, 3 = success

    if is_set_any_session(MessageType.AuthorizeCoinJoin):
        notification = TR.homescreen__title_coinjoin_authorized
        notification_level = 3
    elif storage.device.is_initialized() and storage.device.no_backup():
        notification = TR.homescreen__title_seedless
        notification_level = 0
    elif storage.device.is_initialized() and storage.device.unfinished_backup():
        notification = TR.homescreen__title_backup_failed
        notification_level = 0
    elif storage.device.is_initialized() and storage.device.needs_backup():
        notification = TR.homescreen__title_backup_needed
        notification_level = 1
    elif storage.device.is_initialized() and not config.has_pin():
        notification = TR.homescreen__title_pin_not_set
        notification_level = 1
    elif storage.device.get_experimental_features():
        notification = TR.homescreen__title_experimental_mode
        notification_level = 2

    return notification, notification_level


def _create_homescreen_obj() -> Homescreen:
    """Create a Homescreen object with current device state."""
    if storage.device.is_initialized():
        label = storage.device.get_label()
    else:
        label = None

    notification, notification_level = _get_homescreen_notification()

    return Homescreen(
        label=label,
        notification=notification,
        notification_level=notification_level,
        lockable=config.has_pin(),
    )


def _create_lockscreen_obj() -> Lockscreen:
    """Create a Lockscreen object with current device state."""
    return Lockscreen(
        label=storage.device.get_label(),
        coinjoin_authorized=is_set_any_session(MessageType.AuthorizeCoinJoin),
    )


async def _handle_device_menu(result: trezorui_api.UiResult) -> None:
    """Handle the result from homescreen/lockscreen interaction."""
    if utils.INTERNAL_MODEL == "T3W1" and result is trezorui_api.INFO:
        from .device_menu import handle_device_menu

        return await handle_device_menu()
