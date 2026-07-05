# -*- coding: utf-8 -*-
"""
验证当前环境是否支持 OpenAI function calling
"""
import json
import sys


def test_openai_function_calling():
    """测试 OpenAI 库是否支持 function calling 功能"""
    results = {}

    # 1. 检查 openai 模块是否可导入
    try:
        import openai
        results["openai_installed"] = True
        results["openai_version"] = openai.__version__ if hasattr(openai, "__version__") else "未知版本"
    except ImportError as e:
        results["openai_installed"] = False
        results["openai_error"] = str(e)
        print("❌ openai 模块未安装")
        return results

    # 2. 检查是否有 ChatCompletion 相关的 function calling 支持
    try:
        # 检查客户端对象是否支持 function calling
        client = openai.OpenAI() if hasattr(openai, "OpenAI") else None
        if client:
            # 检查 chat.completions.create 是否支持 functions/tools 参数
            import inspect
            sig = inspect.signature(client.chat.completions.create)
            params = list(sig.parameters.keys())
            has_tools = "tools" in params
            has_functions = "functions" in params
            results["client_supports_tools_param"] = has_tools
            results["client_supports_functions_param"] = has_functions
            print(f"✅ OpenAI 客户端 chat.completions.create 参数: {params}")
        else:
            results["client_supports_tools_param"] = False
            results["client_supports_functions_param"] = False
            print("⚠️ 未找到 OpenAI 客户端类")
    except Exception as e:
        results["client_inspect_error"] = str(e)

    # 3. 尝试构造一个 function calling 请求示例（不实际发送）
    try:
        tools_example = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "获取指定城市的天气信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "城市名称"
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
        results["tools_schema_valid"] = True
        print("✅ function calling tools 模式 schema 构造成功")
        print(f"   tools 示例: {json.dumps(tools_example, ensure_ascii=False, indent=2)}")
    except Exception as e:
        results["tools_schema_valid"] = False
        results["tools_schema_error"] = str(e)

    # 4. 检查支持的模型
    try:
        results["supported_models_note"] = (
            "支持 function calling 的模型: gpt-4, gpt-4-turbo, gpt-4o, gpt-3.5-turbo 等"
            "（需配合 API key 实际调用验证）"
        )
    except Exception as e:
        pass

    return results


def main():
    print("=" * 60)
    print("OpenAI Function Calling 环境验证")
    print("=" * 60)
    print()

    results = test_openai_function_calling()

    print()
    print("=" * 60)
    print("验证结论")
    print("=" * 60)

    if results.get("openai_installed"):
        print("✅ openai 模块已安装")
        print(f"   版本: {results.get('openai_version', '未知')}")
        if results.get("client_supports_tools_param"):
            print("✅ 客户端支持 tools 参数 (function calling)")
        if results.get("client_supports_functions_param"):
            print("✅ 客户端支持 functions 参数 (传统模式)")
        if results.get("tools_schema_valid"):
            print("✅ function calling 请求 schema 构造正常")
        print()
        print("📋 使用 function calling 的基本步骤:")
        print("   1. 定义 tools 列表（描述可用函数及其参数 schema）")
        print("   2. 调用 client.chat.completions.create(tools=tools, ...)")
        print("   3. 处理模型返回的 tool_calls 调用请求")
        print("   4. 执行实际函数并返回结果给模型")
    else:
        print("❌ openai 模块未安装，无法使用 function calling")
        print("   请运行: pip install openai")

    print()
    print("💡 提示: 本验证仅确认 API 支持，实际 function calling 需要有效的 OpenAI API key")
    print("=" * 60)


if __name__ == "__main__":
    main()