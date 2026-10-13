# 网页实际验证

日期：2026-10-14。结果：passed。浏览器：Chromium 151.0.7922.34。

访问地址：https://yydshly.github.io/1013_codex_project/008-shadps4/，通过独立静态子路径测试。

| 检查 | 结果 | 实际证据 |
| --- | --- | --- |
| 静态子路径与资源 | pass | HTML、CSS、JavaScript、完整 SVG / PNG 总览、简化流程、图标、实测 JSON 与实机截图均返回 200；网页加载的是 1800×3290 完整总览图。 |
| 章节和来源 | pass | 11 个目录目标、12 行固定版本源码依据、3 个上游案例入口存在。 |
| 本机运行证据展示 | pass | 7 行执行记录、1282×752 原生窗口截图、实际日志与未验证范围可加载。 |
| 教学流程与失败停止 | pass | 3 个请求 × 3 种条件共 9 条路径；正常到第 7 步，接口缺失停在第 3 步，着色器失败停在第 5 步；后退和重播通过。 |
| 键盘操作 | pass | Enter 重播、Space 推进教学流程通过；测试采用减少动画偏好。 |
| 缓存教学 | pass | 首次转换、第二次复用、清空后再次转换通过；仅验证教学状态。 |
| 理解核对 | pass | 未答提示、三题错误反馈和全部正确反馈通过。 |
| CSV 下载 | pass | 下载名称正确，UTF-8 BOM 存在，22 列含版本、设备、场景、证据与未验证事项。 |
| 响应式布局 | pass | 1440、1024、768、390、320 像素宽均无整页横向溢出；宽表格在内部滚动。 |
| 返回研究库 | pass | 返回链接在聚合站点子路径中打开根索引，索引包含本项目。 |
| 浏览器错误 | pass | 无 JavaScript 页面异常、错误控制台或失败网络请求。 |

截图为实际浏览器内容，保存于子项目 assets/；不是模板或上游游戏素材。

- [assets/01-web-overview.jpg](../../assets/01-web-overview.jpg)：静态子路径的实际浏览器截图。
- [assets/05-web-diagram.jpg](../../assets/05-web-diagram.jpg)：静态子路径的实际浏览器截图。
- [assets/02-web-demonstration.jpg](../../assets/02-web-demonstration.jpg)：静态子路径的实际浏览器截图。
- [assets/03-web-runtime.jpg](../../assets/03-web-runtime.jpg)：静态子路径的实际浏览器截图。
- [assets/04-web-mobile.jpg](../../assets/04-web-mobile.jpg)：390 像素宽手机布局的实际浏览器截图。

验证当前访问地址的网页教学、证据加载和静态子路径；原生模拟器执行另见 runtime-verification。未验证商业游戏或浏览器原生 PS4 执行。

复现脚本：[verify_web.cjs](../verify_web.cjs)。需要 Playwright 与对应 Chromium；以 SHAD_WEB_URL 指定待检查的本地或公网地址。
