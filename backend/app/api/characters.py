"""
角色（用户）库相关 API

提供加密货币交易所用户角色的增删改查、批量导入（CSV/JSON）与导出。
角色库为全局库，与具体种子/项目解耦，可在运行模拟时按需挑选。
"""

import json
import traceback
from flask import request, jsonify, Response

from . import characters_bp
from ..models.character import CharacterManager, Character
from ..utils.logger import get_logger
from ..utils.locale import t

logger = get_logger('digital_twin_agent_sandbox.api.characters')


@characters_bp.route('/list', methods=['GET'])
def list_characters():
    """列出角色（支持搜索 q、标签 tag、启用状态 enabled、分页 limit/offset）"""
    try:
        query = request.args.get('q')
        tag = request.args.get('tag')
        enabled_param = request.args.get('enabled')
        enabled = None
        if enabled_param is not None and enabled_param != '':
            enabled = enabled_param.lower() in ('1', 'true', 'yes')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        items, total, all_tags = CharacterManager.list_characters(
            query=query, tag=tag, enabled=enabled, limit=limit, offset=offset
        )
        return jsonify({
            "success": True,
            "data": {
                "characters": items,
                "total": total,
                "limit": limit,
                "offset": offset,
                "all_tags": all_tags,
            }
        })
    except Exception as e:
        logger.error(f"列出角色失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@characters_bp.route('/create', methods=['POST'])
def create_character():
    """创建角色"""
    try:
        data = request.get_json() or {}
        if not (data.get('name') or '').strip():
            return jsonify({"success": False, "error": t('characters.errNameRequired')}), 400
        character = CharacterManager.create_character(data)
        return jsonify({"success": True, "data": character})
    except Exception as e:
        logger.error(f"创建角色失败: {str(e)}")
        return jsonify({"success": False, "error": str(e), "traceback": traceback.format_exc()}), 500


@characters_bp.route('/<character_id>', methods=['GET'])
def get_character(character_id: str):
    """获取单个角色"""
    character = CharacterManager.get_character(character_id)
    if not character:
        return jsonify({"success": False, "error": t('characters.errNotFound')}), 404
    return jsonify({"success": True, "data": character})


@characters_bp.route('/<character_id>', methods=['PUT'])
def update_character(character_id: str):
    """更新角色"""
    try:
        data = request.get_json() or {}
        updated = CharacterManager.update_character(character_id, data)
        if not updated:
            return jsonify({"success": False, "error": t('characters.errNotFound')}), 404
        return jsonify({"success": True, "data": updated})
    except Exception as e:
        logger.error(f"更新角色失败: {str(e)}")
        return jsonify({"success": False, "error": str(e), "traceback": traceback.format_exc()}), 500


@characters_bp.route('/<character_id>', methods=['DELETE'])
def delete_character(character_id: str):
    """删除角色"""
    ok = CharacterManager.delete_character(character_id)
    if not ok:
        return jsonify({"success": False, "error": t('characters.errNotFound')}), 404
    return jsonify({"success": True, "data": {"character_id": character_id}})


@characters_bp.route('/import', methods=['POST'])
def import_characters():
    """批量导入角色。

    支持两种方式：
    1) multipart/form-data 上传文件（.csv 或 .json），字段名 file
    2) application/json 请求体：{ "characters": [ {...}, ... ] }  或  { "csv": "..." }
    """
    try:
        rows = []

        # 方式一：上传文件
        if 'file' in request.files:
            file = request.files['file']
            filename = (file.filename or '').lower()
            raw = file.read().decode('utf-8-sig', errors='replace')
            if filename.endswith('.json'):
                parsed = json.loads(raw)
                rows = parsed if isinstance(parsed, list) else parsed.get('characters', [])
            else:
                rows = CharacterManager.parse_csv(raw)
        else:
            data = request.get_json(silent=True) or {}
            if isinstance(data.get('characters'), list):
                rows = data['characters']
            elif isinstance(data.get('csv'), str):
                rows = CharacterManager.parse_csv(data['csv'])

        if not rows:
            return jsonify({"success": False, "error": t('characters.errNoRows')}), 400

        count = CharacterManager.import_characters(rows, source='uploaded')
        return jsonify({
            "success": True,
            "data": {"imported": count, "received": len(rows)}
        })
    except json.JSONDecodeError as e:
        return jsonify({"success": False, "error": f"JSON parse error: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"导入角色失败: {str(e)}")
        return jsonify({"success": False, "error": str(e), "traceback": traceback.format_exc()}), 500


@characters_bp.route('/export', methods=['GET'])
def export_characters():
    """导出全部角色为 JSON 文件"""
    items = CharacterManager.export_characters()
    payload = json.dumps(items, ensure_ascii=False, indent=2)
    return Response(
        payload,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=characters.json'}
    )
