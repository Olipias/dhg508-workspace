# Week 4 · 20 行抽样核对

随机种子 `508`，`code/check_rows.py` 可复现。逐行回原来源核对，记录错误、成因、修复。

## 1. `companies` rowid=70

- **company_id**: C070
- **name_zh**: 苏泊尔
- **name_en**: SUPOR
- **industry_id**: IND25
- **city_id**: CITY13
- **schedule_type**: 双休
- **evidence_level**: E-B
- **schedule_original**: 办公岗双休、基本准点
- **source_id**: S1
- **source_locator**: 二、双休为主·家电小家电/家居
- **note**: None
- **来源**: 双休公司推荐名单 2026（270+ 家持续更新）：真双休/大小周/单休 全对照｜即答侠 HireMe AI（第三方整理，据官方通知、媒体报道、脉脉/小红书/知乎/牛客员工反馈）｜https://interviewasssistant.com/zh/blog/company-work-schedule-2026
- **出处位置**: 二、双休为主·家电小家电/家居
- **核对结果**: 与 S1「家电小家电/家居」一致：办公岗双休。城市/行业为公开资料整理，非原文
- **错误/成因/修复**: 无

## 2. `companies` rowid=101

- **company_id**: C101
- **name_zh**: 味事达
- **name_en**: None
- **industry_id**: IND40
- **city_id**: CITY27
- **schedule_type**: 双休
- **evidence_level**: E-C
- **schedule_original**: 名单收录
- **source_id**: S4
- **source_locator**: 企业名单表
- **note**: 酱油与调味汁；英文名未核实，故留空
- **来源**: 双休购 · 企业名单（sxgo.cc）｜双休购公益项目（@大仙在玩数码 发起）｜https://sxgo.cc/
- **出处位置**: 企业名单表
- **核对结果**: 与 S4 快照一致（味事达｜酱油与调味汁｜江门）
- **错误/成因/修复**: 错误：name_en 曾填 “Zhongshan Masters”，来源未载。成因：擅自补英文名。修复：name_en 清空，并在 note 注明“英文名未核实”

## 3. `companies` rowid=85

- **company_id**: C085
- **name_zh**: 恒瑞医药
- **name_en**: Hengrui Pharma
- **industry_id**: IND36
- **city_id**: CITY24
- **schedule_type**: 双休
- **evidence_level**: E-B
- **schedule_original**: 销售岗双休为主
- **source_id**: S1
- **source_locator**: 二、双休为主·金融/医药
- **note**: None
- **来源**: 双休公司推荐名单 2026（270+ 家持续更新）：真双休/大小周/单休 全对照｜即答侠 HireMe AI（第三方整理，据官方通知、媒体报道、脉脉/小红书/知乎/牛客员工反馈）｜https://interviewasssistant.com/zh/blog/company-work-schedule-2026
- **出处位置**: 二、双休为主·金融/医药
- **核对结果**: 与 S1「金融/医药」一致：销售岗双休为主
- **错误/成因/修复**: 无

## 4. `companies` rowid=54

- **company_id**: C054
- **name_zh**: 百事（中国）
- **name_en**: PepsiCo
- **industry_id**: IND26
- **city_id**: CITY09
- **schedule_type**: 双休
- **evidence_level**: E-B
- **schedule_original**: 职能岗双休，销售岗周六常出勤
- **source_id**: S1
- **source_locator**: 二、双休为主·快消/食品饮料
- **note**: None
- **来源**: 双休公司推荐名单 2026（270+ 家持续更新）：真双休/大小周/单休 全对照｜即答侠 HireMe AI（第三方整理，据官方通知、媒体报道、脉脉/小红书/知乎/牛客员工反馈）｜https://interviewasssistant.com/zh/blog/company-work-schedule-2026
- **出处位置**: 二、双休为主·快消/食品饮料
- **核对结果**: 与 S1「快消/食品饮料」一致：职能岗双休，销售岗周六常出勤
- **错误/成因/修复**: 无

## 5. `companies` rowid=64

- **company_id**: C064
- **name_zh**: 上海家化
- **name_en**: Jahwa
- **industry_id**: IND31
- **city_id**: CITY09
- **schedule_type**: 双休
- **evidence_level**: E-B
- **schedule_original**: 职能岗双休
- **source_id**: S1
- **source_locator**: 二、双休为主·美妆/日化/服饰
- **note**: None
- **来源**: 双休公司推荐名单 2026（270+ 家持续更新）：真双休/大小周/单休 全对照｜即答侠 HireMe AI（第三方整理，据官方通知、媒体报道、脉脉/小红书/知乎/牛客员工反馈）｜https://interviewasssistant.com/zh/blog/company-work-schedule-2026
- **出处位置**: 二、双休为主·美妆/日化/服饰
- **核对结果**: 与 S1「美妆/日化/服饰」一致：职能岗双休
- **错误/成因/修复**: 无

## 6. `companies` rowid=9

- **company_id**: C009
- **name_zh**: 霸王茶姬
- **name_en**: CHAGEE
- **industry_id**: IND08
- **city_id**: CITY10
- **schedule_type**: 双休
- **evidence_level**: E-A
- **schedule_original**: “夜洁计划”请外部供应商代做打烊清洁，让门店员工按时下班
- **source_id**: S1
- **source_locator**: 一、明星案例表
- **note**: 门店仍需轮班，重点在减少打烊加班
- **来源**: 双休公司推荐名单 2026（270+ 家持续更新）：真双休/大小周/单休 全对照｜即答侠 HireMe AI（第三方整理，据官方通知、媒体报道、脉脉/小红书/知乎/牛客员工反馈）｜https://interviewasssistant.com/zh/blog/company-work-schedule-2026
- **出处位置**: 一、明星案例表
- **核对结果**: 与 S1「明星案例」一致：夜洁计划。城市成都为公开资料，非原文
- **错误/成因/修复**: 无

## 7. `products` rowid=26

- **product_id**: P026
- **name**: vivo S 系列手机
- **category_id**: CAT16
- **company_id**: C007
- **source_id**: S1
- **source_locator**: 一、明星案例表
- **note**: None
- **来源**: 双休公司推荐名单 2026（270+ 家持续更新）：真双休/大小周/单休 全对照｜即答侠 HireMe AI（第三方整理，据官方通知、媒体报道、脉脉/小红书/知乎/牛客员工反馈）｜https://interviewasssistant.com/zh/blog/company-work-schedule-2026
- **出处位置**: 一、明星案例表
- **核对结果**: 与 S1「明星案例」一致：vivo X/S 手机
- **错误/成因/修复**: 无

## 8. `products` rowid=67

- **product_id**: P067
- **name**: TapTap
- **category_id**: CAT19
- **company_id**: C029
- **source_id**: S1
- **source_locator**: 二、双休为主
- **note**: None
- **来源**: 双休公司推荐名单 2026（270+ 家持续更新）：真双休/大小周/单休 全对照｜即答侠 HireMe AI（第三方整理，据官方通知、媒体报道、脉脉/小红书/知乎/牛客员工反馈）｜https://interviewasssistant.com/zh/blog/company-work-schedule-2026
- **出处位置**: 二、双休为主
- **核对结果**: 与 S1 一致：心动网络 → TapTap
- **错误/成因/修复**: 无

## 9. `products` rowid=94

- **product_id**: P094
- **name**: soundcore
- **category_id**: CAT02
- **company_id**: C043
- **source_id**: S1
- **source_locator**: 二、双休为主
- **note**: 子品牌
- **来源**: 双休公司推荐名单 2026（270+ 家持续更新）：真双休/大小周/单休 全对照｜即答侠 HireMe AI（第三方整理，据官方通知、媒体报道、脉脉/小红书/知乎/牛客员工反馈）｜https://interviewasssistant.com/zh/blog/company-work-schedule-2026
- **出处位置**: 二、双休为主
- **核对结果**: 与 S1 一致：安克 → soundcore 子品牌
- **错误/成因/修复**: 无

## 10. `products` rowid=171

- **product_id**: P171
- **name**: 仟人饮料
- **category_id**: CAT22
- **company_id**: C093
- **source_id**: S4
- **source_locator**: 企业名单表
- **note**: None
- **来源**: 双休购 · 企业名单（sxgo.cc）｜双休购公益项目（@大仙在玩数码 发起）｜https://sxgo.cc/
- **出处位置**: 企业名单表
- **核对结果**: 与 S4 快照一致：仟人｜饮料｜广东
- **错误/成因/修复**: 无

## 11. `products` rowid=21

- **product_id**: P021
- **name**: 长城炮
- **category_id**: CAT15
- **company_id**: C005
- **source_id**: S1
- **source_locator**: 一、明星案例表
- **note**: None
- **来源**: 双休公司推荐名单 2026（270+ 家持续更新）：真双休/大小周/单休 全对照｜即答侠 HireMe AI（第三方整理，据官方通知、媒体报道、脉脉/小红书/知乎/牛客员工反馈）｜https://interviewasssistant.com/zh/blog/company-work-schedule-2026
- **出处位置**: 一、明星案例表
- **核对结果**: 与 S1「明星案例」一致：长城炮
- **错误/成因/修复**: 无

## 12. `products` rowid=178

- **product_id**: P178
- **name**: PLAYMOBIL 儿童玩具
- **category_id**: CAT12
- **company_id**: C099
- **source_id**: S4
- **source_locator**: 企业名单表
- **note**: None
- **来源**: 双休购 · 企业名单（sxgo.cc）｜双休购公益项目（@大仙在玩数码 发起）｜https://sxgo.cc/
- **出处位置**: 企业名单表
- **核对结果**: 与 S4 快照一致：PLAYMOBIL｜儿童玩具｜上海
- **错误/成因/修复**: 无

## 13. `claims` rowid=82

- **claim_id**: CL082
- **company_id**: C082
- **schedule_type**: 双休
- **schedule_original**: 双休为主
- **year_original**: （未注明）
- **year_start**: None
- **date_rule**: 原文未给年份，留空
- **evidence_level**: E-B
- **source_id**: S1
- **source_locator**: 二、双休为主·金融/医药
- **note**: None
- **来源**: 双休公司推荐名单 2026（270+ 家持续更新）：真双休/大小周/单休 全对照｜即答侠 HireMe AI（第三方整理，据官方通知、媒体报道、脉脉/小红书/知乎/牛客员工反馈）｜https://interviewasssistant.com/zh/blog/company-work-schedule-2026
- **出处位置**: 二、双休为主·金融/医药
- **核对结果**: 与 S1 一致：中国银联 双休为主；原文未给年份，year_start 留空
- **错误/成因/修复**: 无

## 14. `claims` rowid=68

- **claim_id**: CL068
- **company_id**: C068
- **schedule_type**: 双休
- **schedule_original**: 双休为主，门店/电商另计
- **year_original**: （未注明）
- **year_start**: None
- **date_rule**: 原文未给年份，留空
- **evidence_level**: E-B
- **source_id**: S1
- **source_locator**: 二、双休为主·美妆/日化/服饰
- **note**: 旗下巴拉巴拉
- **来源**: 双休公司推荐名单 2026（270+ 家持续更新）：真双休/大小周/单休 全对照｜即答侠 HireMe AI（第三方整理，据官方通知、媒体报道、脉脉/小红书/知乎/牛客员工反馈）｜https://interviewasssistant.com/zh/blog/company-work-schedule-2026
- **出处位置**: 二、双休为主·美妆/日化/服饰
- **核对结果**: 与 S1 一致：森马 双休为主
- **错误/成因/修复**: 无

## 15. `claims` rowid=48

- **claim_id**: CL048
- **company_id**: C048
- **schedule_type**: 双休
- **schedule_original**: 双休为主
- **year_original**: （未注明）
- **year_start**: None
- **date_rule**: 原文未给年份，留空
- **evidence_level**: E-B
- **source_id**: S1
- **source_locator**: 二、双休为主·手机/消费电子/硬件
- **note**: 旗下豪威科技
- **来源**: 双休公司推荐名单 2026（270+ 家持续更新）：真双休/大小周/单休 全对照｜即答侠 HireMe AI（第三方整理，据官方通知、媒体报道、脉脉/小红书/知乎/牛客员工反馈）｜https://interviewasssistant.com/zh/blog/company-work-schedule-2026
- **出处位置**: 二、双休为主·手机/消费电子/硬件
- **核对结果**: 与 S1 一致：韦尔 双休为主
- **错误/成因/修复**: 无

## 16. `claims` rowid=83

- **claim_id**: CL083
- **company_id**: C083
- **schedule_type**: 双休
- **schedule_original**: 双休为主
- **year_original**: （未注明）
- **year_start**: None
- **date_rule**: 原文未给年份，留空
- **evidence_level**: E-B
- **source_id**: S1
- **source_locator**: 二、双休为主·金融/医药
- **note**: None
- **来源**: 双休公司推荐名单 2026（270+ 家持续更新）：真双休/大小周/单休 全对照｜即答侠 HireMe AI（第三方整理，据官方通知、媒体报道、脉脉/小红书/知乎/牛客员工反馈）｜https://interviewasssistant.com/zh/blog/company-work-schedule-2026
- **出处位置**: 二、双休为主·金融/医药
- **核对结果**: 与 S1 一致：财付通 双休为主
- **错误/成因/修复**: 无

## 17. `industries` rowid=32

- **industry_id**: IND32
- **name**: 服饰
- **note**: 维度值为依公司公开资料整理，非来源原文；精确信息以公司官网为准
- **source_id**: S1
- **source_locator**: 行业列（整理，非 S1 原文）
- **来源**: 双休公司推荐名单 2026（270+ 家持续更新）：真双休/大小周/单休 全对照｜即答侠 HireMe AI（第三方整理，据官方通知、媒体报道、脉脉/小红书/知乎/牛客员工反馈）｜https://interviewasssistant.com/zh/blog/company-work-schedule-2026
- **出处位置**: 行业列（整理，非 S1 原文）
- **核对结果**: 服饰分类无误
- **错误/成因/修复**: 无

## 18. `cities` rowid=19

- **city_id**: CITY19
- **name**: 厦门
- **province**: 福建
- **note**: 维度值为依公司公开资料整理，非来源原文；精确信息以公司官网为准
- **source_id**: S1
- **source_locator**: 城市列（整理，非 S1 原文）
- **来源**: 双休公司推荐名单 2026（270+ 家持续更新）：真双休/大小周/单休 全对照｜即答侠 HireMe AI（第三方整理，据官方通知、媒体报道、脉脉/小红书/知乎/牛客员工反馈）｜https://interviewasssistant.com/zh/blog/company-work-schedule-2026
- **出处位置**: 城市列（整理，非 S1 原文）
- **核对结果**: 厦门属福建，无误
- **错误/成因/修复**: 无

## 19. `categories` rowid=20

- **category_id**: CAT20
- **name**: 茶饮
- **note**: 维度值为依公司公开资料整理，非来源原文；精确信息以公司官网为准
- **source_id**: S1
- **source_locator**: 产品分类（整理，非 S1 原文）
- **来源**: 双休公司推荐名单 2026（270+ 家持续更新）：真双休/大小周/单休 全对照｜即答侠 HireMe AI（第三方整理，据官方通知、媒体报道、脉脉/小红书/知乎/牛客员工反馈）｜https://interviewasssistant.com/zh/blog/company-work-schedule-2026
- **出处位置**: 产品分类（整理，非 S1 原文）
- **核对结果**: 茶饮分类无误
- **错误/成因/修复**: 无

## 20. `sources` rowid=6

- **source_id**: S6
- **title**: 促中国消费者反加班「双休购」APP走红遭砍
- **publisher**: 世界日报
- **url**: https://www.worldjournal.com/wj/story/121474/9749898?zh-cn
- **pub_date**: 2026-09
- **kind**: 新闻报道
- **accessed**: 2026-09-23
- **note**: 双休购由重庆文化传播公司7月14日上线，后暂停服务
- **来源**: 促中国消费者反加班「双休购」APP走红遭砍｜世界日报｜https://www.worldjournal.com/wj/story/121474/9749898?zh-cn
- **出处位置**: 
- **核对结果**: 来源信息本应正确，但抽样发现列错位
- **错误/成因/修复**: 错误：sources.csv 中 note 与 accessed 两列值互换。成因：seed_data.py 按 (…,note)+[ACCESSED] 追加，而表头写作 accessed,note，错位。修复：调整表头为 note,accessed；重建后 S6 的 accessed=2026-09-23、note=双休购由重庆文化传播公司7月14日上线，后暂停服务

