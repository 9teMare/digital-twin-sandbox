"""
测试Profile格式生成是否符合OASIS要求
验证：
1. Twitter Profile生成CSV格式
2. Reddit Profile生成JSON详细格式
"""

import os
import sys
import json
import csv
import tempfile

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.oasis_profile_generator import OasisProfileGenerator, OasisAgentProfile


def test_profile_formats():
    """测试Profile格式"""
    print("=" * 60)
    print("OASIS Profile格式测试")
    print("=" * 60)
    
    # 创建测试Profile数据
    test_profiles = [
        OasisAgentProfile(
            user_id=0,
            user_name="test_user_123",
            name="Test User",
            bio="A test trader for validation",
            persona="Test User is an active crypto trader who posts market views and reacts quickly to volatility.",
            karma=1500,
            friend_count=100,
            follower_count=200,
            statuses_count=500,
            risk_tolerance="aggressive",
            trading_style="day_trader",
            experience_level="intermediate",
            profession="Futures Trader",
            interested_topics=["BTC", "ETH"],
            source_entity_uuid="test-uuid-123",
            source_entity_type="CryptoUser",
        ),
        OasisAgentProfile(
            user_id=1,
            user_name="org_official_456",
            name="Official Organization",
            bio="Official account for Organization",
            persona="This is an official institutional account that communicates market policy and compliance updates.",
            karma=5000,
            friend_count=50,
            follower_count=10000,
            statuses_count=200,
            risk_tolerance="moderate",
            trading_style="long_term",
            experience_level="advanced",
            profession="Organization",
            interested_topics=["Policy", "Compliance"],
            source_entity_uuid="test-uuid-456",
            source_entity_type="University",
        ),
    ]
    
    generator = OasisProfileGenerator.__new__(OasisProfileGenerator)
    
    # 使用临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        twitter_path = os.path.join(temp_dir, "twitter_profiles.csv")
        reddit_path = os.path.join(temp_dir, "reddit_profiles.json")
        
        # 测试Twitter CSV格式
        print("\n1. 测试Twitter Profile (CSV格式)")
        print("-" * 40)
        generator._save_twitter_csv(test_profiles, twitter_path)
        
        # 读取并验证CSV
        with open(twitter_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        print(f"   文件: {twitter_path}")
        print(f"   行数: {len(rows)}")
        print(f"   表头: {list(rows[0].keys())}")
        print(f"\n   示例数据 (第1行):")
        for key, value in rows[0].items():
            preview = value[:80] + "..." if len(value) > 80 else value
            print(f"     {key}: {preview}")
        
        # 验证必需字段
        required_twitter_fields = ['user_id', 'name', 'username', 'user_char', 'description']
        missing = set(required_twitter_fields) - set(rows[0].keys())
        if missing:
            print(f"\n   [错误] 缺少字段: {missing}")
        else:
            print(f"\n   [通过] 所有必需字段都存在")
        
        # 测试Reddit JSON格式
        print("\n2. 测试Reddit Profile (JSON详细格式)")
        print("-" * 40)
        generator._save_reddit_json(test_profiles, reddit_path)
        
        # 读取并验证JSON
        with open(reddit_path, 'r', encoding='utf-8') as f:
            reddit_data = json.load(f)
        
        print(f"   文件: {reddit_path}")
        print(f"   条目数: {len(reddit_data)}")
        print(f"   字段: {list(reddit_data[0].keys())}")
        print(f"\n   示例数据 (第1条):")
        print(json.dumps(reddit_data[0], ensure_ascii=False, indent=4))
        
        required_reddit_fields = ['user_id', 'username', 'name', 'bio', 'persona']
        optional_reddit_fields = [
            'risk_tolerance', 'trading_style', 'experience_level',
            'profession', 'interested_topics'
        ]
        
        missing = set(required_reddit_fields) - set(reddit_data[0].keys())
        if missing:
            print(f"\n   [错误] 缺少必需字段: {missing}")
        else:
            print(f"\n   [通过] 所有必需字段都存在")
        
        present_optional = set(optional_reddit_fields) & set(reddit_data[0].keys())
        print(f"   [信息] 可选字段: {present_optional}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


def show_expected_formats():
    """显示OASIS期望的格式"""
    print("\n" + "=" * 60)
    print("OASIS 期望的Profile格式参考")
    print("=" * 60)
    
    print("\n1. Twitter Profile (CSV格式)")
    print("-" * 40)
    twitter_example = """user_id,name,username,user_char,description,risk_tolerance,trading_style,experience_level
0,User Zero,user0,I am user zero...,Short bio...,moderate,swing,intermediate"""
    print(twitter_example)
    
    print("\n2. Reddit Profile (JSON详细格式)")
    print("-" * 40)
    reddit_example = [
        {
            "username": "miller_trades",
            "name": "James Miller",
            "bio": "Passionate about crypto markets.",
            "persona": "James is an active futures trader who posts macro views and reacts to volatility...",
            "risk_tolerance": "aggressive",
            "trading_style": "day_trader",
            "experience_level": "advanced",
            "profession": "Futures Trader",
            "interested_topics": ["BTC", "Macro"]
        }
    ]
    print(json.dumps(reddit_example, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    test_profile_formats()
    show_expected_formats()
