# Research journal · 迁陵：仓梁下的尸体

## 2026-10-31 · 换案子：从「十七户」到「一具尸体」

- **决定**：week 8 的「十七户迁都乡」是一个好的行政案，但它的法律冲突太「现代」——名册滞后、口粮标准，读者容易把它理解成「文书工作很麻烦」。我想要一个**和现代法律直觉直接冲突**的案子：杀人了怎么处置。
- **候选**：①《封诊式·贼死》的他杀现场；②《封诊式·经死》的吊死验尸；③《法律答问》的贼杀/斗杀。
- **选择**：以《经死》为主，因为它是**一份验尸模板**：舌出、绳痕、矢溺、头脚距离、死难审、问同居。模板本身不是答案，玩家要在「自杀/他杀/死难审」之间做判断。再用《法律答问》的「斗杀人，廷行事为贼」做反转，用「四邻/典老」做连坐压力。
- **AI 建议 vs 我的判断**：AI 一开始建议做「谁是凶手」的侦探线；我没有采纳。侦探线会把玩家变成全知者，和「文书决定分类」的主题相反。玩家应该**不知道**，只能记录。

## 2026-11-01 · 读《经死》《法律答问》

- **《封诊式·经死》**（睡虎地秦简）：里典报案→令史与牢隶臣、丙妻、女往诊→记录舌出、绳痕、矢溺、头脚距离→解索看口鼻气→「舌不出，口鼻不喟然，索迹不郁，索终急不能脱，□死难审殹」→「自杀者必先有故，问其同居」。
  - **我的理解**：这不是「法医科学」的胜利，而是**一套可复核的书写格式**。它把「死」拆成可记录的项目；项目不对，就写「死难审」。
- **《法律答问》**：
  - 「求盗追捕罪人，罪人挌（格）杀求盗，问杀人者为贼杀人，且斲（斗）杀？斲（斗）杀人，廷行事为贼。」
  - 「贼入甲室，贼伤甲，甲号寇，其四邻、典、老皆出不存，不闻号寇，问当论不当？审不存，不当论；典、老虽不存，当论。」
  - **我的理解**：秦律的「斗杀」不是现代「打架失手」；在这个语境里，斗杀按贼杀办。四邻/典老的连坐也不是「见死不救」的道德口号，是有条件的行政责任。
- **设计修改**：把「斗杀」做成一个陷阱选项；把「写不写里典/四邻」做成玩家的选择；把「死难审」做成一个合法但没结果的判决。

## 2026-11-02 · 检索（OpenAlex）

按课程要求，**没有**用 OpenCode 的简单网页搜索。用 OpenAlex API（`https://api.openalex.org/works?search=...`），记录实际查询：

- `Qin law Shuihudi`
- `Qin dynasty legal procedure`
- `procedural rhetoric video games`
- `historical simulation games`
- `generative agents interactive characters`
- `Shuihudi forensic`
- `封诊式`
- `Qin homicide law`
- `Qin criminal procedure bamboo`
- `history games procedural rhetoric`
- `historical game authenticity`
- `AI NPC historical game`
- `generative AI cultural heritage game`
- `Shuihudi Qin law`
- `Qin bamboo legal manuscripts`
- `Qin law and society`
- `封诊式 秦代 诉讼`
- `睡虎地 秦律`
- `Government document systems in Qin dynasty`
- `Writing Chinese Laws Caldwell`
- `封診式 經死 爰書試探`
- `Beyond the Historical Simulation Clyde Hopkins Wilkinson`
- `Those Who Do Not Learn History Are Doomed to Play It`

> 说明：`generative agents` / `AI NPC` 等查询是早期探索，最终没有选用 AI 作为参考文献。2026-11-04 按新论证重找三篇：周敏華 2009（秦代勘验程序）、Clyde/Hopkins/Wilkinson 2012（gamic mode / procedural rhetoric）、Gluzman 2025（contestability）。OpenAlex 核对：Clyde 等 `W131687738`；周敏華与 Gluzman 用 DOI/Airiti/ACM 记录核对。普通网页搜索只用于找链接和核对律令片段，不作为学术检索来源。

**有用的线索**（不是 finding，只是 lead）：

- 周敏華 2009，《封診式‧經死》爰書試探（Airiti/DOI）→ 新论证的史学命题。
- Clyde, Hopkins & Wilkinson 2012, *Beyond the “Historical” Simulation*（OpenAlex/Loading）→ 新论证的媒介命题。
- Gluzman 2025, *Those Who Do Not Learn History Are Doomed to Play It*（ACM DOI）→ 新论证的 contestability。
- 王均平：用户提到的“秦代犯罪侦查有比较细致的分工和比较科学的程序、方法”，没有找到可核验的篇名/期刊/页码；不引用。
- Aarseth 1997, *Cybertext*：interpretative/configurative 区分的理论脚注，不算三篇核心。
- 早前读过的 Staack 2023、Răzman 2020、Stirling & Wood 2021：保留在书目“Earlier candidates”，不再作为这次的三篇核心。
- 2026 年一篇 Baoshan/Zhangjiashan 证据制度文章（OA）：读了，但重点在楚简/汉简的「盟证」，与秦《经死》不够贴，放弃。
- Brill 的 *On the Death Penalty...*（2022）：OpenAlex 标 OA，但 PDF 被 Cloudflare 挡住；没有全文，按「未读」处理，不引用。
- Lüdke, *Professional Practice: Law in Qin and Han China*（2016）：heiDOK 下载超时；未读，不引用。
- Caldwell, *Writing Chinese Laws*（2018）：书本身没拿到全文；只读到 OA 书评。书评不能代替原书，暂不作为三篇之一。

## 读三篇（页码/位置）

### 1. 周敏華 2009

- **出处**：周敏華，《封診式‧經死》爰書試探，《東吳中文學報》17（2009）：1–18。DOI 10.29460/SJCS.200905.0001。
- **论点**：《经死》不是单纯的尸检知识，而是一份细致的勘验程序；每一项勘验都有目的，而且勘验过程已经与司法程序相结合。
- **位置**：
  - 摘要 p.1：「極為細膩地描述了勘驗的程序，及解釋所有勘驗內容的目的……秦代的法醫勘驗工作已相當成熟，且勘驗的過程，也已經與司法程序相結合。」
  - pp.1–18：全文。
- **和我的设计**：把《经死》拆成必须逐项执行的验尸步骤；缺项，案卷就不完整，守丞驳回。玩家不是“知道”程序，而是“被程序推着走”。

### 2. Clyde, Hopkins & Wilkinson 2012

- **出处**：Jerremie Clyde, Howard Hopkins, and Glenn Wilkinson, “Beyond the ‘Historical’ Simulation: Using Theories of History to Inform Scholarly Game Design,” *Loading...* 6(9) (2012): 3–16. OpenAlex W131687738.
- **论点**：他们提出 **gamic mode of history**：通过 **procedural rhetoric** 建构历史叙事，而不是只做“历史主题的模拟”。玩家通过有意义的决策和游玩来探索历史论证；规则本身可以承载论证。
- **位置**：
  - Abstract：「a gamic mode of history that focuses on the construction of the historical narrative via procedural rhetoric」；「the reader explores the historical argument through meaningful decision making and play」。
  - pp.3–16：全文。
- **和我的设计**：案卷格式、证据门槛、驳回规则就是论证；玩家不能凭直觉断案，必须按规则收集、对照、提交。这不是“历史主题的游戏”，是“用程序修辞做历史论证”。

### 3. Gluzman 2025

- **出处**：Renard Gluzman, “Those Who Do Not Learn History Are Doomed to Play It,” *Proceedings of the 3rd International Conference of the ACM Greek SIGCHI Chapter* (2025). DOI 10.1145/3749012.3749043.
- **论点**：历史游戏不应只靠 setting/visual 来“历史”，而应模拟历史 inquiry；**contestability** 应成为游戏认识论框架里的结构性条件，而不是主题上的模糊氛围。证据是碎片化的、可能误导的；结论始终是暂定的。
- **位置**：
  - Abstract：历史游戏与 historiography 的连接；perspective、causality、continuity/change、source interpretation、contestability。
  - §7 “Contestability”：Obra Dinn / Immortality；从碎片化、误导性证据中重建事件；结论可修正。
- **和我的设计**：4 必得 + 4 可选；可选证据互相矛盾；“死难审”是合法但暂定的记录；结局会驳回、改判、送郡或三个月后翻案。玩家不是选结局，是在承受“我可能判错”的压力。

## 自动生成建议 vs 我的判断

- **AI 建议**：把「斗杀」做成比「贼杀」轻的选项，让玩家可以「替人减罪」。**我的判断**：不采纳。《法律答问》明确说「斗杀人，廷行事为贼」，做成减罪会误导；改成陷阱，让玩家学到反直觉规则。
- **AI 建议**：让丙妻直接说出「是里典杀的」，给玩家一条破案线索。**我的判断**：不采纳。她只知道「有人来、三十石、他害怕」，不知道凶手；这符合信息边界，也让玩家不能靠一句口供结案。
- **AI 建议**：把「死难审」做成失败结局。**我的判断**：不采纳。《经死》原文就有「死难审」，它是**合法的记录**，不是失败；做成「没结果但没冤枉人」的第三种结局。

## 整合进设计

- 验尸五样 + 后脑淤伤/粮袋血 → `body_exam` / `wound_note`。
- 斗杀→贼杀 → `homicide_law` + 「写成了斗杀」结局。
- 四邻/典老 → 提交表单里的「把里典/四邻写进案卷」。
- 原文/人话版 → `documents.json` 的 `body`/`plain`，UI 默认 `plain`，按钮「看原文」。
- 有界 agent → `npcs.json` 的 `knowledge`/`forbidden` + 服务器 `META_TERMS`/`STYLE` 守卫。
- 证据门 → 物件只给线索；`e_wound` 要问仓啬夫，`e_post` 要问邮人，`e_wife` 要问丙妻，`e_neighbor` 要问里典；证据在 NPC 回答后才入案卷。

## 未解决

- 纸本页码：周敏華的期刊页码有了（1–18），Clyde 等是 3–16，Gluzman 用 §7 定位；《经死》《法律答问》的纸本页码还没补。
- 「死难审」是描述还是判决名，需再核。
- 「斗杀人，廷行事为贼」的适用范围是否像游戏里那么宽，需再核。
- 玩家测试：还没有找不了解秦律的玩家做前测/后测。
