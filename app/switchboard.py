from __future__ import annotations

import re
from dataclasses import dataclass

from app.users import User, LocalUser, ForeignUser


LOCAL_PHONE_PREFIX = "+7"
_PHONE_RE = re.compile(r'\+\d{7,15}')


@dataclass(slots=True)
class ActiveCall:
    caller: User
    receiver: User

    @property
    def is_cross_border(self) -> bool:
        return type(self.caller) is not type(self.receiver)


class Switchboard:
    def __init__(self) -> None:
        self._active_calls: list[ActiveCall] = []
        self._cross_border_calls_count: int = 0

    def register_call(self, raw_call: str) -> ActiveCall:
        '''
        Метод должен принимать только 1 строку и возвращать класс ActiveCall.
        На входе строка должна быть вида "caller_id,caller_name,caller_phone,receiver_id,receiver_name,receiver_phone"

        Например: "1001,Иван Петров,+71234567890,1085,Адам Яковлев,+71255556666"
        '''
        parts = [p.strip() for p in raw_call.split(",")]
        if len(parts) != 6:
            raise ValueError(f"Expected 6 fields, got {len(parts)}")

        caller_id, caller_name, caller_phone, receiver_id, receiver_name, receiver_phone = parts

        caller = self._create_user(caller_id, caller_name, caller_phone)
        receiver = self._create_user(receiver_id, receiver_name, receiver_phone)

        active_call = ActiveCall(caller, receiver)
        self._active_calls.append(active_call)

        if active_call.is_cross_border:
            self._cross_border_calls_count += 1

        return active_call

    @staticmethod
    def _create_user(user_id: str, fullname: str, phone: str) -> User:
        try:
            uid = int(user_id)
        except ValueError:
            raise ValueError(f"User id must be an integer, got: '{user_id}'")

        if not _PHONE_RE.fullmatch(phone):
            raise ValueError(f"Invalid phone number format: '{phone}'")

        if phone.startswith(LOCAL_PHONE_PREFIX):
            return LocalUser(uid, fullname, phone)
        return ForeignUser(uid, fullname, phone)

    def get_active_calls_count(self) -> int:
        return len(self._active_calls)

    def get_cross_border_calls_count(self) -> int:
        return self._cross_border_calls_count
