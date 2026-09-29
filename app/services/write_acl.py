"""还原台写授权判定模块。

改状态、登记浸染、染缸字段（缸容/染种）保存三处写路径统一调用本模块，
不再各自按 is_superuser / 用户名字符串各判一套。

角色矩阵（主管 admin / 染缸工 worker 均可写全部三条路径）：

| 角色        | 改状态 | 登记浸染 | 改缸容/染种 |
|-------------|:------:|:--------:|:-----------:|
| 主管        |   ✓    |    ✓     |      ✓      |
| 染缸工      |   ✓    |    ✓     |      ✓      |
| 未登录/匿名 |   ✗    |    ✗     |      ✗      |

判定失败只抛 WriteDeniedError，绝不清理会话——写失败不得误伤浏览，
用户仍可打开还原台。
"""

from enum import Enum

from app.models import User


class Role(str, Enum):
    SUPERVISOR = "supervisor"  # 主管（admin，is_superuser=True）
    WORKER = "worker"          # 染缸工（worker，is_superuser=False）


# 写操作标识
WRITE_STATUS = "status"    # 改染缸状态
WRITE_LOT = "lot"          # 登记浸染批次
WRITE_PROFILE = "profile"  # 改缸容 / 染种

_ACTION_LABELS = {
    WRITE_STATUS: "改状态",
    WRITE_LOT: "登记浸染",
    WRITE_PROFILE: "改缸资料",
}

# 角色矩阵：三种写操作主管、染缸工均放行
WRITE_MATRIX: dict[str, frozenset[Role]] = {
    WRITE_STATUS: frozenset({Role.SUPERVISOR, Role.WORKER}),
    WRITE_LOT: frozenset({Role.SUPERVISOR, Role.WORKER}),
    WRITE_PROFILE: frozenset({Role.SUPERVISOR, Role.WORKER}),
}


class WriteDeniedError(PermissionError):
    """写授权不通过。仅表示拒绝写入，不携带任何清会话副作用。"""

    def __init__(self, action: str):
        self.action = action
        label = _ACTION_LABELS.get(action, action)
        super().__init__(f"无权限{label}")


def role_of(user: User | None) -> Role | None:
    """识别现场角色；未登录/匿名用户返回 None。"""
    if not isinstance(user, User):
        return None
    return Role.SUPERVISOR if user.is_superuser else Role.WORKER


def can_write(user: User | None, action: str) -> bool:
    """统一写授权判定：按角色矩阵查该写操作是否放行。"""
    role = role_of(user)
    if role is None:
        return False
    allowed = WRITE_MATRIX.get(action)
    return bool(allowed and role in allowed)


def require_write(user: User | None, action: str) -> None:
    """授权不通过时抛 WriteDeniedError（不登录出、不清会话）。"""
    if not can_write(user, action):
        raise WriteDeniedError(action)


def can_write_status(user: User | None) -> bool:
    return can_write(user, WRITE_STATUS)


def can_write_lot(user: User | None) -> bool:
    return can_write(user, WRITE_LOT)


def can_write_profile(user: User | None) -> bool:
    return can_write(user, WRITE_PROFILE)
