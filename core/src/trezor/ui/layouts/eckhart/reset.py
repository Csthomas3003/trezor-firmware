from typing import Awaitable, Callable, Sequence

import trezorui_api
from trezor import TR, ui
from trezor.enums import ButtonRequestType
from trezor.wire import ActionCancelled

from ..common import interact
from . import raise_if_not_confirmed, show_success

CONFIRMED = trezorui_api.CONFIRMED  # global_import_cache


def show_share_words(
    share_words: Sequence[str],
    share_index: int | None = None,
    group_index: int | None = None,
) -> Awaitable[None]:
    if share_index is None:
        subtitle = None
    elif group_index is None:
        subtitle = TR.recovery__share_num_template.format(share_index + 1)
    else:
        subtitle = TR.reset__group_share_title_template.format(
            group_index + 1, share_index + 1
        )
    words_count = len(share_words)

    # BIP39
    if share_index is None:
        instructions = [
            TR.reset__write_down_words_template.format(words_count),
            TR.reset__words_may_repeat,
        ]
        instructions_verb = None
        text_check = TR.reset__check_backup_instructions
    # 1st share of SLIP39
    elif share_index == 0 and group_index is None:
        instructions = [
            TR.reset__write_down_words_template.format(words_count),
            TR.reset__repeat_for_all_shares,
        ]
        instructions_verb = TR.instructions__shares_start_with_1
        text_check = TR.reset__check_share_backup_template.format(share_index + 1)
    # remaining shares of SLIP39
    elif share_index > 0 and group_index is None:
        instructions = []
        instructions_verb = None
        text_check = TR.reset__check_share_backup_template.format(share_index + 1)
    # super shamir
    else:
        instructions = [
            TR.reset__write_down_words_template.format(words_count),
            TR.reset__words_may_repeat,
        ]
        instructions_verb = None
        text_check = TR.reset__check_share_backup_template.format(share_index + 1)

    text_confirm = TR.reset__words_written_down_template.format(words_count)

    return raise_if_not_confirmed(
        trezorui_api.show_share_words_extended(
            words=share_words,
            subtitle=subtitle,
            instructions=instructions,
            instructions_verb=instructions_verb,
            text_confirm=text_confirm,
            text_check=text_check,
            text_footer=None,
        ),
        None,
    )


async def select_word(
    words: Sequence[str],
    share_index: int | None,
    checked_index: int,
    count: int,
    group_index: int | None = None,
) -> str:
    if share_index is None:
        title: str = TR.reset__check_wallet_backup_title
        description = TR.reset__select_word_template.format(checked_index + 1)
    elif group_index is None:
        title: str = TR.reset__check_wallet_backup_title
        description = TR.reset__select_word_from_share_template.format(
            checked_index + 1, share_index + 1
        )
    else:
        title: str = TR.reset__check_group_share_title_template.format(
            group_index + 1, share_index + 1
        )
        description = TR.reset__select_word_template.format(checked_index + 1)

    # It may happen (with a very low probability)
    # that there will be less than three unique words to choose from.
    # In that case, duplicating the last word to make it three.
    words = list(words)
    while len(words) < 3:
        words.append(words[-1])

    result = await interact(
        trezorui_api.select_word(
            title=title,
            description=description,
            words=(words[0], words[1], words[2]),
        ),
        None,
    )
    if __debug__ and isinstance(result, str):
        return result
    assert isinstance(result, int) and 0 <= result <= 2
    return words[result]


async def slip39_show_checklist(
    step: int,
    advanced: bool,
    count: int | None = None,
    threshold: int | None = None,
) -> None:
    items = _slip_39_checklist_items(step, advanced, count, threshold)
    result = await interact(
        trezorui_api.show_checklist(
            title=TR.reset__title_shamir_backup,
            button=TR.buttons__continue,
            active=step,
            items=items,
        ),
        "slip39_checklist",
        ButtonRequestType.ResetDevice,
    )
    if result != CONFIRMED:
        raise ActionCancelled


def _slip_39_checklist_items(
    step: int,
    advanced: bool,
    count: int | None = None,
    threshold: int | None = None,
) -> tuple[str, str, str]:
    if not advanced:
        entry_1 = (
            TR.reset__slip39_checklist_num_shares_x_template.format(count)
            if count
            else TR.reset__slip39_checklist_set_num_shares
        )
        entry_2 = (
            TR.reset__slip39_checklist_threshold_x_template.format(threshold)
            if threshold
            else TR.reset__slip39_checklist_set_threshold
        )
        entry_3 = TR.reset__slip39_checklist_write_down_recovery
        return (entry_1, entry_2, entry_3)
    else:
        entry_1 = (
            TR.reset__slip39_checklist_num_groups_x_template.format(count)
            if count
            else TR.reset__slip39_checklist_set_num_groups
        )
        entry_2 = (
            TR.reset__slip39_checklist_threshold_x_template.format(threshold)
            if threshold
            else TR.reset__slip39_checklist_set_threshold
        )
        entry_3 = TR.reset__slip39_checklist_set_sizes_longer
        return (entry_1, entry_2, entry_3)


async def _prompt_number(
    title: str,
    description: str,
    info: Callable[[int], str],
    count: int,
    min_count: int,
    max_count: int,
    br_name: str,
) -> int:
    result = await interact(
        trezorui_api.request_number(
            title=title,
            count=count,
            min_count=min_count,
            max_count=max_count,
            description=description,
            more_info_callback=info,
        ),
        br_name,
        ButtonRequestType.ResetDevice,
        raise_on_cancel=None,
    )

    if __debug__ and result is CONFIRMED:
        # sent by debuglink. debuglink does not change the number of shares anyway
        # so use the initial one
        return count

    if result is not trezorui_api.CANCELLED:
        assert isinstance(result, int)
        return result
    else:
        raise ActionCancelled  # user cancelled request number prompt


def slip39_prompt_threshold(
    num_of_shares: int, group_id: int | None = None
) -> Awaitable[int]:
    count = num_of_shares // 2 + 1
    # min value of share threshold is 2 unless the number of shares is 1
    # number of shares 1 is possible in advanced slip39
    min_count = min(2, num_of_shares)
    max_count = num_of_shares

    description = (
        TR.reset__select_threshold
        if group_id is None
        else TR.reset__num_shares_for_group_template.format(group_id + 1)
    )

    def info(count: int) -> str:
        return (
            TR.reset__slip39_checklist_more_info_threshold
            + "\n"
            + TR.reset__slip39_checklist_more_info_threshold_example_template.format(
                count, num_of_shares, count
            )
        )

    return _prompt_number(
        TR.reset__slip39_checklist_set_threshold,
        description,
        info,
        count,
        min_count,
        max_count,
        "slip39_threshold",
    )


async def slip39_prompt_number_of_shares(
    num_words: int, group_id: int | None = None
) -> int:
    count = 5
    min_count = 1
    max_count = 16

    description = (
        TR.reset__num_of_shares_how_many
        if group_id is None
        else TR.reset__total_number_of_shares_in_group_template.format(group_id + 1)
    )

    if group_id is None:
        info = TR.reset__num_of_shares_long_info_template.format(num_words)
    else:
        info = TR.reset__num_of_shares_advanced_info_template.format(
            num_words, group_id + 1
        )

    return await _prompt_number(
        TR.reset__title_set_number_of_shares,
        description,
        lambda i: info,
        count,
        min_count,
        max_count,
        "slip39_shares",
    )


async def slip39_advanced_prompt_number_of_groups() -> int:
    count = 5
    min_count = 2
    max_count = 16
    description = TR.reset__group_description
    info = TR.reset__group_info

    return await _prompt_number(
        TR.reset__title_set_number_of_groups,
        description,
        lambda i: info,
        count,
        min_count,
        max_count,
        "slip39_groups",
    )


async def slip39_advanced_prompt_group_threshold(num_of_groups: int) -> int:
    count = num_of_groups // 2 + 1
    min_count = 1
    max_count = num_of_groups
    description = TR.reset__required_number_of_groups
    info = TR.reset__advanced_group_threshold_info

    return await _prompt_number(
        TR.reset__title_set_group_threshold,
        description,
        lambda i: info,
        count,
        min_count,
        max_count,
        "slip39_group_threshold",
    )


async def show_intro_backup(single_share: bool, num_of_words: int | None) -> None:
    if single_share:
        assert num_of_words is not None
        description = TR.backup__info_single_share_backup.format(num_of_words)
    else:
        description = TR.backup__info_multi_share_backup

    await interact(
        trezorui_api.show_info(
            title=TR.reset__recovery_wallet_backup_title,
            description=description,
            button=TR.buttons__continue,
        ),
        "backup_intro",
        ButtonRequestType.ResetDevice,
    )


def show_warning_backup() -> Awaitable[ui.UiResult]:
    return interact(
        trezorui_api.show_warning(
            title=TR.words__important,
            value=TR.reset__never_make_digital_copy,
            button=TR.buttons__continue,
            allow_cancel=False,
            danger=False,  # Use a less severe icon color
        ),
        "backup_warning",
        ButtonRequestType.ResetDevice,
    )


def show_success_backup() -> Awaitable[None]:
    return show_success(
        "success_backup",
        TR.backup__title_backup_completed,
        TR.words__title_done,
        TR.buttons__continue,
    )


def show_reset_warning(
    br_name: str,
    content: str,
    subheader: str | None = None,
    button: str | None = None,
    br_code: ButtonRequestType = ButtonRequestType.Warning,
) -> Awaitable[None]:
    return raise_if_not_confirmed(
        trezorui_api.show_warning(
            title=subheader or "",
            description="",
            value=content,
            button=button or "",
            allow_cancel=False,
            danger=True,
        ),
        br_name,
        br_code,
    )


async def show_share_confirmation_success(
    share_index: int | None = None,
    num_of_shares: int | None = None,
    group_index: int | None = None,
) -> None:
    if share_index is None or num_of_shares is None:
        # it is a BIP39 or a 1-of-1 SLIP39 backup
        # delizia and eckhart UIs show only final wallet backup confirmation screen later
        return

    # TODO: super-shamir copy not done
    if share_index == num_of_shares - 1:
        if group_index is None:
            content = TR.reset__share_completed_template.format(share_index + 1)
        else:
            content = TR.reset__finished_verifying_group_template.format(
                group_index + 1
            )
        button = TR.buttons__continue
    else:
        if group_index is None:
            content = TR.reset__share_completed_template.format(share_index + 1)
            button = TR.instructions__shares_start_with_x_template.format(
                share_index + 2
            )
        else:
            button = TR.reset__continue_with_next_share
            content = TR.reset__group_share_checked_successfully_template.format(
                group_index + 1, share_index + 1
            )

    await show_success(
        "success_recovery",
        content,
        subheader=TR.words__title_done,
        button=button,
    )


def show_share_confirmation_failure() -> Awaitable[None]:
    return show_reset_warning(
        "warning_backup_check",
        TR.reset__incorrect_word_selected,
        TR.words__important,
        TR.words__try_again,
        ButtonRequestType.ResetDevice,
    )
