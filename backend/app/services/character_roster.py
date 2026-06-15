"""
角色名单（Roster）构建工具

将"用户库"中选中的角色（CryptoUser）转换为：
1. OASIS Agent Profile（用于写入 reddit_profiles.json / twitter_profiles.csv）
2. EntityNode（复用现有的模拟配置生成器，无需修改其签名）

与种子抽取路径不同：名单模式下用户自行挑选角色，不依赖 Zep 实体抽取。
user_id / agent_id 在此按列表顺序重新分配（0..N-1），
以满足 OASIS 与 initial_posts.poster_agent_id 的匹配约束。
"""

import re
from typing import Dict, Any, List

from ..models.character import Character
from .oasis_profile_generator import OasisAgentProfile
from .zep_entity_reader import EntityNode

ROSTER_ENTITY_TYPE = "CryptoUser"


def _slug(name: str) -> str:
    s = re.sub(r'[^a-z0-9]+', '_', (name or 'user').lower()).strip('_')
    return s or 'user'


def _normalize_gender(gender: Any) -> str:
    if not gender:
        return "other"
    g = str(gender).strip().lower()
    mapping = {
        "男": "male", "女": "female",
        "m": "male", "f": "female",
        "male": "male", "female": "female", "other": "other",
    }
    return mapping.get(g, "other")


def _coerce_age(value: Any) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 30


def character_to_profile(character: Dict[str, Any], user_id: int) -> OasisAgentProfile:
    """把单个角色字典转换为 OASIS Agent Profile（user_id 按名单顺序分配）。"""
    persona = Character.from_dict(character).compose_persona()
    bio = character.get("bio") or (persona[:150] if persona else character.get("name", ""))
    topics = character.get("preferred_assets") or []
    if isinstance(topics, str):
        topics = [t.strip() for t in topics.split(",") if t.strip()]

    name = character.get("name") or f"User {user_id}"

    return OasisAgentProfile(
        user_id=user_id,
        user_name=f"{_slug(name)}_{user_id}",
        name=name,
        bio=bio,
        persona=persona or bio or name,
        age=_coerce_age(character.get("age")),
        gender=_normalize_gender(character.get("gender")),
        mbti=character.get("mbti") or None,
        country=character.get("jurisdiction") or None,
        profession=character.get("occupation") or None,
        interested_topics=topics,
        source_entity_uuid=character.get("character_id"),
        source_entity_type=ROSTER_ENTITY_TYPE,
    )


def build_profiles_from_characters(characters: List[Dict[str, Any]]) -> List[OasisAgentProfile]:
    """批量构建 OASIS Agent Profile，user_id 按列表顺序从 0 开始。"""
    return [character_to_profile(c, idx) for idx, c in enumerate(characters)]


def character_to_entity_node(character: Dict[str, Any]) -> EntityNode:
    """把角色字典转换为 EntityNode，供模拟配置生成器复用。"""
    persona = Character.from_dict(character).compose_persona()

    attr_keys = [
        "risk_type", "purpose", "experience_level", "occupation", "jurisdiction",
        "holding_style", "trading_frequency", "leverage_usage", "avg_position_size",
        "sentiment_bias", "fomo_susceptibility", "source_of_income",
        "income_band", "net_worth_band",
    ]
    attributes: Dict[str, Any] = {}
    for k in attr_keys:
        v = character.get(k)
        if v:
            attributes[k] = v
    assets = character.get("preferred_assets") or []
    if assets:
        attributes["preferred_assets"] = ", ".join(assets) if isinstance(assets, list) else str(assets)

    return EntityNode(
        uuid=character.get("character_id") or _slug(character.get("name", "")),
        name=character.get("name") or "Unnamed User",
        labels=["Entity", ROSTER_ENTITY_TYPE],
        summary=persona or character.get("bio") or "",
        attributes=attributes,
    )


def build_entity_nodes_from_characters(characters: List[Dict[str, Any]]) -> List[EntityNode]:
    return [character_to_entity_node(c) for c in characters]
