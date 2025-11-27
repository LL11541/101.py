
import streamlit as st
import requests
import json
import os  # 新增：用于文件操作

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
        "temperature": 0.5   
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")

# ========== 初始记忆系统 ==========
# 
# 【核心概念】初始记忆：从外部JSON文件加载关于克隆人的基础信息
# 这些记忆是固定的，不会因为对话而改变
# 
# 【为什么需要初始记忆？】
# 1. 让AI知道自己的身份和背景信息
# 2. 基于这些记忆进行个性化对话
# 3. 记忆文件可以手动编辑，随时更新

# 记忆文件夹路径
MEMORY_FOLDER = "4.2_memory_clonebot"

# 角色名到记忆文件名的映射
ROLE_MEMORY_MAP = {
    "悠扬": "youyang_memory.json"
}

# ========== 初始记忆系统 ==========

# ========== ASCII 头像 ==========
def get_portrait():
    """返回 ASCII 艺术头像"""
    return """
odocccc:::::::cccccccclloodkkkxddxxxxkkkkkkkkkkxxddodxkOO00OOkxddddddddddddddxxxxxxxxxkkkkkOkkkkOOO0
dxxolcccccccccccccccclloodxkkkxxxxxkkkOOOOOOOOkkxddddkkOOO0OOOkxxdddddddddddxxxxxxxxxkkkkkkOOOOOOOO0
dxkxolccccccccccccccllloodxkkkkkxxxkkkkOOOOOkkkkxxxxxkkOOOOOOOkkxxxdddddddddxxxxxxxxxkkkkkOkkkkkOOO0
dxkkxolccccccccccccllooodxxkkkkkkxkkkkkOOOOOkkkkkxxxkkkOOOOOOOOkkkxxdddddddxxxxxxxxxxkOOOkkkxddxkOO0
xkkkkxolcccccccccllloodddxkkkkkkkkkkkkkOOOOOkkkkxxxxxxxxxkkkkkkkxxxxxxxxxxdxxxxxxxxxkkkOOkxdollodkO0
xkkkkkxdllccccccllloodddxxkkkkkkkkkkkkOOOOOkkkxxxddddddxxxkkkkxxxxxxxxxxxxxxddddddxxkkkOkxddolllldkO
kkkkkkkkdolllllllloodddxxkkkkkkkkkkkkkkOOkkkkxxdoooooddxxxxxxxxxxxxxxxxddddddddddxxkkkxxxdoollllcokO
kkkkkkkkkxolllllloodddxxxkkkkkkkkkkkkkkkkkkkkxdolooddoolllllllooddddddooooooooddxxkkkkdoolcccccccokO
kkkkkkkkkkxdooooodddddxxkkkkxxxkkkkkkkkkkkkxxdooodddlcccloddddoollcccccclllllloodxxkkxollc::::ccldkO
kkkkkkkkkkkxdooodddddxxxkkkkkkkkkkkkxxdxxxdolc:cllc:;,;;;:::ccc::;:::::clooooooooooddoclc:::::ccldkO
kkkkkkkkkkkxxddddddddxxxkkkkkkkkkkxxxdoolc:,''.'''...........''''''',,;;:clddxxxddoc;;:c:::;;:::ldkO
kkkkkkkkkkkxxdddddddxxxxkkOOOkkxxdddolc:;,'..........      .....''''''''',;cloooool:'.,:;;;;;;;:lxk0
kkkkkkkkkkkkxdddddddxxxxkkkkkkxdddol:,''.'''''',;:::::;,'.........''''''''',,,,,;;,,''',,;;,,,;:lxO0
kkkkkkkkkkkkxdddddddxxxkkkkkkxdddoc,.....';codkO00KKK00Okxdl:;'......''''''',,,'....'''...',,,,;lxO0
kkkkkkkkkkkxxdddddddxxxkkkxxxxdoc;'...';ldO0KKKXXXXXXKKKKKK0Okxo:,.......'''',,,,,'........',,,;ok00
kkkkkkkkkkkxxdddddddxxxkxxddxdl;....,cdO0KKXXXXXXXXXXXXXXXXKKK0Okdl;'........'',;;;,''......''';dO00
kkkkkkkkkkkxxdddddddxxxxddddo:....,lk0KKKXXXXXXXXXXXNNNNXXXKKKKK0Okdc,..........,;;;,,'.......';d00K
kkkkOOOOkkkxxdddddddxxxddddl,...'cx0KKKKKXXXXXXXXXXXXXNNXXXKKKKKK00Okdc'.........,;;,,'.......':x00K
kkkOOOOOOOkxdddddxxxddxxxdc'...,oO00KKKKKKKKKKXXXXXXXXXXXXXKKKKKKKKK00ko;.........',,,''......':x00K
kkkkkxkkkkkkxdddxxxddxxxd:'...;dOO00KKKKKKKKKKXXXXXXXXXXXXXXXXKXXKKKK00Od:'........''''.......'ck00K
kkkkxxxxxdxxxddddddddxxd:....;dkO000KKKKKKKXXXXXXXXXXXXXXXXXXXXXXXXKK000Od:..........''.......'oO00K
OOOOOkxdddxxxddddxxxxxxc....;okOO0000KKKKKKKKKKKKKKKKKKKKKKKKKXXXXXKKK000Oo;...   ............;x00KK
OOOOOOkxxxxxddddddxxxxo'...'lkOO000000000KKKK000OkkkxxxxxkkO000KKKKKKKK000ko,..     ..........:k00KK
OOOOkkkkxxxxddddddxxxd,. ..:xOO000OOOOOOOO000OOkxdooooddxkO0000KKK00000000Okl,.      ....  ...lO00KK
Okkxxxxxxxxddddddxdxx:.  ..lxxxxdooooodxxkOOOOkxdoooodxOO00KKKKKK00OOO00000Oxc'.     ...     'd000KK
kxxddddxxxxddddddddxl. ...,loolllllllllodxkkkkkxdddddxxkkkkkkkkOOOOOOO000000Od:..    ...     ;k00KKK
xddddxddxxdddddddddo,. ...:oodxxxxddoooodkOOOOOkdddddol:;,''',;cldxkkOO00000Oko;.    ..     .cO000KK
ddddxxddxxdddddddddc. . .'ldxkOOOOkxdoooxO0KKK0Oxdool:;,;;::c::;,;coxkO000000Okl,.          .d0000KK
xxxxxdddxxxddddoodl'  . .;oxxxdolccccllok0KXXXKK0kkdolclodddxkkOkkkkO0KKKKK00OOxc.          ,k0000KK
ddddddddxxdddddddo;.  . .:ooc;'''',,;cok0KXXXXXKKKK0OkxddddxkO0KKXXXXXXXKKKK00Okl,.         cO000KKK
oodddddxxxdddoodd:.     .cl:;:cllllloxk0KXXXXKXXXXXXXXXKKKKKXXXXXXXXXXXXXKKK0OOko;.        .o0000KKK
oodddddxxxddodddl'      .cccodoolodxO00KKXXKKKKKKKKKKXXXXXXXXXXXXXXXXXXKKKK00Okxo;.        ,x0000KKK
oddddddxxdddoodl,.      ,oxOOOO000K0000KKKKKKKKK0OkkO0KKXXXXXXXXXXXXKKKKK000Okkdl,.        :O0000K00
oddddddddddoooo;..     .o0KKKKKKK0OOOOkkkkkkO0KKK0OkxxO0KKKXXXXXXKKKKKK00OOOkxxdc,.       .oO0000000
ddddddddxddooo:...    .c0KKKKKK0OkkkxdollllllodxkkxxxxxkO0KKKKKKKKKK000OOOkkxddo:'.       ,xO0000000
ddxdddddddoooc...     'kKKKK000Okxdo:;,;;;;,'.';:cldkOkxxkO000000000OOOOkkxxdooc;.        cOO0000000
dxddddddddooc'.,.     cO0000OOkxddol:,,;:::ccccloxkOKK0xdxxkkOOOOOOOOkkkkxxddolc,.       .oOO0000000
ddddddddddol,.,;.    .lOOOkkkxxddxxdooodxkOO00OO00KKKKKOxddxxxxxxxkkkkkxxxxdoll:,..      'xOO0000000
dddddddddol;.':,     .lxxxxxxddddkkkxxxxddddxxk00KKKKK00xdoddxxxxxxxxxxxxxxdoll:,..      :OO00000000
ddddddddooc..::.     .:ooooooolloxkkxl:;,,,,,,;:lodxkOOkxdoddxxxxxxxkkkkxxxdool:'.      .oOO00000000
ddddddddol'.;c;.      ,lollllccclddl:,',;;::::;;,;;;:coddooddxxxxxxxkkkkxxxdolc;'...    ,xO000000000
ddddddddo;.,cc,.      .clllllc:::c;,,;:llooodlc:,'''..';lodxxxxxxxxxxkxxxxdool:,.''..   ,c::;',:lc:c
ddddddooc..cl:'.       ;llllllc:;,..',,'',,;,,''.....,:codxxxxxxxxxxxxxxddoolc;'..'..               
ddoooool,.;ll;.        .cllllll:;;'..'',:loddddoollloxkkkkxxxxxdddddddddoollc:,..                   
doooooo:.,llc,.        .:lllllllcccllodxxxddooooddxxkOOOOkkxxddddddooooollcc:;'.                    
doooooc..col:'          .clllllllooolc:::;;;;cloxkkkOOOOOOkxxddooooollllcc::;'.                  .. 
dooooo,.;lol;.           'clllllooddolc::::cloxkOOOOOOOOOOkxdooollllccc:::;;,.                      
oooooc.'lllc'.            .:llloodxxdolllllodxkOO00000OOkkxdoollllcc:::;;;,,..                      
ooooo,.:oll:.              .;cllodxkxxxdddxxkOO000OOOOkkxdoollllcc::;;;;,,,'.                       
ooooc',llll;.                ':lodxkkkkkkkkOOOOOkkkkxxddollccccc::;;;;;,,,'..                       
oooo;'collc'                  .,:lodxxxxxxxxxxxddddoollccc:::::;;;;;;;;;;,'..                       
,,;;':dddoc.                    .,:loooooolollllllccc:::;;;;;;,,,,;;;;::;;'...                      
..';;oOOkxc.                      ..;ccc::::::::;;;;;;,,,,,,,,,,;;;::::::;,...                      
;cdo:dOOkd,.                         .',,,,,,,,,,,,,,,,,,,,,,,;;;:::ccccc;,....                     
O00dcx00Oo'                             .'''''''',,,,,,,,,,,;;;:::ccclllc:,'....                    
000dlkK0Ol.           ..   ..            ..'''''',,,,,,,,,;;;:::cccllllll:;,'''.                    
00KxlxK0x;.           .....''.             .,,,,,,,,,,,,,;;:::cccllllllolc;,,,''.                   
00KOlxK0o'...         ...;:co;             .',;;,,,,,,,;;;::ccclllloooooolc:;;,,..                  
KKK0dx0kc......       ..;kklxk'             .,;;;;;;,,;;:::ccllllooooooooolcc::;,..                 
KKKKOxkd,.......      ..oKKdd0o.             ';;;;;;;;;;::ccllloooooooddddoollcc:;'.                
KKKK0kdl'....... .    .ck0X0dkk,             .,;;;;;;;;:::ccllloooooddddddddooollc:,..              
XXXXKOo;...........   .cO0KXOol'             .,;;;;;;;;::ccclllooooddddxxxxxddddddolc;,'.           
NNNXX0o'.......... .,:,.ckkko'.               ';:::::::::cccllloooodddxxxxxxxxkkkkkkxollc;'.        
NNNNN0c............;OKd,.','.                 .;:::::::::cclllllooodddxxxxxkkkOO00000OOkdlclc,.     
NNNNXk,............dXKOl.                     .;::::::::cccllllllooodddxxkkkOO0000KK00000OkOOOxl;.  
WWNNXx'...........,OX0x:.                     .,::::::cccccllllllloooddxxkOO0000KKKKKKKKKKKK0Okxdl;.
WWNNXd'...........:xo,.                       .,;:::::ccccclllllllooodxxkOO000KKKKKKKKK0Okdoc:,'....
NNNNKo'.............                          .,;::::ccccclllllllooodxxkkOO000KKKKK0kdlc;'..........
XXXX0l'. .........                           ..,;;:::ccccllllllooodxxkkOOO000KK0Odl;,'.....    .....
coxOkc'.  ........                          ..',;;::ccccllllloooddxkkOOO0000Oxl:,........  .........
'',;::,.   .......                         ..',;;:::ccllllooooddxxkkOOO00Odc;'.........  .......'...
kdddxo;.    ......                        .',,;;::ccclllooooddxxkkOOO0Odc,........... ...'..........
0KXXXO:..    .   ..                       ';:::cclllllooodddxxkkOOOOxl,........  .. ................
NNWWNO;...        ..                     .;cccllllloooodddxxkkkOOxl;......... ......................
NWWNO:....        ...                   .,ccclllloooooddxxkkkOko:'.........  ............''.........
WWXk:......        ..                   .;cllllloooooddxxkkkdc,...........  .........'''............
WXx:'.....          ...                 ':llllooooodddxxkxo;.............    .....'''...............
N0l,'.....  ...............            .,clllooooddddxxdc,.............      .......................
Ko,''................'cxkkxdlc;,'..    .;cllloooddddxdc'..............      ........................
x,..'...............'l0KKKKKKKKK0Oxdl:;;:cllooooddxo:'..............       .........................
;...................cOKKKKKKKKKKKKKXXK0Okxdoooool:,'...............   .   ..........................
'..................,dKKKKKKKKKKKKKKKKKKKKKKOxdl:'.........   .....   .   ...........................
...................:OKKKKKKKKKKKKKKKKKKKKK000Ol'.....    .. ....   ..   ............................
..................'o0KKKKKKKKKKKKKKKKKKKK0OO0K0d:...          .   ..   .............................
..   .............,xK0KKKKKKKKKKK00OOO0000OOO0000kxo;'..         ..   ..............................
       ...........:O000000000KKKK0OkkxkO000Okk000000Okkxl'.     ..   ...............................
              ....:k00000000OOOOOOOOkdxkOO00Okk00000xl:;,.    ...   ................................
                 .,dkO0000OOkxxkkOOOOxodxkOO0OkkO000Ox;.     ...   .................................
                  .cdxkOOOkkxdodxxkOOOkddxkkOOOkxkOOOOkc.  ...    ..................................
                  .,cloddxxxxxoccoxkOOOOxddxkkOOkdddkkO0o'...    ...................................
                    .,:lloodxkko;;ldxkOOOkoodxkOOxllok000x,.    ....................................
                     ..';clodxkko''codxkOOkolodxxl:,,lkO00x;.  .....................................
                    .....';coodxko'.,coxkkOxc,;;,....'cdk00Oc.......................................
                    ........;lodxkd'..:loooc,..........cxO0K0o'.....................................
                     ....    ':loddc. .;;,''.....  .   .;oOKX0c.....................................
                              .,::;;'..,,''...........  .'lk0Ko,''''................................
                               .;ccc::cccc::;;;;;;;;:;;;;;clodoccccc'...............................
                                                          ..........................................

    """

# ========== 主程序 ==========

def roles(role_name):
    """
    角色系统：整合人格设定和记忆加载
    
    这个函数会：
    1. 加载角色的外部记忆文件（如果存在）
    2. 获取角色的基础人格设定
    3. 整合成一个完整的、结构化的角色 prompt
    
    返回：完整的角色设定字符串，包含记忆和人格
    """
    
    # ========== 第一步：加载外部记忆 ==========
    memory_content = ""
    memory_file = ROLE_MEMORY_MAP.get(role_name)
    
    if memory_file:
        memory_path = os.path.join(MEMORY_FOLDER, memory_file)
        try:
            if os.path.exists(memory_path):
                with open(memory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 处理数组格式的聊天记录：[{ "content": "..." }, { "content": "..." }, ...]
                    if isinstance(data, list):
                        # 提取所有 content 字段，每句换行
                        contents = [item.get('content', '') for item in data if isinstance(item, dict) and item.get('content')]
                        memory_content = '\n'.join(contents)
                    # 处理字典格式：{ "content": "..." }
                    elif isinstance(data, dict):
                        memory_content = data.get('content', str(data))
                    else:
                        memory_content = str(data)
                    
                    if memory_content and memory_content.strip():
                        # Streamlit 中使用 st.write 或静默加载
                        pass  # 记忆加载成功，不需要打印
                    else:
                        memory_content = ""
            else:
                pass  # 记忆文件不存在，静默处理
        except Exception as e:
                pass  # 加载失败，静默处理
    
    # ========== 第二步：获取基础人格设定 ==========
    role_personality = {
          "悠扬": """
        【人格特征】
        你是一个大学生：
        - **外向开朗**：你总是喜欢"哈哈哈哈"等大笑表达来展现自己的情绪
        - **灵活应变**：你善于说一些似真似假的话
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
    
    personality = role_personality.get(role_name, "你是一个普通的人，没有特殊角色特征。")
    
    # ========== 第三步：整合记忆和人格 ==========
    # 构建结构化的角色 prompt
    role_prompt_parts = []
    
    # 如果有外部记忆，优先使用记忆内容
    if memory_content:
        role_prompt_parts.append(f"""【你的说话风格示例】
以下是你说过的话，你必须模仿这种说话风格和语气：

{memory_content}

在对话中，你要自然地使用类似的表达方式和语气。""")
    
    # 添加人格设定
    role_prompt_parts.append(f"【角色设定】\n{personality}")
    
    # 整合成完整的角色 prompt
    role_system = "\n\n".join(role_prompt_parts)
    
    return role_system

# 【结束对话规则】
break_message = """【结束对话规则 - 系统级强制规则】

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

# ========== Streamlit Web 界面 ==========
st.set_page_config(
    page_title="你好,悠扬!",
    page_icon="❀",
    layout="wide"
)

# 初始化 session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "selected_role" not in st.session_state:
    st.session_state.selected_role = "人质"
if "initialized" not in st.session_state:
    st.session_state.initialized = False

# 页面标题
st.title(❀ 你好,悠扬!")
st.markdown("---")

# 侧边栏：角色选择和设置
with st.sidebar:
    st.header("⚙️ 设置")
    
    # 角色选择
    selected_role = st.selectbox(
        "选择角色",
        ["悠扬", "你"],
        index=0 if st.session_state.selected_role == "悠扬" else 1
    )
    
    # 如果角色改变，重新初始化对话
    if selected_role != st.session_state.selected_role:
        st.session_state.selected_role = selected_role
        st.session_state.initialized = False
        st.session_state.conversation_history = []
        st.rerun()
    
    # 清空对话按钮
    if st.button("🔄 清空对话"):
        st.session_state.conversation_history = []
        st.session_state.initialized = False
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📝 说明")
    st.info(
        "- 选择角色后开始对话\n"
        "- 对话记录不会保存\n"
        "- AI的记忆基于初始记忆文件"
    )

# 初始化对话历史（首次加载或角色切换时）
if not st.session_state.initialized:
    role_system = roles(st.session_state.selected_role)
    system_message = role_system + "\n\n" + break_message
    st.session_state.conversation_history = [{"role": "system", "content": system_message}]
    st.session_state.initialized = True

# 显示对话历史
st.subheader(f"💬 与 {st.session_state.selected_role} 的对话")

# 显示角色头像（在聊天窗口上方）
st.code(get_portrait(), language=None)
st.markdown("---")  # 分隔线

# 显示历史消息（跳过 system 消息）
for msg in st.session_state.conversation_history[1:]:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(msg["content"])

# 用户输入
user_input = st.chat_input("输入你的消息...")

if user_input:
    # 检查是否结束对话
    if user_input.strip() == "再见":
        st.info("对话已结束")
        st.stop()
    
    # 添加用户消息到历史
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    
    # 显示用户消息
    with st.chat_message("user"):
        st.write(user_input)
    
    # 调用API获取AI回复
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                result = call_zhipu_api(st.session_state.conversation_history)
                assistant_reply = result['choices'][0]['message']['content']
                
                # 添加AI回复到历史
                st.session_state.conversation_history.append({"role": "assistant", "content": assistant_reply})
                
                # 显示AI回复
                st.write(assistant_reply)
                
                # 检查是否结束
                reply_cleaned = assistant_reply.strip().replace(" ", "").replace("！", "").replace("!", "").replace("，", "").replace(",", "")
                if reply_cleaned == "再见" or (len(reply_cleaned) <= 5 and "再见" in reply_cleaned):
                    st.info("对话已结束")
                    st.stop()
                    
            except Exception as e:
                st.error(f"发生错误: {e}")
                st.session_state.conversation_history.pop()  # 移除失败的用户消息

