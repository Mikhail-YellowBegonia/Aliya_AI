import os
from core.states import AgentState
from database.db_manager import DBManager

class SubContextAssembly:
    """Sub Agent 专用的上下文组装器"""
    def __init__(self, db: DBManager):
        self.db = db
        self.sub_prompt = (
            "你是一个子任务执行模块（Sub Agent）。你的目标是根据最新的对话需求，"
            "合理使用工具并处理信息。请保持逻辑严密，并在任务完成时使用 [SUB QUIT] 标记。"
        )

    def _get_last_record(self) -> str:
        """获取最后一条历史记录 (Last History)"""
        query = "SELECT role, content FROM chat_records ORDER BY order_index DESC LIMIT 1"
        result = self.db.execute(query)
        if not result:
            return ""
        role, content = result[0]
        return f"### 核心需求 (Context Slicer 提取项) ###\n{role}: {content}"

    def _get_subsession(self, session_id: str) -> str:
        """获取当前子循环的私有上下文 (Subsession)"""
        query = "SELECT role, content FROM sub_sessions WHERE session_id = ? ORDER BY order_index ASC"
        results = self.db.execute(query, (session_id,))
        if not results:
            return ""
        chain = "\n".join([f"{r[0]}: {r[1]}" for r in results])
        return f"### 子任务逻辑链 (Subsession) ###\n{chain}"

    def _get_meta(self) -> str:
        """获取 [0] Meta: 动态环境感知"""
        query = "SELECT key, value FROM meta_cache"
        results = self.db.execute(query)
        if not results:
            return ""
        meta_items = [f"[{r[0]}: {r[1]}]" for r in results]
        return "当前环境状态: " + " ".join(meta_items)

    def assemble(self, session_id: str) -> str:
        """组装 Sub Agent 的上下文"""
        # 顺序: Last History + Sub Prompt + Subsession + [0]
        segments = [
            self._get_last_record(),
            f"### 子任务指令 (Sub Prompt) ###\n{self.sub_prompt}",
            self._get_subsession(session_id),
            f"### 实时环境 ###\n{self._get_meta()}"
        ]
        # 过滤掉空段落并合并
        return "\n\n".join([s for s in segments if s.strip()])

class SubAgent:
    """Sub Agent 核心类"""
    def __init__(self, db: DBManager):
        self.db = db
        self.assembler = SubContextAssembly(db)

    def process_step(self, session_id: str):
        """执行一个子循环迭代（占位）"""
        context = self.assembler.assemble(session_id)
        
        # TODO: 调用 LiteLLM 进行推理
        # TODO: 拦截 Action 并调用 MCP
        
        return context

# ---------------------------------------------------------
# 测试输出
# ---------------------------------------------------------
if __name__ == "__main__":
    db = DBManager("aliya.db")
    db.connect()
    
    # 构造一些测试数据
    # 1. 模拟最后一条历史 (万字级别占位)
    db.execute_and_commit("INSERT INTO chat_records (role, content, order_index, is_archived) VALUES (?, ?, ?, ?)", 
                         ('user', '请帮我查一下北京明天的天气，并结合我之前提到的旅游计划给出建议。' * 10, 100, 0))
    
    # 2. 模拟 Subsession
    session_id = "test_task_001"
    db.execute_and_commit("INSERT INTO sub_sessions (session_id, role, content, order_index) VALUES (?, ?, ?, ?)",
                         (session_id, 'assistant', '正在调用搜索工具...', 1))
    db.execute_and_commit("INSERT INTO sub_sessions (session_id, role, content, order_index) VALUES (?, ?, ?, ?)",
                         (session_id, 'tool', '{"result": "北京明天晴，10-20度"}', 2))

    # 3. 模拟 Meta [0]
    db.execute_and_commit("INSERT OR REPLACE INTO meta_cache (key, value) VALUES (?, ?)", ('time', '2024-03-21'))

    agent = SubAgent(db)
    print("="*30)
    print("SUB AGENT CONTEXT ASSEMBLY TEST")
    print("="*30)
    print(agent.process_step(session_id))
    print("="*30)

    db.close()
