#!/usr/bin/env python3
"""
Ollama 诊断脚本 - 检查 Ollama 服务是否正常工作
使用方法: python backend/scripts/diagnose_ollama.py
"""
import httpx
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.settings import get_settings

def check_ollama_service():
    """检查 Ollama 服务状态"""
    print("=" * 60)
    print("🔍 Ollama 诊断工具")
    print("=" * 60)
    
    settings = get_settings()
    # Normalize to use 127.0.0.1 instead of localhost to avoid IPv6 issues
    base_url = settings.ollama_api_url.replace("/api/generate", "").replace("localhost", "127.0.0.1")
    api_url = settings.ollama_api_url.replace("localhost", "127.0.0.1")
    
    print(f"\n📋 配置信息:")
    print(f"   API URL: {settings.ollama_api_url}")
    print(f"   模型: {settings.ollama_model}")
    print(f"   超时: {settings.ollama_timeout}秒")
    print(f"   基础 URL: {base_url}")
    
    issues = []
    
    # 步骤 1: 检查服务是否运行
    print(f"\n[1/4] 检查 Ollama 服务是否运行...")
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{base_url}/api/tags")
            response.raise_for_status()
            print("   ✅ Ollama 服务正在运行")
            
            # 显示已安装的模型
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            print(f"   📦 已安装的模型: {', '.join(model_names) if model_names else '无'}")
            
    except httpx.ConnectError:
        print("   ❌ Ollama 服务未运行")
        print("   💡 尝试运行: brew services start ollama")
        issues.append("Ollama 服务未运行")
        return False, issues
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        issues.append(f"连接失败: {e}")
        return False, issues
    
    # 步骤 2: 检查模型是否存在
    print(f"\n[2/4] 检查模型 '{settings.ollama_model}' 是否可用...")
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{base_url}/api/tags")
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            if settings.ollama_model in model_names:
                print(f"   ✅ 模型 '{settings.ollama_model}' 已安装")
            else:
                print(f"   ❌ 模型 '{settings.ollama_model}' 未安装")
                print(f"   💡 运行: ollama pull {settings.ollama_model}")
                issues.append(f"模型 '{settings.ollama_model}' 未安装")
                return False, issues
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")
        issues.append(f"检查模型失败: {e}")
        return False, issues
    
    # 步骤 3: 测试简单生成
    print(f"\n[3/4] 测试模型生成功能...")
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                api_url,
                json={
                    "model": settings.ollama_model,
                    "prompt": "Say 'Hello' in one word",
                    "stream": False,
                }
            )
            response.raise_for_status()
            result = response.json()
            
            if "response" in result:
                generated_text = result["response"].strip()
                print(f"   ✅ 生成成功")
                print(f"   📝 响应: {generated_text[:50]}...")
            else:
                print(f"   ⚠️  响应格式异常")
                issues.append("响应格式异常")
                return False, issues
    except httpx.HTTPStatusError as e:
        print(f"   ❌ HTTP 错误: {e.response.status_code}")
        error_text = e.response.text[:200]
        print(f"   📄 响应: {error_text}")
        issues.append(f"HTTP {e.response.status_code}: {error_text}")
        return False, issues
    except Exception as e:
        print(f"   ❌ 生成失败: {e}")
        issues.append(f"生成失败: {e}")
        return False, issues
    
    # 步骤 4: 测试完整流程（模拟后端调用）
    print(f"\n[4/4] 测试完整 API 调用...")
    try:
        with httpx.Client(timeout=settings.ollama_timeout) as client:
            response = client.post(
                api_url,
                json={
                    "model": settings.ollama_model,
                    "prompt": "Test prompt",
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "num_predict": 10,
                    },
                }
            )
            response.raise_for_status()
            result = response.json()
            
            if "response" in result and result.get("done", False):
                print("   ✅ 完整流程测试成功")
            else:
                print("   ⚠️  响应不完整")
                issues.append("响应不完整")
                return False, issues
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        issues.append(f"完整测试失败: {e}")
        return False, issues
    
    print("\n" + "=" * 60)
    print("✅ 所有检查通过！Ollama 配置正常。")
    print("=" * 60)
    return True, []

if __name__ == "__main__":
    success, issues = check_ollama_service()
    if not success:
        print("\n❌ 发现问题，请按照上述提示进行修复。")
        if issues:
            print("\n问题摘要:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
    sys.exit(0 if success else 1)

