from enum import Enum, auto

class MainState(Enum):
    """Main FSM: 逻辑与锁控制循环"""
    INIT = auto()              # 初始化中
    IDLE = auto()              # 空闲，等待输入
    BUSY_COGNITION = auto()    # 认知中（锁定终端）
    BUSY_MAINTENANCE = auto()  # 维护/切片中
    FAULT = auto()             # 故障处理

class AgentState(Enum):
    """Agent FSM: 认知与行为循环"""
    SLEEPING = auto()          # 睡眠/等待信号
    MAIN_TOOL = auto()         # 意图识别/工具触发
    SUB_LOOP = auto()          # MCP工具调用子循环
    MAIN_HIDDEN = auto()       # 隐藏逻辑链生成
    MAIN_FORMAL = auto()       # 最终自然语言生成
