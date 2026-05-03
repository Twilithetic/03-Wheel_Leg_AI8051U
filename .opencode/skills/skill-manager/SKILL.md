---
name: skill-manager
description: 使用 skm (skill-manager) CLI 工具管理 OpenCode / Claude / Cursor 等 AI 编码助手的 skills。包含安装、添加源、安装/更新/移除 bundle、查看已安装列表等完整操作指南。当用户提到 skill 管理、安装新 skill、查找社区 skill、从 anthropics/skills 安装、或者需要管理 .opencode/skills 目录时触发。
license: MIT
compatibility: opencode
metadata:
  tool: skm
  version: "0.9.0"
  repo: https://github.com/pyrex41/skill-manager
  install_method: cargo install skill-manager
---

# skm (skill-manager) 使用指南

## 这是什么？

**skm**（skill-manager）是一个 Rust 编写的 CLI 工具，用于统一管理 AI 编码助手的 **skills**（技能/提示词/指令文件）。

支持的目标工具：**Claude Code**、**OpenCode**、**Cursor**、**Codex**。

核心价值：一套 skill 源文件 → 自动适配并安装到不同工具的目录结构。

## 当前环境（29344 的环境）

| 项目 | 值 |
|------|-----|
| skm 版本 | 0.9.0 |
| 配置文件 | `~/.config/skm/config.toml` |
| Sources | ① `~/.claude-skills` (local) ② `https://github.com/anthropics/skills` (git) |
| 已安装（项目内） | `pdf`（来自 anthropics/skills） |
| 安装清单 | `.opencode/.skm.toml` |

## 安装 skm

```bash
# 需要先安装 Rust: https://rustup.rs/
cargo install skill-manager

# 验证
skm --version
```

## 核心概念

```
Sources（源）  →  Bundles（捆绑包）  →  Targets（目标工具目录）
  ├─ git repo        ├─ skills/          ├─ .opencode/skills/
  └─ 本地目录        ├─ agents/           ├─ .opencode/agents/
                     ├─ commands/         ├─ .opencode/commands/
                     └─ rules/            └─ .opencode/rules/
```

- **Source**：skill 的"仓库"，可以是 GitHub 仓库或本地目录
- **Bundle**：一个功能单位，包含 skills/agents/commands/rules 子目录
- **Target**：安装目标（`-o` = OpenCode，`-c` = Cursor，默认 Claude）

## 快速入门

### 1. 添加源

```bash
# 官方 Anthropic skills 仓库（推荐添加！）
skm sources add https://github.com/anthropics/skills

# 本地目录
skm sources add ~/my-skills

# 查看所有源
skm sources list

# 交互式管理源
skm sources
```

### 2. 浏览可用的 Bundles

```bash
# 列表视图
skm

# 交互式模糊搜索浏览器
skm list
```

### 3. 安装 Bundle

```bash
# 安装到 OpenCode（当前项目）
skm pdf -o

# 安装到 Claude（默认）
skm pdf

# 安装到 Cursor
skm pdf -c

# 全局安装（到用户目录而非当前项目）
skm pdf -o -g

# 自动安装某个源的所有 bundles
skm sources add https://github.com/anthropics/skills
skm anthropics  # 安装该源的所有 bundle
```

### 4. 查看已安装

```bash
skm here                # 当前目录所有已安装
skm here --tool opencode  # 只看 OpenCode 的
```

### 5. 移除

```bash
skm rm pdf              # 移除 pdf bundle
skm rm pdf -y           # 跳过确认
skm here --remove       # 交互式选择移除
skm here --clean --yes  # 全部移除
```

### 6. 更新

```bash
skm update              # 更新 git 源 + 刷新已安装的 skills
skm update --sources-only  # 只更新 git 源
```

## 完整命令参考

| 命令 | 说明 |
|------|------|
| `skm` | 列出所有可用 bundle |
| `skm list` | 交互式模糊搜索浏览器 |
| `skm <bundle>` | 安装指定 bundle（默认 Claude） |
| `skm <bundle> -o` | 安装到 OpenCode |
| `skm <bundle> -c` | 安装到 Cursor |
| `skm <bundle> -x` | 安装到 Codex |
| `skm <bundle> -g` | 全局安装 |
| `skm <bundle> --skills` | 只安装 skills 部分 |
| `skm <bundle> --agents` | 只安装 agents 部分 |
| `skm <bundle> --commands` | 只安装 commands 部分 |
| `skm <bundle> --rules` | 只安装 rules 部分 |
| `skm add <bundle>` | 同 `skm <bundle>` |
| `skm sources` | 交互式管理源 |
| `skm sources list` | 列出所有源 |
| `skm sources add <path>` | 添加源 |
| `skm sources remove <path>` | 移除源 |
| `skm here` | 查看已安装的 skills |
| `skm here --tool opencode` | 按工具筛选 |
| `skm here --remove` | 交互式移除 |
| `skm here --clean --yes` | 清理所有已安装 |
| `skm rm <bundle>` | 移除指定 bundle |
| `skm rm <bundle> -y` | 跳过确认 |
| `skm update` | 更新源并刷新已安装 |
| `skm completions bash/zsh/fish` | 生成 shell 补全 |

## OpenCode 安装细节

当用 `skm <bundle> -o` 安装到 OpenCode 时，文件的映射规则如下：

| 源文件类型 | 目标路径 |
|-----------|---------|
| `skills/foo.md` | `.opencode/skills/{bundle}-{name}/SKILL.md` |
| `agents/foo.md` | `.opencode/agents/{bundle}-{name}.md` |
| `commands/foo.md` | `.opencode/commands/{bundle}-{name}.md` |
| `rules/foo.md` | `.opencode/rules/{bundle}-{name}/RULE.md` |

skm 会自动：
1. 如果 skill/rule 文件缺少 YAML frontmatter，**自动添加** `name` 和 `description`
2. 如果 agent 文件的 `tools:` 是 Claude 格式（PascalCase 逗号分隔），**自动转换**为 OpenCode 格式（YAML 对象）
3. 复制 companion files（同目录下的脚本、配置等）

## 重要规则 / 决策指南

### 何时使用 skm？

✅ **应该用 skm 的场景：**
- 用户说"我想装一个新的 skill"（如 `skm xlsx -o`）
- 用户说"帮我找找有没有处理 Word 文档的 skill"（先用 `skm` 或 `skm list` 搜索）
- 用户说"更新一下所有 skills"（`skm update`）
- 用户说"把 Claude 的 skills 也弄到 OpenCode"（`skm <bundle> -o`）
- 用户问"我怎么知道已经装了哪些 skills"（`skm here`）

❌ **不需要 skm 的场景：**
- 用户只是问某个 skill 怎么用（直接告诉用户这个 skill 的用法即可）
- 用户想从零创建一个新的 skill（用 OpenCode 的 `/skill-create` 或手动写 `SKILL.md`）
- 用户想编辑已有的 skill（直接修改 `.opencode/skills/<name>/SKILL.md` 文件）

### 安装新 skill 后的操作

1. 安装完成后，**需要重启 OpenCode 会话**（或新开一个 session）才能加载新 skill
2. 可以在 `opencode.json` 中配置权限（`permission.skill`）

### 已知问题 / 注意事项

1. **`skm pdf` vs `skm pdf -o`**：不带 `-o` 默认安装到 Claude 的 `.claude/` 目录，一定要加 `-o` 才安装到 `.opencode/`
2. **组合名称**：OpenCode 安装后 skill 名会是 `{bundle}-{name}` 格式（如 `pdf-pdf`），但这是底层实现细节，对使用无影响
3. **全局 vs 项目**：不加 `-g` 安装到当前目录，加 `-g` 安装到 `~/.config/opencode/`
4. **source 优先级**：source 按添加顺序搜索，同名 bundle 第一个匹配的优先
5. **更新后刷新**：`skm update` 会同时更新源码仓库和刷新已安装的 skills（从源重新写入）

## 常用 anthropics/skills 目录

来自 `https://github.com/anthropics/skills` 的可用 bundles：

| Bundle | 用途 |
|--------|------|
| `pdf` | PDF 读取/创建/编辑/合并/拆分 |
| `xlsx` | Excel 电子表格处理 |
| `docx` | Word 文档创建/编辑 |
| `pptx` | PowerPoint 演示文稿 |
| `frontend-design` | 前端界面设计 |
| `canvas-design` | 海报/视觉设计 |
| `algorithmic-art` | p5.js 算法艺术 |
| `mcp-builder` | MCP 服务器构建 |
| `webapp-testing` | Playwright Web 测试 |
| `slack-gif-creator` | Slack GIF 动画 |
| `skill-creator` | 创建/优化 skills |
| `theme-factory` | 主题样式工具 |
| `brand-guidelines` | Anthropic 品牌设计 |
| `internal-comms` | 内部通讯写作 |
| `doc-coauthoring` | 文档协作写作 |
| `web-artifacts-builder` | 复杂 Web 组件 |
| `claude-api` | Claude API/SDK 开发 |

## 执行命令时的注意事项

在 OpenCode 环境中执行 skm 相关命令时：

```powershell
# 必须用 pwsh.exe -Command 来执行（Windows 环境）
pwsh.exe -Command "skm pdf -o"

# 或者直接用 skm（如果已在 PATH）
skm pdf -o
```
