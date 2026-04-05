import pytest

from app.switchboard import Switchboard
from app.users import ForeignUser, LocalUser


def test_register_call_creates_local_and_foreign_users() -> None:
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
    )

    assert isinstance(active_call.caller, LocalUser)
    assert isinstance(active_call.receiver, ForeignUser)
    assert active_call.caller.id == 1
    assert active_call.receiver.id == 2


def test_register_call_counts_active_calls() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,Petr Petrov,+78880000000"
    )
    switchboard.register_call(
        "3,John Smith,+15551234567,4,Jane Doe,+33123456789"
    )

    assert switchboard.get_active_calls_count() == 2


def test_register_call_counts_calls_between_local_and_foreign_users() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
    )
    switchboard.register_call(
        "3,Petr Petrov,+78880000000,4,Maria Petrova,+79991112233"
    )
    switchboard.register_call(
        "5,Jane Doe,+33123456789,6,Alex Doe,+442012345678"
    )

    assert switchboard.get_active_calls_count() == 3
    assert switchboard.get_cross_border_calls_count() == 1


def test_initial_state_is_zero() -> None:
    switchboard = Switchboard()

    assert switchboard.get_active_calls_count() == 0
    assert switchboard.get_cross_border_calls_count() == 0


@pytest.mark.parametrize("caller_phone, receiver_phone, expected_cross_border", [
    ("+79990000000", "+78880000000", False),
    ("+15551234567", "+33123456789", False),
    ("+79990000000", "+15551234567", True),
    ("+15551234567", "+79990000000", True),
])
def test_register_call_is_cross_border(
    caller_phone: str, receiver_phone: str, expected_cross_border: bool
) -> None:
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        f"1,Ivan Ivanov,{caller_phone},2,John Smith,{receiver_phone}"
    )

    assert active_call.is_cross_border == expected_cross_border
    assert switchboard.get_cross_border_calls_count() == (1 if expected_cross_border else 0)


def test_register_call_strips_whitespace() -> None:
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        "  1  ,  Ivan Ivanov  ,  +79990000000  ,  2  ,  John Smith  ,  +15551234567  "
    )

    assert active_call.caller.id == 1
    assert active_call.caller.fullname == "Ivan Ivanov"
    assert active_call.caller.phone == "+79990000000"
    assert active_call.receiver.id == 2


def test_register_call_raises_on_wrong_fields_count() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError, match="Expected 6 fields"):
        switchboard.register_call("1,Ivan Ivanov,+79990000000")

    with pytest.raises(ValueError, match="Expected 6 fields"):
        switchboard.register_call("")


@pytest.mark.parametrize("raw_call, match", [
    ("abc,Ivan Ivanov,+79990000000,2,John Smith,+15551234567", "User id must be an integer"),
    ("1,Ivan Ivanov,+79990000000,abc,John Smith,+15551234567", "User id must be an integer"),
])
def test_register_call_raises_on_non_numeric_id(raw_call: str, match: str) -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError, match=match):
        switchboard.register_call(raw_call)


@pytest.mark.parametrize("phone", [
    "79990000000",
    "+7AAA000000",
    "+1234567890123456",
    "+123456",
    "+abc1234567",
])
def test_register_call_raises_on_invalid_phone_format(phone: str) -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError, match="Invalid phone number format"):
        switchboard.register_call(
            f"1,Ivan Ivanov,{phone},2,John Smith,+15551234567"
        )


def test_register_call_id_is_stored_as_int() -> None:
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        "42,Ivan Ivanov,+79990000000,99,John Smith,+15551234567"
    )

    assert isinstance(active_call.caller.id, int)
    assert active_call.caller.id == 42
    assert isinstance(active_call.receiver.id, int)
    assert active_call.receiver.id == 99


@pytest.mark.parametrize("raw_call", [
    "1,,+79990000000,2,John Smith,+15551234567",
    "1,Ivan Ivanov,+79990000000,2,,+15551234567",
])
def test_register_call_raises_on_empty_name(raw_call: str) -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError, match="User fullname cannot be empty"):
        switchboard.register_call(raw_call)
