-- Aliya 数据库初始化蓝图 - 2.1 增强版

-- 1. 提示词分片表 (AMP: -N)
-- 存储：系统人设、道德准则、Sub-Agent 清洗提示词等
CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,          -- 唯一标识符，如 'core_persona', 'sub_cleaner'
    content TEXT NOT NULL,              -- 提示词具体内容
    priority INTEGER DEFAULT 0,         -- 组装时的优先级
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 对话记录表 (AMP: +N / Cache)
-- 包含：长期历史 (History) 和 尚未切片的近期记忆 (Working Memory)
-- 使用 is_archived 来区分，避免在两个表之间频繁物理搬运
CREATE TABLE IF NOT EXISTS chat_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT CHECK(role IN ('user', 'assistant')) NOT NULL,
    content TEXT NOT NULL,
    hidden_thought TEXT,                -- [MAIN_HIDDEN] 阶段生成的内心独白（可选存储）
    order_index INTEGER NOT NULL,       -- 时间线绝对顺序
    is_archived INTEGER DEFAULT 0,      -- 0: Cache (Working), 1: +N (History)
    milestone_id INTEGER DEFAULT 0,     -- 归档所属的里程碑ID
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. 子循环沙盒 (Subsession)
-- 专门存放 Sub Agent 在执行工具调用时的内部逻辑链，不进入主对话历史
CREATE TABLE IF NOT EXISTS sub_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,           -- 本轮工具调用的唯一标识
    role TEXT NOT NULL,                 -- system, user, assistant, tool
    content TEXT NOT NULL,
    order_index INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. 阅后即焚便签 (AMP: [S] Scratchpad)
-- 存放 Sub Agent 基于工具结果清洗后的自然语言信息
CREATE TABLE IF NOT EXISTS ephemeral_scratch (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,              -- 已经由 Sub Agent 清洗过的自然语言
    source_tool TEXT,                   -- 来源工具名（可选，方便溯源）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 5. 瞬时感官/环境变量 (AMP: [0] Meta)
CREATE TABLE IF NOT EXISTS meta_cache (
    key TEXT PRIMARY KEY,               -- 如 'time', 'weather', 'location'
    value TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
