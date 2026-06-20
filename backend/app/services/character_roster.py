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


def character_to_profile(character: Dict[str, Any], user_id: int) -> OasisAgentProfile:
    """把单个角色字典转换为 OASIS Agent Profile（user_id 按名单顺序分配）。

    交易所用户数据没有姓名/年龄/性别：
    - name 用 uid 兜底
    - country 取二级区域(region)
    - profession 取主要交易产品(main_product)
    - 兴趣话题取偏好资产，缺省回退到主要交易币种(main_coin)
    """
    persona = Character.from_dict(character).compose_persona()
    bio = character.get("bio") or (persona[:150] if persona else character.get("name", ""))

    topics = character.get("preferred_assets") or []
    if isinstance(topics, str):
        topics = [t.strip() for t in topics.split(",") if t.strip()]
    if not topics and character.get("main_coin"):
        topics = [character["main_coin"]]

    uid = character.get("uid")
    name = character.get("name") or (f"User {uid}" if uid not in (None, "") else f"User {user_id}")

    return OasisAgentProfile(
        user_id=user_id,
        user_name=f"{_slug(name)}_{user_id}",
        name=name,
        bio=bio,
        persona=persona or bio or name,
        country=character.get("region") or None,
        profession=character.get("main_product") or None,
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
        "region", "user_source", "registered_at", "vip_level",
        "main_product", "main_coin", "positions",
        "orders_30d", "orders_90d", "volume_30d", "volume_90d",
        "fees_30d", "fees_90d", "activities_90d", "rewards_claimed",
        "risk_type",
    ]
    attributes: Dict[str, Any] = {}
    for k in attr_keys:
        v = character.get(k)
        if v not in (None, "", []):
            attributes[k] = v
    assets = character.get("preferred_assets") or []
    if assets:
        attributes["preferred_assets"] = ", ".join(assets) if isinstance(assets, list) else str(assets)
    activity_ids = character.get("activity_ids") or []
    if activity_ids:
        attributes["activity_ids"] = ", ".join(map(str, activity_ids)) if isinstance(activity_ids, list) else str(activity_ids)

    return EntityNode(
        uuid=character.get("character_id") or _slug(character.get("name", "")),
        name=character.get("name") or "Unnamed User",
        labels=["Entity", ROSTER_ENTITY_TYPE],
        summary=persona or character.get("bio") or "",
        attributes=attributes,
    )


def build_entity_nodes_from_characters(characters: List[Dict[str, Any]]) -> List[EntityNode]:
    return [character_to_entity_node(c) for c in characters]


def character_to_episode_text(character: Dict[str, Any]) -> str:
    """把单个角色序列化为适合 Zep 抽取的自然语言 episode 文本。

    用于"图谱增强"：把用户挑选进本次模拟的角色注入到已构建的图谱（GraphRAG）中，
    使其成为知识图谱的一部分，并与种子场景中的实体建立关联。

    文本同时包含：
    - 可读人设（compose_persona）
    - 结构化的关键交易指标（便于 Zep 抽取实体属性）
    """
    char = Character.from_dict(character)
    name = char.name
    uid = character.get("uid")
    persona = char.compose_persona()

    header = f"Crypto exchange user {name}"
    if uid not in (None, ""):
        header += f" (UID {uid})"
    header += " is one of the participants in this simulation scenario."

    lines: List[str] = [header]
    if persona:
        lines.append(persona)

    facts: List[str] = []

    def add(label: str, value: Any) -> None:
        if value not in (None, "", []):
            facts.append(f"{label}: {value}")

    add("Region", character.get("region"))
    add("Registration source", character.get("user_source"))
    add("Registered at", character.get("registered_at"))
    add("VIP level", character.get("vip_level"))
    add("Main trading product", character.get("main_product"))
    add("Main trading coin", character.get("main_coin"))
    add("Open positions", character.get("positions"))
    add("Orders in last 30 days", character.get("orders_30d"))
    add("Orders in last 90 days", character.get("orders_90d"))
    add("Trading volume in last 30 days", character.get("volume_30d"))
    add("Trading volume in last 90 days", character.get("volume_90d"))
    add("Trading fees in last 30 days", character.get("fees_30d"))
    add("Trading fees in last 90 days", character.get("fees_90d"))
    add("Activities joined in last 90 days", character.get("activities_90d"))
    add("Rewards claimed", character.get("rewards_claimed"))
    assets = character.get("preferred_assets") or []
    if assets:
        add("Preferred assets", ", ".join(assets) if isinstance(assets, list) else str(assets))
    add("Risk type", character.get("risk_type"))

    if facts:
        lines.append("Key profile facts — " + "; ".join(facts) + ".")

    return "\n".join(lines)


def build_episode_texts_from_characters(characters: List[Dict[str, Any]]) -> List[str]:
    return [character_to_episode_text(c) for c in characters]
