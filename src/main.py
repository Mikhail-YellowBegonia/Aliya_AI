import sys
import time
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# 核心组件导入
from core.states import MainState, AgentState
from core.assembly import ContextAssembly
from core.sub_agent import SubAgent
from database.db_manager import DBManager
from utils.llm_client import LLMClient

# 加载 .env
load_dotenv()

console = Console()

class AliyaApp:
    def __init__(self):
        # 1. 状态管理
        self.state = MainState.INIT
        self.agent_state = AgentState.SLEEPING
        self._is_running = True
        self.last_command = None
        
        # 2. 配置与数据库
        self.db_path = os.getenv("DB_PATH", "aliya.db")
        self.db = DBManager(self.db_path)
        
        # 3. 核心功能对象 (Data Model 占位)
        self.llm = LLMClient()
        self.assembler = ContextAssembly(self.db)
        self.sub_agent = SubAgent(self.db)

    def initialize(self):
        """对应 INIT -> IDLE"""
        console.print("[bold blue]Aliya[/] 系统初始化中...", style="italic")
        self.db.connect()
        # TODO: 启动 MetaFetcher 后台线程
        time.sleep(0.5) 
        self.state = MainState.IDLE
        console.print("[bold green]✓[/] 系统已就绪，进入 IDLE 状态。\n")

    def run(self):
        self.initialize()
        while self._is_running:
            if self.state == MainState.IDLE:
                self.handle_idle()
            elif self.state == MainState.BUSY_COGNITION:
                self.handle_cognition()
            elif self.state == MainState.BUSY_SYSTEM:
                self.handle_system()
            elif self.state == MainState.BUSY_MAINTENANCE:
                self.handle_maintenance()
            elif self.state == MainState.FAULT:
                self.handle_fault()
            elif self.state == MainState.SHUTDOWN:
                self.handle_shutdown()

    def handle_idle(self):
        """接收输入并判定流转"""
        try:
            user_input = console.input("[bold magenta]User > [/]")
            if not user_input.strip(): return
            
            if user_input.lower() in ["exit", "quit", "退出"]:
                self.state = MainState.SHUTDOWN
                return

            if user_input.startswith("/"):
                self.last_command = user_input
                self.state = MainState.BUSY_SYSTEM
                return

            # 进入正式对话流程
            # 记录用户输入到 DB (占位)
            # self.db.execute_and_commit(...)
            self.state = MainState.BUSY_COGNITION
            console.print(Panel("已锁定终端输入 (LOCK_INPUT)", style="yellow dim"))
            
        except KeyboardInterrupt:
            self.state = MainState.SHUTDOWN

    def handle_cognition(self):
        """核心认知模型：3-Iteration Cycle"""
        console.print("[cyan]Aliya 正在思考... (BUSY_COGNITION)[/]")
        
        # --- Stage 1: MAIN_TOOL ---
        self.agent_state = AgentState.MAIN_TOOL
        context_tool = self.assembler.assemble(self.agent_state)
        # TODO: 意图识别判断是否进入 SUB_LOOP
        # has_tool_intent = self._detect_tool_intent(context_tool)
        has_tool_intent = False # 模拟占位
        
        # --- Stage 2: SUB_LOOP (Optional) ---
        if has_tool_intent:
            self.agent_state = AgentState.SUB_LOOP
            # TODO: sub_agent.process_step()
            pass

        # --- Stage 3: MAIN_HIDDEN ---
        self.agent_state = AgentState.MAIN_HIDDEN
        context_hidden = self.assembler.assemble(self.agent_state)
        # TODO: self.llm.ask(context_hidden) -> 存入内心独白缓存
        time.sleep(0.2)

        # --- Stage 4: MAIN_FORMAL ---
        self.agent_state = AgentState.MAIN_FORMAL
        context_formal = self.assembler.assemble(self.agent_state)
        # TODO: self.llm.ask(context_formal) -> 生成拟人回复
        console.print("\n[bold blue]Aliya:[/][italic] (正在生成回复...) [/]\n")
        
        # 任务结束，流转到维护状态
        self.state = MainState.BUSY_MAINTENANCE
        self.agent_state = AgentState.SLEEPING

    def handle_maintenance(self):
        """持久化与善后"""
        console.print("[dim]正在进行认知维护与记忆切片... (BUSY_MAINTENANCE)[/]")
        # TODO: 存储 AI 回复到 DB
        # TODO: 检查是否需要 Slice
        time.sleep(0.3)
        self.state = MainState.IDLE
        console.print(Panel("已解锁终端输入 (UNLOCK_INPUT)", style="green dim"))

    def handle_system(self):
        """系统指令处理模型"""
        cmd = self.last_command.lower().strip()
        console.print(f"[bold yellow]执行系统指令: {cmd}[/]")
        # TODO: 根据 cmd 分发到具体逻辑
        self.state = MainState.IDLE

    def handle_shutdown(self):
        """退出善后模型"""
        console.print("\n[bold red]正在启动退出流程...[/]")
        self.db.close()
        self._is_running = False

    def handle_fault(self):
        self.state = MainState.IDLE

if __name__ == "__main__":
    # 路径对齐
    sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
    app = AliyaApp()
    app.run()
