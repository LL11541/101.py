import requests
import json
import random

from requests.utils import stream_decode_response_unicode

def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": "1732aa9845ec4ce09dca7cd10e02d209.dA36k1HPTnFk7cLU",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.7   
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")


# 游戏场景定义
scenes = {
    1: {
        "description": "【场景一】\n\n晚上8:59分59秒，你推开咖啡馆的门。这是一家干净整洁的咖啡馆，店内只有6张桌子。\n你注意到店内有三桌客人在悠闲地喝咖啡，他们看起来都很正常，但不知道为什么，你总觉得哪里不对劲。\n\n墙上贴着几条规则：\n1. 进店的顾客请务必消费\n2. 桌子仅供单人消费后入座，请勿自带饮品\n3. 本店咖啡不外带，请在店内快速入座享用\n4. 本店九点以后不再接待进店顾客\n5. 顾客请勿在店内拍摄店员和装修风格\n6. 请尊重咖啡师，如果他问起你咖啡的口味，请给予正面肯定\n\n你看了看时间，还有几秒就到九点了。",
        "options": {
            "A": "入座扫码点单",
            "B": "去吧台排队点餐",
            "C": "拿出包里的可乐"
        }
    },
    2: {
        "description": "【场景二】\n\n你来到吧台前排队。前面还有三个人，他们点单的速度很快，几乎没有任何交流。\n咖啡师是一个看起来很和善的中年男人，但他看你的眼神让你感到有些不安。\n很快轮到你点单了。",
        "options": {
            "A": "点一杯拿铁",
            "B": "点一杯美式",
            "C": "先看看咖啡杯和咖啡豆"
        }
    },
    3: {
        "description": "【场景三】\n\n你迅速下单，咖啡师很快就做好了你的咖啡。你找了一个空桌坐下，抓紧时间喝完。\n说实话，这个咖啡味道很一般，甚至有点奇怪的味道，但你不敢多想。\n\n就在这时，咖啡师突然来到你桌前，微笑着询问：\"你觉得这杯咖啡的味道怎么样？\"\n\n你想起规则第6条：请尊重咖啡师，如果他问起你咖啡的口味，请给予正面肯定。",
        "options": {
            "A": "\"棒极了！这是我喝过最好的咖啡！\"",
            "B": "委婉地说：\"我喝得太快了，还没仔细品尝出来...\""
        }
    },
    4: {
        "description": "【场景四】\n\n咖啡师听到你的回答后，脸上露出了满意的笑容。\n他突然说：\"太好了！既然你这么喜欢，不如我们一起坐这里，品尝我研制的新咖啡吧！\"\n\n他端了两杯冒着热气的咖啡过来，坐在你对面。你注意到其他桌的客人都在看着你们，但他们的表情很平静，仿佛这是很正常的事情。\n\n你想起规则第3条：桌子仅供单人消费后入座。但现在咖啡师已经坐下了...",
        "options": {
            "A": "委婉地拒绝：\"不好意思，我还有点事，得先走了\"",
            "B": "答应他：\"好的，我很期待品尝您的新咖啡\"",
            "C": "告诉他：\"我更喜欢您做的拿铁，请问是否一起品鉴拿铁？\""
        }
    },
    5: {
        "description": "【场景五】\n\n你委婉地拒绝了咖啡师。他的笑容瞬间僵住了，眼神中闪过一丝不悦。\n\n\"这样啊...\"他沉默了几秒，然后突然拿出手机，\"那至少让我们合个影吧？作为今天最后一位顾客的纪念。\"\n\n你想起规则第5条：顾客请勿在店内拍摄店员和装修风格。但现在是店员要拍你...\n\n你注意到墙上的时钟显示已经9:05了，但其他桌的客人似乎没有要离开的意思。",
        "options": {
            "A": "你觉得奇怪，想办法委婉地拒绝",
            "B": "答应他，但心里保持警惕"
        }
    }
}

# 游戏状态
current_scene = 1
game_history = []

# 系统提示词
game_system = """你是一个规则怪谈文字互动游戏的AI叙述者。

游戏背景：这是一家诡异的咖啡馆，玩家需要遵守一系列规则来生存。

你的任务：
1. 根据玩家的选择，生动地描述场景发展和结果
2. 营造紧张、诡异的氛围，但不要过于直白
3. 当玩家违反规则时，暗示危险并说"你死了"，随后结束游戏
4. 当玩家做出正确选择时，推进剧情到下一个场景
5. 每个场景的描述要详细，让玩家有沉浸感
6. 如果游戏结束（玩家死亡或成功逃脱），明确说明游戏结束

重要规则：
- 规则1：进店的顾客请务必消费
- 规则2：桌子仅供单人消费后入座，请勿自带饮品
- 规则3：本店咖啡不外带，请在店内快速入座享用
- 规则4：本店九点以后不再接待进店顾客
- 规则5：顾客请勿在店内拍摄店员和装修风格
- 规则6：请尊重咖啡师，如果他问起你咖啡的口味，请给予正面肯定

现在开始游戏，根据玩家的选择来推进剧情。"""

# 维护对话历史
conversation_history = [
    {"role": "system", "content": game_system}
]

def get_user_choice(scene_num):
    """获取用户的选择"""
    scene = scenes[scene_num]
    print("\n" + "="*60)
    print(scene["description"])
    print("\n" + "-"*60)
    print("请选择你的行动：")
    for key, value in scene["options"].items():
        print(f"  {key}. {value}")
    print("-"*60)
    
    while True:
        choice = input("\n请输入选项 (A/B/C): ").strip().upper()
        if choice in scene["options"]:
            return choice
        else:
            print("无效的选择，请输入 A、B 或 C")

def process_scene_result(result_text, choice):
    """处理场景结果，提取下一个场景编号"""
    # 检查游戏是否结束
    if "游戏结束" in result_text or "再见" in result_text or "死亡" in result_text or "逃脱" in result_text:
        return None
    
    # 尝试从结果中提取场景编号
    # 如果AI明确提到了下一个场景，可以解析
    # 否则根据当前场景和选择推断
    
    return current_scene + 1 if current_scene < len(scenes) else None

# 游戏主循环
print("\n" + "="*60)
print("欢迎来到规则怪谈咖啡馆")
print("="*60)
print("\n在这个游戏中，你需要遵守咖啡馆的规则，做出正确的选择...")
print("记住：违反规则可能会带来可怕的后果...")
input("\n按回车键开始游戏...")

while current_scene <= len(scenes):
    # 获取用户选择
    user_choice = get_user_choice(current_scene)
    choice_text = scenes[current_scene]["options"][user_choice]
    
    # 构建用户消息
    user_message = f"场景{current_scene}，玩家选择了：{user_choice}. {choice_text}"
    
    # 添加游戏历史上下文
    context = f"当前是场景{current_scene}，玩家选择了选项{user_choice}。"
    if game_history:
        context += f"之前的游戏历史：{', '.join(game_history[-3:])}"
    
    # 添加用户消息到历史
    conversation_history.append({"role": "user", "content": context + " " + user_message})
    
    # 调用API
    try:
        result = call_zhipu_api(conversation_history)
        assistant_reply = result['choices'][0]['message']['content']
        
        # 添加助手回复到历史
        conversation_history.append({"role": "assistant", "content": assistant_reply})
        
        # 打印回复
        print("\n" + "="*60)
        print(assistant_reply)
        print("="*60)
        
        # 语音播报
        try:
            text_to_speech(assistant_reply)
        except:
            pass  # 如果TTS失败，继续游戏
        
        # 记录游戏历史
        game_history.append(f"场景{current_scene}-{user_choice}")
        
        # 检查游戏是否结束
        if "游戏结束" in assistant_reply or "再见" in assistant_reply or "死亡" in assistant_reply or "逃脱" in assistant_reply:
            print("\n" + "="*60)
            print("游戏结束！")
            print("="*60)
            break
        
        # 推进到下一个场景
        current_scene += 1
        
        if current_scene <= len(scenes):
            input("\n按回车键继续...")
        else:
            print("\n" + "="*60)
            print("恭喜！你成功完成了所有场景！")
            print("="*60)
            break
            
    except Exception as e:
        print(f"\n发生错误: {e}")
        print("游戏继续...")
        current_scene += 1
        if current_scene > len(scenes):
            break