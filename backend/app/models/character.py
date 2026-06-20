"""
角色（用户）库模型 - 面向加密货币交易所场景

角色代表交易所的真实/虚拟用户，数据来源于 KYC 与交易行为。
与"种子文档"解耦：角色可独立创建、编辑、上传、删除，
并在运行模拟时按需挑选进入某个推演世界。

存储：全局库，持久化为单个 JSON 文件，便于增删改查。
"""

import os
import csv
import io
import json
import uuid
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict

from ..config import Config


# 列表型字段（导入时按分隔符拆分）
_LIST_FIELDS = {"preferred_assets", "tags", "activity_ids"}
# 整数型字段
_INT_FIELDS = {"vip_level", "orders_30d", "orders_90d", "positions", "activities_90d"}
# 浮点型字段（金额 / 交易量；导入时去除千分位逗号）
_FLOAT_FIELDS = {"volume_30d", "volume_90d", "fees_30d", "fees_90d", "rewards_claimed"}
# 布尔型字段
_BOOL_FIELDS = {"enabled", "zep_enrich"}

# CSV/TSV/JSON 导入时的表头同义词映射 -> 标准字段名。
# 同时支持交易所导出的中文表头与英文 snake_case，方便直接粘贴原始数据。
_IMPORT_ALIASES = {
    # 账户 / 身份
    "uid": "uid", "user_id": "uid", "用户id": "uid", "用户uid": "uid",
    "name": "name", "用户名": "name", "nickname": "name",
    "region": "region", "secondary_region": "region", "二级区域": "region", "地区": "region",
    "user_source": "user_source", "registration_source": "user_source",
    "channel": "user_source", "用户来源": "user_source", "来源": "user_source",
    "registered_at": "registered_at", "registration_time": "registered_at",
    "register_time": "registered_at", "reg_time": "registered_at", "注册时间": "registered_at",
    "vip_level": "vip_level", "vip": "vip_level", "vip_tier": "vip_level",
    "vip等级": "vip_level", "vip_等级": "vip_level",
    # 交易行为（近 30 / 90 天）
    "orders_30d": "orders_30d", "order_count_30d": "orders_30d", "近30天交易订单数": "orders_30d",
    "orders_90d": "orders_90d", "order_count_90d": "orders_90d", "近90天交易订单数": "orders_90d",
    "volume_30d": "volume_30d", "trading_volume_30d": "volume_30d", "近30天交易量": "volume_30d",
    "volume_90d": "volume_90d", "trading_volume_90d": "volume_90d", "近90天交易量": "volume_90d",
    "fees_30d": "fees_30d", "trading_fees_30d": "fees_30d", "fee_30d": "fees_30d", "近30天交易手续费": "fees_30d",
    "fees_90d": "fees_90d", "trading_fees_90d": "fees_90d", "fee_90d": "fees_90d", "近90天交易手续费": "fees_90d",
    "main_product": "main_product", "primary_product": "main_product", "product": "main_product", "主要交易产品": "main_product",
    "main_coin": "main_coin", "primary_coin": "main_coin", "main_symbol": "main_coin",
    "symbol": "main_coin", "coin": "main_coin", "主要交易币种": "main_coin",
    "positions": "positions", "position_count": "positions", "holdings": "positions", "持仓": "positions",
    # 活动参与
    "activities_90d": "activities_90d", "activity_count_90d": "activities_90d", "近90天参与活动数": "activities_90d",
    "activity_ids": "activity_ids", "activity_id": "activity_ids", "近90天参与活动id": "activity_ids",
    "rewards_claimed": "rewards_claimed", "reward_amount": "rewards_claimed",
    "rewards": "rewards_claimed", "claimed_rewards": "rewards_claimed", "领取奖励金额": "rewards_claimed",
    # 分析 / 人设（可选，用于驱动模拟）
    "risk_type": "risk_type", "risk": "risk_type", "risk_appetite": "risk_type", "risk_tolerance": "risk_type",
    "preferred_assets": "preferred_assets", "assets": "preferred_assets", "favorite_assets": "preferred_assets",
    "bio": "bio", "description": "bio",
    "persona": "persona", "persona_text": "persona",
    # 其他
    "tags": "tags", "tag": "tags",
    "trading_history": "trading_history", "history": "trading_history",
    "zep_enrich": "zep_enrich",
    "enabled": "enabled", "active": "enabled",
}


@dataclass
class Character:
    """加密货币交易所用户角色数据模型（字段对齐交易所真实导出数据）"""
    character_id: str
    name: str
    created_at: str
    updated_at: str

    source: str = "manual"            # manual | uploaded | extracted
    enabled: bool = True
    tags: List[str] = field(default_factory=list)

    # 账户 / 身份
    uid: Optional[str] = None             # 交易所用户 UID
    region: Optional[str] = None          # 二级区域
    user_source: Optional[str] = None     # 用户来源（注册渠道）
    registered_at: Optional[str] = None   # 注册时间
    vip_level: Optional[int] = None       # VIP 等级

    # 交易行为（近 30 / 90 天）
    orders_30d: Optional[int] = None      # 近30天交易订单数
    orders_90d: Optional[int] = None      # 近90天交易订单数
    volume_30d: Optional[float] = None    # 近30天交易量
    volume_90d: Optional[float] = None    # 近90天交易量
    fees_30d: Optional[float] = None      # 近30天交易手续费
    fees_90d: Optional[float] = None      # 近90天交易手续费
    main_product: Optional[str] = None    # 主要交易产品
    main_coin: Optional[str] = None       # 主要交易币种
    positions: Optional[int] = None       # 持仓

    # 活动参与（近 90 天）
    activities_90d: Optional[int] = None  # 近90天参与活动数
    activity_ids: List[str] = field(default_factory=list)  # 近90天参与活动id
    rewards_claimed: Optional[float] = None  # 领取奖励金额

    # 分析 / 人设（可选，用于驱动模拟）
    preferred_assets: List[str] = field(default_factory=list)
    risk_type: Optional[str] = None
    bio: Optional[str] = None
    persona: Optional[str] = None

    # Zep 可选记忆增强层
    zep_enrich: bool = False
    trading_history: Optional[str] = None
    zep_graph_id: Optional[str] = None

    # 上传时未识别的额外列
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        clean = {k: v for k, v in data.items() if k in known}
        # 兜底必需字段
        clean.setdefault("character_id", f"char_{uuid.uuid4().hex[:12]}")
        # 无显式名称时用 UID 兜底（交易所数据通常仅有 uid）
        if not clean.get("name"):
            uid = clean.get("uid")
            clean["name"] = f"User {uid}" if uid not in (None, "") else "Unnamed User"
        now = datetime.now().isoformat()
        clean.setdefault("created_at", now)
        clean.setdefault("updated_at", now)
        return cls(**clean)

    @staticmethod
    def _fmt_num(value: Any) -> str:
        """格式化数值：整数去掉小数点，浮点保留紧凑形式并加千分位。"""
        try:
            f = float(value)
        except (TypeError, ValueError):
            return str(value)
        if f == int(f):
            return f"{int(f):,}"
        return f"{f:,.2f}"

    def compose_persona(self) -> str:
        """根据交易所行为字段拼装一段可读的人设文本（当 persona 为空时使用）。

        既用于界面展示，也作为后续构建 OASIS profile 的基础。
        """
        if self.persona and self.persona.strip():
            return self.persona

        parts: List[str] = []

        # 身份：地区 + 主要产品 + VIP 等级 + 注册渠道/时间
        product = self.main_product or "crypto"
        intro = f"{self.name} is a"
        if self.region:
            intro += f" {self.region}"
        intro += f" {product} trader on the exchange"
        if self.vip_level is not None:
            intro += f" (VIP level {self.vip_level})"
        if self.registered_at:
            via = f" via {self.user_source}" if self.user_source else ""
            intro += f", who registered{via} on {self.registered_at}"
        elif self.user_source:
            intro += f", who joined via {self.user_source}"
        parts.append(intro + ".")

        # 近 30 / 90 天交易行为
        activity: List[str] = []
        seg30 = []
        if self.orders_30d is not None:
            seg30.append(f"{self._fmt_num(self.orders_30d)} orders")
        if self.volume_30d is not None:
            seg30.append(f"a trading volume of {self._fmt_num(self.volume_30d)}")
        if self.fees_30d is not None:
            seg30.append(f"{self._fmt_num(self.fees_30d)} in fees")
        if seg30:
            activity.append("over the last 30 days they made " + ", ".join(seg30))
        seg90 = []
        if self.orders_90d is not None:
            seg90.append(f"{self._fmt_num(self.orders_90d)} orders")
        if self.volume_90d is not None:
            seg90.append(f"{self._fmt_num(self.volume_90d)} volume")
        if self.fees_90d is not None:
            seg90.append(f"{self._fmt_num(self.fees_90d)} in fees")
        if seg90:
            activity.append("over 90 days, " + ", ".join(seg90))
        if activity:
            parts.append("In terms of activity, " + "; ".join(activity) + ".")

        # 主要币种 / 持仓
        if self.main_coin:
            parts.append(f"Their most-traded instrument is {self.main_coin}.")
        if self.positions is not None:
            parts.append(f"They currently hold {self._fmt_num(self.positions)} open positions.")

        # 活动参与 / 奖励
        if self.activities_90d is not None:
            s = f"In the last 90 days they joined {self._fmt_num(self.activities_90d)} exchange promotions"
            if self.rewards_claimed is not None:
                s += f" and claimed {self._fmt_num(self.rewards_claimed)} in rewards"
            parts.append(s + ".")

        if self.risk_type:
            parts.append(f"Risk profile: {self.risk_type}.")

        return " ".join(parts)


class CharacterManager:
    """角色库管理器 - 负责全局角色库的持久化与检索"""

    LIBRARY_DIR = os.path.join(Config.UPLOAD_FOLDER, "characters")
    LIBRARY_FILE = os.path.join(LIBRARY_DIR, "characters.json")

    _lock = threading.Lock()

    @classmethod
    def _ensure_dir(cls) -> None:
        os.makedirs(cls.LIBRARY_DIR, exist_ok=True)

    @classmethod
    def _load_all(cls) -> List[Dict[str, Any]]:
        if not os.path.exists(cls.LIBRARY_FILE):
            return []
        try:
            with open(cls.LIBRARY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    @classmethod
    def _save_all(cls, items: List[Dict[str, Any]]) -> None:
        cls._ensure_dir()
        tmp_path = cls.LIBRARY_FILE + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, cls.LIBRARY_FILE)

    @classmethod
    def list_characters(
        cls,
        query: Optional[str] = None,
        tag: Optional[str] = None,
        enabled: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int, List[str]]:
        """返回 (当前页角色, 过滤后总数, 库内全部标签)"""
        items = cls._load_all()

        all_tags = sorted({t for it in items for t in (it.get("tags") or [])})

        if query:
            q = query.lower()
            def _match(it: Dict[str, Any]) -> bool:
                haystack = " ".join(str(it.get(k, "")) for k in
                                    ("name", "uid", "region", "main_product", "main_coin", "risk_type"))
                haystack += " " + " ".join(it.get("preferred_assets") or [])
                return q in haystack.lower()
            items = [it for it in items if _match(it)]

        if tag:
            items = [it for it in items if tag in (it.get("tags") or [])]

        if enabled is not None:
            items = [it for it in items if bool(it.get("enabled", True)) == enabled]

        total = len(items)
        # 最近更新的排在前面
        items.sort(key=lambda it: it.get("updated_at", ""), reverse=True)
        page = items[offset: offset + limit] if limit > 0 else items[offset:]
        return page, total, all_tags

    @classmethod
    def get_character(cls, character_id: str) -> Optional[Dict[str, Any]]:
        for it in cls._load_all():
            if it.get("character_id") == character_id:
                return it
        return None

    @classmethod
    def create_character(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now().isoformat()
        payload = dict(data)
        payload["character_id"] = f"char_{uuid.uuid4().hex[:12]}"
        payload["created_at"] = now
        payload["updated_at"] = now
        payload.setdefault("source", "manual")
        character = Character.from_dict(payload)
        with cls._lock:
            items = cls._load_all()
            items.append(character.to_dict())
            cls._save_all(items)
        return character.to_dict()

    @classmethod
    def update_character(cls, character_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with cls._lock:
            items = cls._load_all()
            for idx, it in enumerate(items):
                if it.get("character_id") == character_id:
                    merged = {**it, **data}
                    merged["character_id"] = character_id
                    merged["created_at"] = it.get("created_at")
                    merged["updated_at"] = datetime.now().isoformat()
                    character = Character.from_dict(merged)
                    items[idx] = character.to_dict()
                    cls._save_all(items)
                    return items[idx]
        return None

    @classmethod
    def delete_character(cls, character_id: str) -> bool:
        with cls._lock:
            items = cls._load_all()
            new_items = [it for it in items if it.get("character_id") != character_id]
            if len(new_items) == len(items):
                return False
            cls._save_all(new_items)
        return True

    @classmethod
    def import_characters(
        cls,
        rows: List[Dict[str, Any]],
        source: str = "uploaded",
    ) -> int:
        """批量导入角色（已归一化的行字典列表）。返回成功导入数量。"""
        now = datetime.now().isoformat()
        created: List[Dict[str, Any]] = []
        for raw in rows:
            mapped = cls._map_import_row(raw)
            if not mapped.get("name"):
                continue
            mapped["character_id"] = f"char_{uuid.uuid4().hex[:12]}"
            mapped["created_at"] = now
            mapped["updated_at"] = now
            mapped.setdefault("source", source)
            created.append(Character.from_dict(mapped).to_dict())

        if not created:
            return 0

        with cls._lock:
            items = cls._load_all()
            items.extend(created)
            cls._save_all(items)
        return len(created)

    @classmethod
    def export_characters(cls) -> List[Dict[str, Any]]:
        return cls._load_all()

    # ---------- 导入辅助 ----------

    @staticmethod
    def _normalize_header(header: str) -> str:
        return header.strip().lower().replace(" ", "_").replace("-", "_")

    @classmethod
    def _map_import_row(cls, raw: Dict[str, Any]) -> Dict[str, Any]:
        """把任意来源的一行映射为标准 Character 字段；未识别列存入 extra。"""
        mapped: Dict[str, Any] = {}
        extra: Dict[str, Any] = {}

        for key, value in raw.items():
            if key is None:
                continue
            norm = cls._normalize_header(str(key))
            field_name = _IMPORT_ALIASES.get(norm)
            if field_name is None:
                if value not in (None, ""):
                    extra[str(key)] = value
                continue
            mapped[field_name] = cls._coerce_value(field_name, value)

        # 交易所数据通常只有 uid 而无姓名：用 uid 兜底名称
        if not mapped.get("name") and mapped.get("uid") not in (None, ""):
            mapped["name"] = f"User {mapped['uid']}"
        # 主要交易币种自动填入偏好资产（用于模拟话题）
        if not mapped.get("preferred_assets") and mapped.get("main_coin"):
            mapped["preferred_assets"] = [mapped["main_coin"]]

        if extra:
            mapped["extra"] = extra
        return mapped

    @staticmethod
    def _coerce_value(field_name: str, value: Any) -> Any:
        if value is None:
            return None
        if field_name in _LIST_FIELDS:
            if isinstance(value, list):
                return [str(v).strip() for v in value if str(v).strip()]
            parts = str(value).replace(";", ",").replace("|", ",").split(",")
            return [p.strip() for p in parts if p.strip()]
        if field_name in _INT_FIELDS:
            try:
                # 去除千分位逗号（如 "1,457"）后再解析
                return int(float(str(value).replace(",", "").strip()))
            except (ValueError, TypeError):
                return None
        if field_name in _FLOAT_FIELDS:
            try:
                return float(str(value).replace(",", "").strip())
            except (ValueError, TypeError):
                return None
        if field_name in _BOOL_FIELDS:
            if isinstance(value, bool):
                return value
            return str(value).strip().lower() in ("1", "true", "yes", "y", "on", "enabled", "active")
        return str(value).strip() if not isinstance(value, (dict,)) else value

    @classmethod
    def parse_csv(cls, content: str) -> List[Dict[str, Any]]:
        """解析 CSV/TSV 文本为原始行字典列表（表头保持原样，映射在导入时进行）。

        自动识别分隔符：含制表符时按 TSV 解析（交易所导出常为制表符分隔，
        且数值带千分位逗号，无法用逗号分隔）。
        """
        content = content.lstrip("\ufeff")
        first_line = next((ln for ln in content.splitlines() if ln.strip()), "")
        delimiter = "\t" if "\t" in first_line else ","
        reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
        return [dict(row) for row in reader]
