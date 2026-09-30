---
title: 双休购 Shuangxiu Gou
emoji: 🛒
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 双休购 · Shuangxiu Gou

先问企业双不双休，再决定买不买。输入品牌/产品，或**用手机拍一张包装图**，
服务器识别图中的产品与公司，再查库判断它是否被公开来源描述为双休。

- 数据：`week-04` 的双休公司/产品库（SQLite，由 CSV 在镜像构建时重建）。
- 模型：DeepSeek（`deepseek-flash`）——function calling 查库 + 视觉识别。
- 密钥：`DEEPSEEK_API_KEY` 由 Space 的 **Secret** 提供，不写进仓库。

> 口径：只反映**公开来源的描述**，非用工事实认定、非穷举；企业作息以其官方最新说明为准。

本 Space 是 `dhg508-workspace` 的 `assignments/week-05` 应用，由
`code/deploy_hf.py` 打包上传。
