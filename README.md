# Agent 电子书重构预览

四本中文电子书 `rewrite/agent-ebooks` 分支的集中静态预览。与各仓库 `main` 的正式 Pages 分开，不覆盖现有发布。

- 入口：<https://stardust0083-gp03.github.io/agent-ebooks-rewrite-preview/>
- 分支：`rewrite/agent-ebooks`

| 书 | 路径 | 本地克隆 |
| --- | --- | --- |
| AI 工程师：从原理到实践 | `ai-engineer/` | `../AI-Engineer-from-scrach` |
| Agent Memory from Scratch | `agent-memory/` | `../agent-memory-from-scratch` |
| AI Infra from Scratch | `ai-infra/` | `../ai-infra-from-scratch` |
| LangChain × LangGraph | `langchain-langgraph/` | `../langchain-langgraph-from-scratch` |

`preview.json` 记录各分支的提交。AI 工程师阅读本原有的 163 个仓库根目录素材链接在部署时改写为该分支的 GitHub 源码地址；其余三本保留构建器生成的站内链接和上游固定提交链接。

## 检查

- 本地服务器检查 259 个内部 URL，0 个 404 或缺失锚点。
- 桌面和移动布局检查；四本目录页、三个合订本与搜索页可打开。
- 未重新运行各仓库构建器，直接发布分支中已跟踪的静态产物。
- 未执行各仓库完整测试或真实模型/MCP 调用。

本目录可由上一级 `prepare_preview.py` 从四个本地分支重新生成。
