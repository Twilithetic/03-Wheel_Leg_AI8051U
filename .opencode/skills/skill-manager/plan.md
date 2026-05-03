# skill-manager OpenCode Skill 撰写计划

## 问题

我们需要为 OpenCode 创建一个 skill，让 AI（知心姐姐）学会如何使用 `skm`（skill-manager）这个 CLI 工具来管理 skills。当前环境已经安装了 skm 0.9.0，但 AI 还不"认识"这个工具，不知道在什么场景下应该使用它、如何调用它。

## 问题分析

### 1. skm 是什么？

**skill-manager (skm)** 是一个用 Rust 编写的 CLI 工具（GitHub: `pyrex41/skill-manager`），用于统一管理 AI 编码助手（Claude、OpenCode、Cursor、Codex）的 skills。

核心概念：
- **Sources**：skill 仓库（本地目录或 git repo）
- **Bundles**：包含 `skills/`、`agents/`、`commands/`、`rules/` 子目录的文件夹
- **Targets**：工具特定的目录（如 `.opencode/`、`.claude/`、`.cursor/`）

### 2. skm 为 OpenCode 写入文件的规则

根据源码 `src/target.rs` 中的 `write_opencode()` 方法：

| 类型 | 目标路径 | 格式 |
|------|---------|------|
| **Skills** | `.opencode/skills/{bundle}-{name}/SKILL.md` | 文件夹 + SKILL.md（自动添加 frontmatter） |
| **Agents** | `.opencode/agents/{bundle}-{name}.md` | 扁平单文件 |
| **Commands** | `.opencode/commands/{bundle}-{name}.md` | 扁平单文件 |
| **Rules** | `.opencode/rules/{bundle}-{name}/RULE.md` | 文件夹 + RULE.md |

自动转换功能：
- 自动为 skill/rule 文件添加 YAML frontmatter（`name` + `description`），如果缺失的话
- agent 文件的 `tools:` 字段在 Claude 格式（`Read, Grep, Glob`）和 OpenCode 格式（`read: true\n  grep: true`）之间自动转换
- 复制 companion files（同目录下的脚本、模板等）

### 3. 当前环境状态

- skm 0.9.0 已安装（通过 `cargo install skill-manager`）
- 配置文件：`~/.config/skm/config.toml`
- 已添加的 sources：
  1. `~/.claude-skills` (local)
  2. `https://github.com/anthropics/skills` (git)
- 项目中已通过 skm 安装：`pdf` bundle → `.opencode/skills/pdf-pdf/SKILL.md`
- 项目中有 manifest 文件：`.opencode/.skm.toml`

### 4. OpenCode Skill 格式要求

根据 OpenCode 官方文档（https://opencode.ai/docs/zh-cn/skills/）：

- 目录结构：`.opencode/skills/<name>/SKILL.md`
- 必须 YAML frontmatter，必需字段：`name`（`^[a-z0-9]+(-[a-z0-9]+)*$`）、`description`（1-1024 字符）
- name 必须与目录名一致
- 可选字段：`license`、`compatibility`、`metadata`

## 解决方案

### 创建 skill：`skill-manager`

**位置**：`D:\Learning-STC\test_8051_STC\.opencode\skills\skill-manager\SKILL.md`

**内容大纲**：

1. **概述**：介绍 skm 是什么、解决什么问题
2. **安装**：`cargo install skill-manager`，前提条件
3. **快速入门**：
   - 添加 source：`skm sources add <path-or-url>`
   - 查看可用 bundles：`skm` 或 `skm list`
   - 安装 bundle 到 OpenCode：`skm <bundle> -o`
   - 安装 bundle 到 Claude（默认）：`skm <bundle>`
   - 查看已安装：`skm here`
   - 移除：`skm rm <bundle>`
4. **完整命令参考**：所有子命令及其用途
5. **当前环境配置**：记录用户（29344）的 sources、已安装的 bundles
6. **使用场景决策树**：什么情况下应该建议用户使用 skm
7. **注意事项 / 坑**：
   - OpenCode 安装后格式是 `{bundle}-{name}` 组合名称
   - 需要重启 OpenCode 才能加载新 skill
   - skm 更新源：`skm update`

### 技术细节

- skill 使用 OpenCode 标准的 YAML frontmatter 格式
- name: `skill-manager`（符合 `^[a-z0-9]+(-[a-z0-9]+)*$` 正则）
- description 需要在 1-1024 字符内

## 总结

创建 `.opencode/skills/skill-manager/SKILL.md`，内容涵盖：
1. skm 工具的介绍
2. 完整的命令参考
3. 适配 OpenCode 的特殊说明
4. 当前环境的配置信息
5. 使用决策指南

这样以后当用户问"怎么安装/管理 skills"时，加载此 skill 就能获得完整的 skm 使用知识。
