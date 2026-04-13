import sys
from core.states import AgentState
from database.db_manager import DBManager

class ContextAssembly:
    def __init__(self, db: DBManager):
        self.db = db

    def _get_prompts(self) -> str:
        """获取 [-N] Prompt Slices: 静态系统层"""
        query = "SELECT content FROM prompts ORDER BY priority DESC, id ASC"
        results = self.db.execute(query)
        return "\n".join([r[0] for r in results])

    def _get_history_and_cache(self, exclude_last_user: bool = True):
        """
        获取 [+N] History 和 [Cache] Working Memory
        - exclude_last_user: 是否排除最后一条用户消息（为了单独作为 Cache* 放在最末尾）
        """
        # 1. 获取长期历史 [+N]
        history_query = "SELECT role, content FROM chat_records WHERE is_archived = 1 ORDER BY order_index ASC"
        history_data = self.db.execute(history_query)
        history_str = "\n".join([f"{r[0]}: {r[1]}" for r in history_data])

        # 2. 获取近期记忆 [Cache]
        cache_query = "SELECT id, role, content FROM chat_records WHERE is_archived = 0 ORDER BY order_index ASC"
        cache_data = self.db.execute(cache_query)
        
        cache_list = []
        last_user_msg = None
        
        if exclude_last_user:
            # 找到最后一条用户消息
            for i in range(len(cache_data) - 1, -1, -1):
                if cache_data[i][1] == 'user':
                    last_user_msg = f"User: {cache_data[i][2]}"
                    # 移除这一条，不让它出现在中间的 [Cache] 中
                    cache_data.pop(i)
                    break
        
        cache_str = "\n".join([f"{r[1]}: {r[2]}" for r in cache_data])
        
        return history_str, cache_str, last_user_msg

    def _get_meta(self) -> str:
        """获取 [0] Meta: 动态环境感知"""
        query = "SELECT key, value FROM meta_cache"
        results = self.db.execute(query)
        if not results:
            return ""
        meta_items = [f"[{r[0]}: {r[1]}]" for r in results]
        return "当前环境状态: " + " ".join(meta_items)

    def _get_scratchpad(self) -> str:
        """获取 [S] Scratchpad: 阅后即焚便签（清洗后的自然语言）"""
        query = "SELECT content FROM ephemeral_scratch ORDER BY id ASC"
        results = self.db.execute(query)
        if not results:
            return ""
        return "\n".join([f"补充信息: {r[0]}" for r in results])

    def assemble(self, agent_state: AgentState) -> str:
        """根据当前 Agent 状态组装最终的上下文文本"""
        
        # 1. [-N] Prompts
        prompts = self._get_prompts()
        
        # 2. [+N] History & [Cache] Working Memory
        # 同时提取出 [Cache*] (Latest Stimulus)
        history, cache, last_stimulus = self._get_history_and_cache(exclude_last_user=True)
        
        # 3. [0] Meta
        meta = self._get_meta()
        
        # 4. [S] Scratchpad
        scratch = self._get_scratchpad()

        # 按照特定顺序缝合
        # 预期顺序: [-N] > [+N] > [Cache] > [0] > [S] > [Cache*]
        segments = []
        if prompts: segments.append(f"### 系统指令 ###\n{prompts}")
        if history: segments.append(f"### 长期记忆 ###\n{history}")
        if cache: segments.append(f"### 近期对话 ###\n{cache}")
        if meta: segments.append(f"### 环境状态 ###\n{meta}")
        if scratch: segments.append(f"### 检索信息 ###\n{scratch}")
        if last_stimulus: segments.append(f"### 当前输入 ###\n{last_stimulus}")
        
        full_context = "\n\n".join(segments)
        return full_context

# ---------------------------------------------------------
# 测试函数 (按照要求直接 print)
# ---------------------------------------------------------
def test_assembly():
    db = DBManager("aliya.db")
    db.connect()
    
    # 清理并预置一些测试数据
    db.execute("DELETE FROM prompts")
    db.execute("DELETE FROM chat_records")
    db.execute("DELETE FROM meta_cache")
    db.execute("DELETE FROM ephemeral_scratch")
    
    # [-N]
    db.execute_and_commit("INSERT INTO prompts (slug, content, priority) VALUES (?, ?, ?)", 
                         ('core', '你是一个温柔的AI助手。', 10))
    db.execute_and_commit("INSERT INTO prompts (slug, content, priority) VALUES (?, ?, ?)", 
                         ('skill', '你擅长查天气。', 5))
    
    # [+N]
    db.execute_and_commit("INSERT INTO chat_records (role, content, order_index, is_archived) VALUES (?, ?, ?, ?)", 
                         ('user', '你好', 1, 1))
    db.execute_and_commit("INSERT INTO chat_records (role, content, order_index, is_archived) VALUES (?, ?, ?, ?)", 
                         ('assistant', '你好呀', 2, 1))
    
    # [Cache]
    db.execute_and_commit("INSERT INTO chat_records (role, content, order_index, is_archived) VALUES (?, ?, ?, ?)", 
                         ('user', '今天心情不错', 3, 0))
    db.execute_and_commit("INSERT INTO chat_records (role, content, order_index, is_archived) VALUES (?, ?, ?, ?)", 
                         ('assistant', '听起来太棒了', 4, 0))
    
    # [Cache*] - 最后一条用户输入
    db.execute_and_commit("INSERT INTO chat_records (role, content, order_index, is_archived) VALUES (?, ?, ?, ?)", 
                         ('user', '告诉我今天天气怎么样', 5, 0))
    
    # [0] Meta
    db.execute_and_commit("INSERT INTO meta_cache (key, value) VALUES (?, ?)", ('weather', '晴朗'))
    
    # [S] Scratch
    db.execute_and_commit("INSERT INTO ephemeral_scratch (content) VALUES (?)", ('我发现北京目前气温20度。',))
    
    assembler = ContextAssembly(db)
    result = assembler.assemble(AgentState.MAIN_FORMAL)
    
    print("="*30)
    print("ALIYA CONTEXT ASSEMBLY RESULT")
    print("="*30)
    print(result)
    print("="*30)
    
    db.close()

if __name__ == "__main__":
    test_assembly()
