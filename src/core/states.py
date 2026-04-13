from enum import Enum, auto

class MainState(Enum):
    """Main FSM: 逻辑与锁控制循环"""
    INIT = auto()              # 初始化中
    IDLE = auto()              # 空闲，等待输入
    BUSY_COGNITION = auto()    # 认知中（锁定终端）
    BUSY_SYSTEM = auto()       # 系统维护/指令中（如重置DB、加载预设）
    BUSY_MAINTENANCE = auto()  # 维护/切片中
    FAULT = auto()             # 故障处理
    SHUTDOWN = auto()          # 退出流程（存档与关闭服务）

    @property
    def allows_background_io(self) -> bool:
        """策略声明：当前状态是否允许外挂服务进行数据库读写"""
        # 仅在 IDLE 状态下允许后台服务运行，其余所有忙碌或维护状态均按停服务
        return self == MainState.IDLE

class AgentState(Enum):
    """Agent FSM: 认知与行为循环"""
    SLEEPING = auto()          # 睡眠/等待信号
    MAIN_TOOL = auto()         # 意图识别/工具触发
    SUB_LOOP = auto()          # MCP工具调用子循环
    MAIN_HIDDEN = auto()       # 隐藏逻辑链生成
    MAIN_FORMAL = auto()       # 最终自然语言生成
