import sys
import time
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from core.states import MainState, AgentState

# 加载 .env
load_dotenv()

console = Console()

class AliyaApp:
    def __init__(self):
        self.state = MainState.INIT
        self.agent_state = AgentState.SLEEPING
        self._is_running = True
        self.last_command = None
        
        # 从配置加载，提供默认值
        self.db_path = os.getenv("DB_PATH", "aliya.db")
        self.user_name = os.getenv("USER_NAME", "User")
        self.aliya_name = os.getenv("ALIYA_NAME", "Aliya")

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
            elif self.state == MainState.BUSY_SYSTEM:
                self.handle_system()
            elif self.state == MainState.BUSY_MAINTENANCE:
                self.handle_maintenance()
            elif self.state == MainState.FAULT:
                self.handle_fault()
            elif self.state == MainState.SHUTDOWN:
                self.handle_shutdown()

    def handle_idle(self):
        """IDLE 状态：接收用户输入"""
        try:
            # 简单模拟，后续可改用 prompt_toolkit 增强
            user_input = console.input("[bold magenta]User > [/]")
            if not user_input.strip():
                return
            
            # 退出指令优先级最高
            if user_input.lower() in ["exit", "quit", "退出"]:
                self.state = MainState.SHUTDOWN
                return

            # 检测到系统指令 (/reset, /status 等)
            if user_input.startswith("/"):
                self.last_command = user_input
                self.state = MainState.BUSY_SYSTEM
                return

            # 普通对话消息
            self.state = MainState.BUSY_COGNITION
            console.print(Panel("已锁定终端输入 (LOCK_INPUT)", style="yellow dim"))
            
        except KeyboardInterrupt:
            self.state = MainState.SHUTDOWN

    def handle_system(self):
        """BUSY_SYSTEM 状态：处理非对话类系统指令"""
        cmd = self.last_command.lower().strip()
        console.print(f"[bold yellow]正在执行系统指令: {cmd}[/]")

        # 模拟高危 DB 操作
        if cmd == "/reset":
            console.print("[dim]→ 正在释放数据库连接以防止死锁...")
            # TODO: db_manager.close()
            time.sleep(0.5)
            console.print("[dim]→ 正在重建数据库表结构...")
            time.sleep(0.5)
            console.print("[bold green]✓ 数据库已重置并重新连接。[/]")
        
        elif cmd == "/status":
            console.print(Panel(
                f"Main FSM : [cyan]{self.state.name}[/]\nAgent FSM: [cyan]{self.agent_state.name}[/]", 
                title="Aliya 系统监控", 
                border_style="blue"
            ))

        else:
            console.print(f"[red]未知或尚未实现的系统指令: {cmd}[/]")

        # 任务完成，平滑返回 IDLE
        self.state = MainState.IDLE
        console.print(Panel("已解锁终端输入 (UNLOCK_INPUT)", style="green dim"))

    def handle_shutdown(self):
        """SHUTDOWN 状态：关闭服务并存档流程"""
        console.print("\n[bold red]正在启动退出流程...[/]")
        
        # 1. 关闭后台服务（如 MetaFetcher）
        console.print("[dim]→ 正在停止后台元数据同步服务...[/]")
        # TODO: 这里应向后台线程发送停止信号
        time.sleep(0.5)
        
        # 2. 数据库存档
        console.print("[dim]→ 正在存档工作记忆与状态...[/]")
        # TODO: 执行 DB 最后的 commit 和备份
        time.sleep(0.5)
        
        # 3. 释放资源
        console.print("[dim]→ 正在释放资源...[/]")
        
        console.print("[bold green]✓ Aliya 系统已完全关闭。[/]")
        self._is_running = False

    def handle_cognition(self):
        """BUSY_COGNITION 状态：Agent 认知循环"""
        console.print("[cyan]Aliya 正在思考... (BUSY_COGNITION)[/]")
        
        # 演示 Agent 内部状态对齐
        self.agent_state = AgentState.MAIN_TOOL
        time.sleep(0.4)
        
        self.agent_state = AgentState.MAIN_HIDDEN
        time.sleep(0.4)
        
        self.agent_state = AgentState.MAIN_FORMAL
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
