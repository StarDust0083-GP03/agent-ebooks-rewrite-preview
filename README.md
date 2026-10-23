# Agent 电子书重构预览

四本中文电子书 `rewrite/agent-ebooks` 分支，加上 Pi Code Mode 架构书的集中静态预览。与各仓库 `main` 的正式 Pages 分开，不覆盖现有发布。

- 入口：<https://stardust0083-gp03.github.io/agent-ebooks-rewrite-preview/>
- 分支：`rewrite/agent-ebooks`

| 书 | 路径 | 本地克隆 |
| --- | --- | --- |
| AI 工程师：从原理到实践 | `ai-engineer/` | `../AI-Engineer-from-scrach` |
| Agent Memory from Scratch | `agent-memory/` | `../agent-memory-from-scratch` |
| AI Infra from Scratch | `ai-infra/` | `../ai-infra-from-scratch` |
| LangChain × LangGraph | `langchain-langgraph/` | `../langchain-langgraph-from-scratch` |
| Pi：从工具循环到 Code Mode | `pi-code-mode/` | `../pi-mono-evolution` |

`preview.json` 记录各分支的提交。AI 工程师阅读本原有的 163 个仓库根目录素材链接在部署时改写为该分支的 GitHub 源码地址；其余三本保留构建器生成的站内链接和上游固定提交链接。Pi 书的网页、PDF、EPUB、Markdown 和 12 张 SVG 均从本地构建产物复制，源链接固定到 `pi-mono-architecture-book` 仓库。

## 检查

- 本地服务器检查 263 个内部 URL，0 个 404 或缺失锚点。
- 桌面和移动布局检查；五本目录页、三个合订本、搜索页与 Pi 的 PDF/EPUB 可打开。
- 四套书均已重新构建，新增 16 幅正文内嵌图解：AI Engineer 3 幅、Agent Memory 2 幅、AI Infra 4 幅、LangChain / LangGraph 7 幅。Pi 书更新至 v1.4.0，包含 12 章、12 张架构图、29 条固定来源与 49 页 PDF。
- 修复 AI Infra 与 LangChain / LangGraph 合订本的重复锚点，补充内嵌 SVG 无障碍引用校验。
- 四套阅读产物校验通过；Agent Memory 的 24 项示例测试、AI Infra 离线检查及标准库 Agent 示例通过。
- LangGraph 审批示例测试因当前 Python 缺少 `langgraph` 而受阻，未执行真实模型、MCP、GPU 或持久数据库集成测试。

四套书的构建产物从对应分支的 `ebook/` 或 `wiki/` 同步，再使用上一级 `prepare_preview.py` 的链接改写和目录生成函数整理。`preview.json` 记录本次构建时间、源码提交和新增图数量；未覆盖四个原仓库的正式 Pages。
