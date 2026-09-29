"""三条写路径统一的授权判定。

改状态、登记浸染、改缸容/染种都必须调用本模块，路由不得各写各的角色判断。

角色矩阵（与 app/seed.py 账号一致）：

                         改状态  登记浸染  改缸容/染种
  主管   is_superuser       ✓      ✓         ✓
  染缸工 is_superuser=False ✓      ✓         ✓
  匿名 / 未登录              ✗      ✗         ✗

注意：判定为 False 只表示拒绝本次写入，调用方不得据此清除会话——
写失败后会话保持，用户仍应能打开还原台浏览。
"""

from app.models import User

# 三类写操作
STATUS = "status"    # 改缸状态
LOT = "lot"          # 登记浸染批次
PROFILE = "profile"  # 改缸容 / 染种

# 角色
ROLE_SUPERVISOR = "supervisor"  # 主管
ROLE_DYEWORKER = "dyeworker"    # 染缸工
ROLE_ANONYMOUS = "anonymous"    # 未登录

# 角色 × 写操作 授权矩阵
_WRITE_MATRIX: dict[str, frozenset[str]] = {
    ROLE_SUPERVISOR: frozenset({STATUS, LOT, PROFILE}),
    ROLE_DYEWORKER: frozenset({STATUS, LOT, PROFILE}),
    ROLE_ANONYMOUS: frozenset(),
}

# 各写路径被拒时给现场看的提示
DENIED_MESSAGES = {
    STATUS: "无权限改状态：仅主管或染缸工可操作。",
    LOT: "无权限登记浸染：仅主管或染缸工可操作。",
    PROFILE: "无权限改缸容或染种：仅主管或染缸工可操作。",
}


def role_of(user: User | None) -> str:
    """把登录账号归一化为矩阵里的角色；未登录即匿名。"""
    if user is None:
        return ROLE_ANONYMOUS
    return ROLE_SUPERVISOR if user.is_superuser else ROLE_DYEWORKER


def can_write(user: User | None, action: str) -> bool:
    """唯一授权结论入口：某角色能否执行某条写路径，以矩阵为准。"""
    return action in _WRITE_MATRIX[role_of(user)]


def can_write_status(user: User | None) -> bool:
    return can_write(user, STATUS)


def can_write_lot(user: User | None) -> bool:
    return can_write(user, LOT)


def can_write_profile(user: User | None) -> bool:
    return can_write(user, PROFILE)
