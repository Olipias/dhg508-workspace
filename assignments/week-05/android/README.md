# 双休购 · Android（WebView 壳）

把线上网页 `https://shuangxiu-app.vercel.app` 包成一个可安装的 APK。已处理：
JavaScript/DOM 存储、`<input type=file capture>` 拍照与相册选择、相机运行时权限、返回键回退。

## 用 Android Studio 生成 APK（推荐，零命令行）

1. Android Studio → **Open** → 选本目录 `assignments/week-05/android`。
2. 首次会自动下载 Gradle 与依赖（需联网）。
3. 菜单 **Build → Build Bundle(s) / APK(s) → Build APK(s)**。
4. 产物在 `app/build/outputs/apk/debug/app-debug.apk`，传到手机安装（允许"未知来源"）。

想改加载的网址：编辑 `app/src/main/java/com/shuangxiu/app/MainActivity.kt` 里的
`webView.loadUrl("...")` 一行。

## 命令行构建（可选，需本机有 JDK 17 + Android SDK）

```bash
cd assignments/week-05/android
gradle wrapper            # 生成 gradlew（若没有）
./gradlew assembleDebug
```

## 说明与限制

- 这是**壳**：内容仍是线上网页，所以"国内网络打不开 vercel.app"的问题会一并带进来。
- 表情/相机：首次点"拍照/上传产品"会申请相机权限，允许后即可调用系统相机。
- 包名 `com.shuangxiu.app`，`minSdk 26`（Android 8.0+），`targetSdk 34`。
- 想换图标：`app/src/main/res/drawable/ic_launcher_foreground.xml` + `res/values/colors.xml`。
