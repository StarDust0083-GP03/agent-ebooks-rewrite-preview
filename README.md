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

2026-10-27：扫描七本的 125 个分章阅读页（Pi 为含 12 章的单页），保留技术含义，逐处改写重复对比、抽象总结和说教语气。没有做全部源码与外部文献的逐句事实审计。

七本均通过 390、834、1440px 布局检查，未发现整页横向溢出。27 项浏览器检查覆盖搜索、主题保存、受限复制回退、44px 复制按钮、打印展开及恢复，以及 Pi 从手机切回桌面后的目录可见性。Pi 正文调整为桌面 20px、手机 19px。可用已安装的 `agent-browser` 复跑：

```bash
python3 scripts/verify_readers.py
```

321 个内部 URL 与锚点检查通过；各书自带的结构检查通过，PDF 与 EPUB 已同步本次文稿。离线教学程序不代表真实模型、MCP、云服务或硬件验收。LangGraph 审批示例测试因环境缺少 `langgraph` 未能运行，不计为通过。

Impeccable 扫描提示 Pi 暗色文字可能落在白底上。浏览器实测背景为 `#171d19`，正文与次要文字的对比度分别为 13.66:1 和 8.61:1；浅色分别为 13.57:1 和 5.61:1。已查看深浅色页面与 PDF，未按静态扫描的跨主题误配修改配色。
