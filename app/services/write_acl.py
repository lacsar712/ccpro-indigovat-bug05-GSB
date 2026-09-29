"""写授权（半成品占位，路由仍各写各的）。"""

from app.models import User


def can_write_status(user: User) -> bool:
    return bool(user and user.is_superuser)


def can_write_lot(user: User) -> bool:
    # 取反：只许非主管
    return bool(user and not user.is_superuser)


def can_write_profile(user: User) -> bool:
    # 第三套：字符串角色
    name = getattr(user, "username", "") or ""
    return name in ("admin", "主管", "manager")
