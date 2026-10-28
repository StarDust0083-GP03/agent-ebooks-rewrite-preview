# Agent 工程书架

七本中文电子书的独立预览站，不覆盖各原仓库的正式 Pages。

阅读入口：https://stardust0083-gp03.github.io/agent-ebooks-rewrite-preview/

| 书 | 入口 |
| --- | --- |
| AI 工程师：从原理到实践 | `ai-engineer/index.html` |
| Agent Memory from Scratch | `agent-memory/index.html` |
| AI Infra from Scratch | `ai-infra/index.html` |
| LangChain × LangGraph | `langchain-langgraph/index.html` |
| Pi：从工具循环到 Code Mode | `pi-code-mode/index.html` |
| RAG 工程实战 | `rag/wiki/index.html` |
| Octop 架构解剖 | `octop/wiki/index.html` |

## 阅读器

保留正文及各书配色，改进阅读栏宽、标题层级、手机目录、当前章节定位、代码与表格横向滚动、三态外观和键盘焦点。代码复制受浏览器限制时会选中文本，供手动复制。样式与脚本随书分发，合订本保留内嵌资源，不依赖外部 CDN。

Octop 提供分章网页、单文件合订本、Markdown、PDF 与 EPUB。内容依据官方提交 `890111b7879665840414ca28ab168b05b0db0921`，参考 SAM 系列的需求驱动讲解方法；不是官方文档，也不是生产压测或安全审计。RAG 与 Octop 的“源码”链接指向被分析的上游项目，而非书稿仓库。

## 构建与发布

本目录只包含可公开的阅读产物、少量原创教学代码和清单。不包含第三方仓库克隆、凭证、虚拟环境、全文研究归档和依赖缓存。

对应本地书稿构建完成后，由上级 `prepare_preview.py` 按白名单复制阅读资源并改写链接。Pi 的构建器将阅读样式与交互内嵌到 HTML；AI Engineer 和 RAG 的离线合订本也需在修改阅读资源后重新构建，不能只更新外链 CSS。

GitHub Pages 从本仓库 `main` 的根目录发布。部署前检查内部 URL、锚点和桌面/平板/手机布局，推送后等待 Pages 构建成功并核验线上入口与下载文件。各原始书稿工作区中的改动不自动等于其正式 Pages 已更新。

## 本次验证

2026-10-29：七本书的文案复审。范围包括全部章节标题与小节标题、七本目录页、四个搜索页、书架页、章首与下载入口等读者可见文案，以及每本书的前言/开篇和 12 个代表章节的逐段阅读。

本轮改动：

- 标题统一为中文在前，保留 API、基准和文件名。AI Infra 42 个纯英文标题、LangChain 14 个、Agent Memory 6 个就地改写，半译标题（如 “Sequence 数量”“KV block”“iteration-level scheduling”）一并修正。
- 修正 AI Infra 搜索页误用 LangChain 示例（reducer、interrupt）的文案错误，各书搜索提示改为本书术语，空状态统一为“换个更短的说法，或清空后浏览目录”。
- Agent Memory 搜索页补上提示与结果计数，索引改为内联脚本，`file://` 直接打开也能检索；四本搜索结果的摘要不再以逗号或冒号开头。
- 书架去掉分支名等技术标识，卡片统一为章节计数（如“25 篇 · 含 6 篇补编”“17 章 + 附录”），外观切换并入说明行。
- 正文做句子级改写，只动需要回读才能拆开的句子与堆叠条件，未逐段重写。改动数量以各仓库 diff 为准。

验证：七本的 390、834、1440px 布局检查与 27 项浏览器检查通过；322 个内部 URL 与锚点无断链；各书结构校验、EPUB 结构与 PDF 文稿核对通过。可用已安装的 `agent-browser` 复跑：

```bash
python3 scripts/verify_readers.py
```

LangGraph 审批示例测试仍因环境缺少 `langgraph` 未运行，不计为通过。离线教学程序不代表真实模型、MCP、云服务或硬件验收。

Impeccable 扫描提示 Pi 暗色文字可能落在白底上。浏览器实测背景为 `#171d19`，正文与次要文字的对比度分别为 13.66:1 和 8.61:1；浅色分别为 13.57:1 和 5.61:1。已查看深浅色页面与 PDF，未按静态扫描的跨主题误配修改配色。
