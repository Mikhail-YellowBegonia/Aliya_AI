# Project Aliya: 系统需求与架构规约 (Demo Phase)

## 1. 核心愿景与设计哲学 (The Philosophy)
Aliya 是一个聚焦于“陪伴”而非“生产力”的 AI 智能体。底层依托于状态机与长上下文工程（Context Engineering）。
* **Warmth over Efficiency（温暖优于效率）**：Aliya 被允许低效。她应当展现出拟人化的情感波动、记忆回顾和环境感知。
* **Immersion Protection（沉浸感保护）**：用户和主LLM看到的必须是纯净的自然语言。所有 JSON、工具调用日志、系统报错，必须在“潜意识层”被消化或转译。

## 2. 架构模式与边界 (Architecture Scope)
本项目采用 **“外圆（纯自然语言 LLM）内方（基于状态机的逻辑与工具隔离）”** 的中心化 Multi-Agent 架构。

**Demo 阶段实施边界 (In Scope)：**
1. **控制中心 (Main Loop)**：基于有限状态机（FSM）的 I/O 锁控制与 Key 分配机制。
2. **认知循环 (Agent Loop)**：基于 `TOOL -> HIDDEN -> FORMAL` 三阶段迭代的意识流逻辑。
3. **上下文寻址 (Context Assembly)**：基于绝对号段分配的“寄存器式”上下文拼接机制。
4. **外部拓扑 (Take-ism/拿来主义)**：全面拥抱 Model Context Protocol (MCP)，以Openclaw为榜样拓展功能。

**Demo 阶段不包含 (Out of Scope)：**
复杂的 3D 渲染控制、Auto Dream 离线记忆整理（Demo 期手动触发）、高维度的多 Agent 并发竞争。

## 3. 核心机制定义 (Core Mechanisms)

### 3.1 上下文号段分配协议 (AMP - Aliya Milestone Protocol)
上下文不再是简单的滑动窗口，而是分布式的内存对象。组装器（Context Assembly）按以下优先级严格串联：
1. **[-N] Prompt Slices (静态系统层)**：系统提示词、核心人设、道德边界（如拒绝编程指令）。绝对不可被子 Agent 覆盖。
2. **[+N] History Slices (半静态历史层)**：由 Milestone 机制切片固化后的长期对话记忆。
3. **[Cache] 工作记忆**：尚未触发切片条件（Slice）的近期对话上下文。
4. **[0] Meta (动态环境感知)**：存放在独立数据库的瞬时数据（时间、日期、天气、系统状态）。每轮对话前强制刷新，**不进入历史库**。
5. **[Scratchpad] 阅后即焚便签**：仅在 `HIDDEN` 阶段挂载。存放子 Agent (MCP Server) 返回的原始 JSON 或长文本。在 `FORMAL` 输出完毕后立即清空。
6. **[Cache*] 最新刺激**：将最新的一轮对话（以及进行中的这轮对话）单独提取，置于上下文最末端，利用 LLM 近因效应确保指令遵循。

### 3.2 并发状态机与 Key 分配锁 (Dual-FSM & I/O Governance)
系统分为 Main FSM与 Agent FSM。
* **独占性控制**：当 Main FSM 离开 `IDLE` 状态进入 `BUSY_COGNITION` 时，立刻下发 `int.key` 给 Agent FSM，同时向前端 CLI 广播 `LOCK_INPUT` 信号，强制屏蔽用户后续输入。
* **三段式迭代 (The 3-Iteration)**：
    * `MAIN_TOOL`：意图识别与工具触发请求。
    * `MAIN_HIDDEN`：吸收 Scratchpad 里的工具反馈，生成内在逻辑链（对用户隐藏）。
    * `MAIN_FORMAL`：基于前两步，生成最终的拟人化自然语言输出。

### 3.3 积极容错机制 (Positive Fail-forward)
* **Error as Answer**：系统假设底层 API 不保证 100% 成功。当发生网络超时、MCP 崩溃时，拦截器（Interceptor）必须将系统 Traceback 转换为标准化自然语言（例：`{"status": "error", "message": "Aliya 失去了与天气服务器的连接"}`），并作为合法结果存入 Scratchpad 继续流转，诱导 LLM 生成“抱歉，我刚刚走神了”的拟人化回应。
* **避免死循环**：Agent FSM 内设置 `iter_count`。工具调用循环（SUB LOOP）超过 3 次强制熔断，直接进入 `MAIN_FORMAL`。

### 3.4 AI驱动的开发 (AI Driven Development)
* **代码轻量化**：尽量通过明确的函数/类来保证代码的可维护性，同时减少文件数量，保证可读性，原则上*AI产出的全部代码必须经过人工阅读，且理解*，同时，*使用AI写代码时不得跨文件，跨模块或直接处理架构逻辑*。
* **注释优先**：注释比文档更灵活，具体实现/用途/责任划分的内容优先进行注释，文档只记录更关键内容。