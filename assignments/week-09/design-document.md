# Design document · 迁陵：仓梁下的尸体

## 1. Claim

A historical simulation should simulate **the procedure by which the past was made legible**, not only its scenery. In the Qin county of Qianling, a death became a legal fact only when a clerk wrote it into a category: suicide, intentional killing (zeisha 贼杀), killing in a fight (dousha 斗杀), or "death hard to determine" (sinan shen 死难审). The player learns this by writing the case file, not by watching a cutscene.

## 2. Historical question

How did a Qin local clerk turn a corpse into a legal category, and how did that category distribute responsibility among the household, the village, the granary, and the post station?

## 3. Sources

- **Primary**: *Shuihudi Qin bamboo manuscripts* — *Fengzhen shi* 封诊式 (especially *Jing si* 经死 and *Zei si* 贼死), *Falü dawen* 法律答问, *Xingshu lü* 行书律.
- **Primary (format/context)**: Liye 里耶 Qin slips — grain accounts, household registers, postal records.
- **Secondary (core three)**: 周敏華 2009 (Qin forensic procedure); Clyde, Hopkins & Wilkinson 2012 (gamic mode / procedural rhetoric); Gluzman 2025 (contestability). Aarseth 1997 is a theoretical footnote for interpretative/configurative user functions. Full citations and locators in `bibliography.md`.

## 4. The design

### 4.1 Player role and loop

The player is **Xi 喜**, a newly appointed *lingshi* 令史. On his first day, a fictional granary clerk, Bing 丙, is found hanged—a case built from the real *Jing si* 经死 autopsy template. The player must:

1. read the village head's report and the *Jing si* checklist;
2. inspect the body (tongue, rope marks, excrement, head/feet distances, breath);
3. inspect the bruise and blood by the grain sacks;
4. check the granary ledger (30 shi missing);
5. interview the granary overseer, the village head, and Bing's wife;
6. seal the file and record the time at the post station;
7. submit a verdict and decide whom to write into the file.

### 4.2 Four verdicts

| Verdict | Evidentiary condition | Consequence |
|---|---|---|
| **Suicide** | required items only; no bruise, no wife's testimony | case closed; granary accounts buried; later appeal |
| **Zeisha** (intentional killing) | bruise + wife's testimony or ledger | homicide case; granary overseer and village head detained |
| **Dousha** (fight) | neighbour's testimony | the deputy magistrate reclassifies it as *zeisha*: "dousha ren, ting xingshi wei zei" |
| **Sinan shen** (hard to determine) | bruise but contradictory signs | file sent to the commandery; no resolution |
| **Falsified autopsy** | bruise/wife's testimony but wrote suicide | the clerk is blamed |
| **Falsified time** | backdated post time | postman punished; clerk blamed |

### 4.3 Text layers

- **Original layer**: the manuscript text, preserved verbatim, with source card.
- **Plain layer**: a modern Chinese paraphrase, shown by default; "看原文" toggles.
- **Why**: the original is the evidence; the plain layer is the access. This is a deliberate design choice, not a claim that the paraphrase is the source.

### 4.4 Bounded agents

Each NPC has:

- a **persona** and a **goal**;
- a **knowledge scope** of sourced facts;
- a **forbidden** list (what they cannot know);
- a **speech style** (plain modern Chinese, no classical pastiche);
- **fallback** lines for offline/blocked calls.

The model proposes speech only. The world validates movement, evidence, verdicts, and endings. The server applies schema, source, meta-discourse, and style guards.

### 4.5 Evidence gates

- Documents and objects provide **clues** and document text; they do not automatically add every evidence item to the case file.
- Key evidence is granted by an NPC topic only **after** the NPC reply (or the scripted fallback): the granary clerk's `press` gives `e_wound`; the postman's topics give `e_post`; the wife's topics give `e_wife`; the village head's topics give `e_neighbor`.
- Therefore every verdict requires at least one NPC conversation: suicide requires `e_post` from the postman; homicide and “死难审” require `e_wound` from the granary clerk; fight requires `e_neighbor` from the village head.
- The world appends a “〔记入案卷〕…” confirmation line to the dialogue when evidence is added, so the player sees that the answer, not the click alone, produced the evidence.

## 5. Technical stack

| Layer | Technology | Why | Limits |
|---|---|---|---|
| Game | Godot 4.7 (GDScript, 2D) | walkable scenes, camera, collision, UI, exportable | needs Godot; 2D abstraction |
| Web | HTML/CSS/JS canvas | no install; embeddable in Reslides iframe | needs local server; no offline file:// |
| Data | JSON | inspectable, shared by both builds | no schema validation at runtime beyond code |
| AI | DeepSeek via Python stdlib server | cheap, JSON mode, logs tokens/cost | latency, hallucination, no semantic guarantee |
| Art | PIL procedural generation | consistent style, no third-party assets | schematic, not archaeological reconstruction |
| Sources | Markdown/JSON with locators | traceability | paper page numbers still missing |

## 6. Evaluation

- `--playtest`: all eight evidence items, six verdict paths, no missing target.
- `--walktest`: four gates pass.
- Online/offline: fallback lines keep the chain playable.
- AI probes: meta-discourse and stylistic guards; 121 calls logged, 3 retries, 7 meta blocks.
- **Not yet done**: user testing with players unfamiliar with Qin law; a proper pre/post comprehension test.

## 7. Academic significance

- **Qin judicial procedure**: 周敏華 (2009) shows that the *Jing si* examination has a detailed procedure, each examination item has a purpose, and the examination process is integrated with judicial procedure (abstract p.1). The simulation turns that procedure into a sequence the player must execute; missing an item produces a defective case file and the deputy magistrate rejects it.
- **Media argument**: Clyde, Hopkins, and Wilkinson (2012) argue for a “gamic mode of history” that constructs historical narrative through **procedural rhetoric**; the player explores the historical argument through meaningful decision-making and play (Abstract). In the simulation, the case-file format, evidence thresholds, and rejection rules are the argument. The player does not read a conclusion; they configure means, rules, and operations to produce one.
- **Contestability**: Gluzman (2025) argues that contestability should be a structural condition embedded in a game’s epistemological framework, not merely thematic ambiguity; evidence is fragmentary and often misleading, and conclusions remain provisional (§7). The simulation uses four required and four optional evidence items that can contradict one another; “死难审” is a legitimate but provisional verdict; endings show rejection, reclassification, transfer to the commandery, or a later appeal.

The claim is not "a game recreates the Qin"; it is that a historical simulation can make **legal classification** and **procedural judgment** into a testable, replayable, explainable argument.

## 8. Contribution

1. **Procedure-first historical simulation**: the document, not the street, is the main game board.
2. **Non-skippable procedure**: verify—investigate—write; the player runs the procedure rather than reading about it (configurative function).
3. **Contestability as a mechanic**: incomplete and contradictory evidence, provisional verdicts, and endings that can be overturned.
4. **A Qin legal case study**: the *Jing si* checklist and the *Falü dawen* rules become mechanics, not exposition.

## 9. Limits

- The case is invented; *Jing si* is a model document, not a real case.
- The four verdicts are a game simplification of Qin homicide categories.
- The English/Chinese terminology is simplified for access.
- The 2D map is schematic, not an archaeological reconstruction.
- No audio; no standalone export yet.
