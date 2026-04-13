import sys
import time
from rich.console import Console
from rich.panel import Panel
from core.states import MainState, AgentState

console = Console()

class AliyaApp:
    def __init__(self):
        self.state = MainState.INIT
        self.agent_state = AgentState.SLEEPING
        self._is_running = True

    def initialize(self):
        """对应 INIT -> IDLE"""
        console.print("[bold blue]Aliya[/] 系统初始化中...", style="italic")
        # 模拟加载数据库和配置
        time.sleep(1) 
        self.state = MainState.IDLE
        console.print("[bold green]✓[/] 系统已就绪，进入 IDLE 状态。\n")

    def run(self):
        self.initialize()
        
        while self._is_running:
            if self.state == MainState.IDLE:
                self.handle_idle()
            elif self.state == MainState.BUSY_COGNITION:
                self.handle_cognition()
            elif self.state == MainState.BUSY_MAINTENANCE:
                self.handle_maintenance()
            elif self.state == MainState.FAULT:
                self.handle_fault()

    def handle_idle(self):
        """IDLE 状态：接收用户输入"""
        try:
            # 简单模拟，后续可改用 prompt_toolkit 增强
            user_input = console.input("[bold magenta]User > [/]")
            if not user_input.strip():
                return
            if user_input.lower() in ["exit", "quit", "退出"]:
                self._is_running = False
                return

            # IDLE -> BUSY_COGNITION (收到消息，锁定输入)
            self.state = MainState.BUSY_COGNITION
            console.print(Panel("已锁定终端输入 (LOCK_INPUT)", style="yellow dim"))
            
        except KeyboardInterrupt:
            self._is_running = False

    def handle_cognition(self):
        """BUSY_COGNITION 状态：Agent 认知循环"""
        console.print("[cyan]Aliya 正在思考... (BUSY_COGNITION)[/]")
        
        # 演示 Agent 内部状态对齐
        self.agent_state = AgentState.MAIN_TOOL
        # 模拟意图识别
        time.sleep(0.4)
        
        self.agent_state = AgentState.MAIN_HIDDEN
        # 模拟潜意识逻辑生成
        time.sleep(0.4)
        
        self.agent_state = AgentState.MAIN_FORMAL
        # 模拟最终语言生成
        time.sleep(0.4)
        
        console.print("\n[bold blue]Aliya:[/][italic] 唔... 我听到了。目前我只是一个状态机骨架，等我的数据库和 LLM 接口接通后，我就能真的和你聊天了。[/]\n")
        
        # BUSY_COGNITION -> BUSY_MAINTENANCE
        self.state = MainState.BUSY_MAINTENANCE
        self.agent_state = AgentState.SLEEPING

    def handle_maintenance(self):
        """BUSY_MAINTENANCE 状态：对话切片与持久化"""
        console.print("[dim]正在进行认知维护与记忆切片... (BUSY_MAINTENANCE)[/]")
        time.sleep(0.5)
        
        # BUSY_MAINTENANCE -> IDLE (解锁输入)
        self.state = MainState.IDLE
        console.print(Panel("已解锁终端输入 (UNLOCK_INPUT)", style="green dim"))

    def handle_fault(self):
        """FAULT 状态：紧急恢复"""
        console.print("[bold red]系统发生严重故障！[/] 正在尝试重启...")
        time.sleep(1)
        self.state = MainState.IDLE

if __name__ == "__main__":
    # 为了能直接 import src 下的模块，将 src 加入 sys.path
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
    
    app = AliyaApp()
    app.run()
