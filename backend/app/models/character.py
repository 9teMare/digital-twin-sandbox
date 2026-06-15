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
_LIST_FIELDS = {"preferred_assets", "tags"}
# 整数型字段
_INT_FIELDS = {"age"}
# 布尔型字段
_BOOL_FIELDS = {"enabled", "zep_enrich"}

# CSV/JSON 导入时的表头同义词映射 -> 标准字段名
_IMPORT_ALIASES = {
    # 身份 / KYC
    "name": "name", "full_name": "name", "fullname": "name",
    "age": "age",
    "gender": "gender", "sex": "gender",
    "occupation": "occupation", "job": "occupation", "profession": "occupation",
    "jurisdiction": "jurisdiction", "country": "jurisdiction", "region": "jurisdiction", "residence": "jurisdiction",
    "source_of_income": "source_of_income", "income_source": "source_of_income",
    "income_band": "income_band", "annual_income": "income_band", "income": "income_band",
    "net_worth_band": "net_worth_band", "net_worth": "net_worth_band", "networth": "net_worth_band",
    "kyc_tier": "kyc_tier", "kyc_level": "kyc_tier", "kyc": "kyc_tier",
    # 风险 / 意图
    "risk_type": "risk_type", "risk": "risk_type", "risk_appetite": "risk_type", "risk_tolerance": "risk_type",
    "purpose": "purpose", "purpose_of_using_exchange": "purpose", "use_purpose": "purpose", "goal": "purpose",
    "experience_level": "experience_level", "experience": "experience_level", "trading_experience": "experience_level",
    # 交易行为
    "preferred_assets": "preferred_assets", "assets": "preferred_assets", "favorite_assets": "preferred_assets",
    "avg_position_size": "avg_position_size", "position_size": "avg_position_size", "average_position_size": "avg_position_size",
    "trading_frequency": "trading_frequency", "frequency": "trading_frequency",
    "holding_style": "holding_style", "holding_period": "holding_style", "trader_type": "holding_style",
    "leverage_usage": "leverage_usage", "leverage": "leverage_usage",
    "derivatives_usage": "derivatives_usage", "derivatives": "derivatives_usage",
    "reaction_to_volatility": "reaction_to_volatility", "volatility_reaction": "reaction_to_volatility",
    "deposit_withdrawal_pattern": "deposit_withdrawal_pattern", "deposit_pattern": "deposit_withdrawal_pattern", "withdrawal_pattern": "deposit_withdrawal_pattern",
    # 心理 / 人设
    "sentiment_bias": "sentiment_bias", "sentiment": "sentiment_bias", "bias": "sentiment_bias",
    "fomo_susceptibility": "fomo_susceptibility", "fomo": "fomo_susceptibility",
    "social_influence": "social_influence", "influence": "social_influence",
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
    """加密货币交易所用户角色数据模型"""
    character_id: str
    name: str
    created_at: str
    updated_at: str

    source: str = "manual"            # manual | uploaded | extracted
    enabled: bool = True
    tags: List[str] = field(default_factory=list)

    # 身份 / KYC
    age: Optional[int] = None
    gender: Optional[str] = None       # male | female | other
    occupation: Optional[str] = None
    jurisdiction: Optional[str] = None
    source_of_income: Optional[str] = None
    income_band: Optional[str] = None
    net_worth_band: Optional[str] = None
    kyc_tier: Optional[str] = None

    # 风险 / 意图
    risk_type: Optional[str] = None
    purpose: Optional[str] = None
    experience_level: Optional[str] = None

    # 交易行为
    preferred_assets: List[str] = field(default_factory=list)
    avg_position_size: Optional[str] = None
    trading_frequency: Optional[str] = None
    holding_style: Optional[str] = None
    leverage_usage: Optional[str] = None
    derivatives_usage: Optional[str] = None
    reaction_to_volatility: Optional[str] = None
    deposit_withdrawal_pattern: Optional[str] = None

    # 心理 / 人设
    sentiment_bias: Optional[str] = None
    fomo_susceptibility: Optional[str] = None
    social_influence: Optional[str] = None
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
        clean.setdefault("name", "Unnamed User")
        now = datetime.now().isoformat()
        clean.setdefault("created_at", now)
        clean.setdefault("updated_at", now)
        return cls(**clean)

    def compose_persona(self) -> str:
        """根据结构化字段拼装一段可读的人设文本（当 persona 为空时使用）。

        既用于界面展示，也作为后续构建 OASIS profile 的基础。
        """
        if self.persona and self.persona.strip():
            return self.persona

        parts: List[str] = []
        identity = []
        if self.age:
            identity.append(f"{self.age}-year-old")
        if self.occupation:
            identity.append(self.occupation)
        if self.jurisdiction:
            identity.append(f"based in {self.jurisdiction}")
        if identity:
            parts.append(f"{self.name} is a " + " ".join(identity) + ".")
        else:
            parts.append(f"{self.name} is a crypto exchange user.")

        if self.source_of_income:
            parts.append(f"Primary source of income: {self.source_of_income}.")
        if self.income_band or self.net_worth_band:
            wealth = ", ".join(x for x in [self.income_band, self.net_worth_band] if x)
            parts.append(f"Financial profile: {wealth}.")
        if self.risk_type:
            parts.append(f"Risk profile is {self.risk_type}.")
        if self.purpose:
            parts.append(f"Uses the exchange mainly for {self.purpose}.")
        if self.experience_level:
            parts.append(f"Trading experience: {self.experience_level}.")

        behavior = []
        if self.preferred_assets:
            behavior.append("prefers " + ", ".join(self.preferred_assets))
        if self.holding_style:
            behavior.append(f"a {self.holding_style}")
        if self.trading_frequency:
            behavior.append(f"trades {self.trading_frequency}")
        if self.avg_position_size:
            behavior.append(f"typical position size {self.avg_position_size}")
        if self.leverage_usage:
            behavior.append(f"leverage usage: {self.leverage_usage}")
        if behavior:
            parts.append("Trading behavior: " + "; ".join(behavior) + ".")

        if self.reaction_to_volatility:
            parts.append(f"When markets are volatile, they tend to {self.reaction_to_volatility}.")
        if self.sentiment_bias:
            parts.append(f"Generally {self.sentiment_bias} on the market.")
        if self.fomo_susceptibility:
            parts.append(f"FOMO/FUD susceptibility: {self.fomo_susceptibility}.")

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
                                    ("name", "occupation", "risk_type", "purpose", "jurisdiction"))
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
                return int(float(str(value).strip()))
            except (ValueError, TypeError):
                return None
        if field_name in _BOOL_FIELDS:
            if isinstance(value, bool):
                return value
            return str(value).strip().lower() in ("1", "true", "yes", "y", "on", "enabled", "active")
        return str(value).strip() if not isinstance(value, (dict,)) else value

    @classmethod
    def parse_csv(cls, content: str) -> List[Dict[str, Any]]:
        """解析 CSV 文本为原始行字典列表（表头保持原样，映射在导入时进行）。"""
        reader = csv.DictReader(io.StringIO(content))
        return [dict(row) for row in reader]
