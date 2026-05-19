# .gitignore 忽略构建产物并保留空目录 — 计划

## 问题
- `Listings/` 和 `Objects/` 里的文件是 Keil C51 编译自动生成的，不应提交到 Git
- 已被 Git 跟踪，`.gitignore` 对已跟踪文件无效
- 希望保留这两个空目录（让 clone 后目录结构完整）

## 分析

### 技术细节
1. **`.gitignore` 只对新文件生效**：已经被 `git add` / 提交过的文件，`.gitignore` 不会忽略它
2. **需要先 `git rm --cached`** 从 Git 索引中移除，但保留本地文件（`--cached` 不删文件）
3. **Git 不跟踪空目录**：需要在目录里放一个占位文件（惯例叫 `.gitkeep`）
4. **`.gitignore` 规则**：
   - `Listings/*` → 忽略 Listings 下的所有文件
   - `!Listings/.gitkeep` → 取消忽略 .gitkeep，让它被 Git 跟踪
   
### 文件类型说明
- `Listings/` 里：`.lst`（汇编列表）、`.map`（内存映射）
- `Objects/` 里：`.obj`、`.__i`、`.crf`、`.lnp`、`.hex`、`build.log` 等

## 解决步骤

1. 创建根目录 `.gitignore`，写入规则
2. 在 `Listings/` 和 `Objects/` 里各创建 `.gitkeep` 空文件
3. `git rm -r --cached Listings/ Objects/` 从 Git 索引移除所有构建产物
4. `git add .gitignore Listings/.gitkeep Objects/.gitkeep` 暂存新文件
5. 验证 `git status` 确认效果

## 总结
- 保留本地文件 ✅
- 以后不再被 Git 跟踪 ✅
- 目录结构保留 ✅
