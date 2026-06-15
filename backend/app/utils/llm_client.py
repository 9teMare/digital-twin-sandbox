"""
LLM客户端封装
统一使用OpenAI格式调用
"""

import json
import re
from typing import Optional, Dict, Any, List
from openai import OpenAI, BadRequestError

from ..config import Config


class LLMClient:
    """LLM客户端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL_NAME

        if not self.api_key:
            raise ValueError("LLM_API_KEY 未配置")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    # 推理型模型的最小补全 token 预算（需为推理过程留出余量，避免返回空内容）
    REASONING_MIN_COMPLETION_TOKENS = 16000

    def _create_with_param_fallback(self, kwargs: Dict[str, Any]):
        """
        调用 chat.completions.create，并自动适配不同模型/供应商的参数差异。

        例如 OpenAI 的 GPT-5 / o 系列推理模型：
        - 不支持 max_tokens，需改用 max_completion_tokens
        - 仅支持默认 temperature(=1)，不接受自定义值

        遇到对应的 400 错误时，自动修正参数并重试。
        """
        kwargs = dict(kwargs)
        last_error: Optional[BadRequestError] = None

        for _ in range(4):
            try:
                return self.client.chat.completions.create(**kwargs)
            except BadRequestError as e:
                last_error = e
                msg = str(e).lower()
                changed = False

                # max_tokens -> max_completion_tokens
                # 命中此错误说明是推理型模型（如 GPT-5 / o 系列）：
                # max_completion_tokens 同时包含“推理 token”，预算过小会导致
                # 推理耗尽预算、最终返回空内容。这里放大预算并降低推理强度。
                if (
                    "max_tokens" in msg
                    and "max_completion_tokens" in msg
                    and "max_tokens" in kwargs
                ):
                    requested = kwargs.pop("max_tokens")
                    kwargs["max_completion_tokens"] = max(
                        requested, self.REASONING_MIN_COMPLETION_TOKENS
                    )
                    kwargs.setdefault("reasoning_effort", "low")
                    changed = True

                # 自定义 temperature 不被支持时，移除该参数使用默认值
                if (
                    "temperature" in msg
                    and "temperature" in kwargs
                    and (
                        "unsupported" in msg
                        or "does not support" in msg
                        or "only the default" in msg
                    )
                ):
                    kwargs.pop("temperature")
                    changed = True

                if not changed:
                    raise

        # 重试次数耗尽仍失败
        if last_error:
            raise last_error
        return self.client.chat.completions.create(**kwargs)

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
    ) -> str:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式（如JSON模式）

        Returns:
            模型响应文本
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            kwargs["response_format"] = response_format

        response = self._create_with_param_fallback(kwargs)
        content = response.choices[0].message.content
        # 部分模型（如MiniMax M2.5）会在content中包含<think>思考内容，需要移除
        content = re.sub(r"<think>[\s\S]*?</think>", "", content).strip()
        return content

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """
        发送聊天请求并返回JSON

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            解析后的JSON对象
        """
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        # 清理markdown代码块标记
        cleaned_response = response.strip()
        cleaned_response = re.sub(
            r"^```(?:json)?\s*\n?", "", cleaned_response, flags=re.IGNORECASE
        )
        cleaned_response = re.sub(r"\n?```\s*$", "", cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise ValueError(f"LLM返回的JSON格式无效: {cleaned_response}")
