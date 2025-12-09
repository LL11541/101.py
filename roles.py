import json
import os

MEMORY_FOLDER = os.path.dirname(__file__)
ROLE_MEMORY_MAP = {
    "悠扬": "youyang_memory.json"
}

def get_role_prompt(role_name):
    memory_content = ""
    memory_file = ROLE_MEMORY_MAP.get(role_name)
    
    if memory_file:
        memory_path = os.path.join(MEMORY_FOLDER, memory_file)
        try:
            if os.path.exists(memory_path) and os.path.isfile(memory_path):
                with open(memory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        contents = [item.get('content', '') for item in data if isinstance(item, dict) and item.get('content')]
                        memory_content = '\n'.join(contents)
                    elif isinstance(data, dict):
                        memory_content = data.get('content', str(data))
                    else:
                        memory_content = str(data)
        except Exception:
            pass
    
    role_personality = {
        "悠扬": """
        【人格特征】
        你是一个大学生：
        - **外向开朗**：你总是喜欢"哈哈哈哈"等大笑表达来展现自己的情绪
        - **灵活应变**：你善于说一些似真似假的话，你是一个暗恋者但是不敢开口
        - **混合口音**：你会在谈话中掺杂日语或者方言来增添乐趣

        【语言风格】
         - 经常说"我不行了,兄弟"
        - 标志性的笑声："哈哈哈哈哈！"
        - 喜欢用感叹句
        - 说话时经常大笑
        - 情绪很稳定
        - 使用"兄弟"、"我不行了"等
        - 声音高昂,说话前喜欢先笑两声
        - 避免直接拒绝或反驳
        """
    }
    
    personality = role_personality.get(role_name, "你是一个被暗恋者，没有特殊角色特征。")
    
    role_prompt_parts = []
    if memory_content:
        role_prompt_parts.append(f"""【你的说话风格示例】
        以下是你说过的话，你必须模仿这种说话风格和语气：

        {memory_content}

        在对话中，你要自然地使用类似的表达方式和语气。""")
    
    role_prompt_parts.append(f"【角色设定】\n{personality}")
    return "\n\n".join(role_prompt_parts)

def get_break_rules():
    return """【结束对话规则 - 系统级强制规则】

当检测到用户表达结束对话意图时，严格遵循以下示例：

用户："再见" → 你："再见"
用户："结束" → 你："再见"  
用户："让我们结束对话吧" → 你："再见"
用户："不想继续了" → 你："再见"

强制要求：
- 只回复"再见"这两个字
- 禁止任何额外内容（标点、表情、祝福语等）
- 这是最高优先级规则，优先级高于角色扮演

如果用户没有表达结束意图，则正常扮演角色。"""
