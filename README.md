# ESP32-Paxcounter for Cardputer ADV

面向 **M5Stack Cardputer ADV + Cap LoRa-1262** 的 ESP32-Paxcounter 适配项目，目标是做一台轻量、可通过 M5Launcher 安装和切换的便携无线设备计数器。

基于 [cyberman54/ESP32-Paxcounter](https://github.com/cyberman54/ESP32-Paxcounter) fork，复用上游 Wi-Fi / BLE 计数与 LoRaWAN 基础，重点适配 ADV 的屏幕、键盘和扩展模块。

> **当前状态：适配筹备中。** 本次初始化仅更新项目说明与路线，代码仍为继承的上游版本；尚未提供经过验证的 ADV 构建配置或固件，也未进行 ADV 实机验收。以下功能均为规划，不代表已经实现。

## 为什么做这个 fork

希望在 Cardputer ADV 上随身观察周边无线设备数量及其变化，并保留后续位置记录和 LoRa 传输的可能性。

主要使用场景是 **M5Launcher 多固件共存**。根据当前使用体验，较大的固件会增加空间压力，切换时有时需要临时移除其他固件。因此，本项目选择在原 Paxcounter 上做专用适配，按需启用功能，控制产物体积，并用实际分区与 Launcher 安装结果验证收益。

## 目标硬件

| 硬件 | 作用 |
| --- | --- |
| Cardputer ADV（ESP32-S3） | Wi-Fi / BLE 扫描、240×135 彩屏显示、键盘操作 |
| Cap LoRa-1262（SX1262 + GNSS） | 后续 LoRaWAN 上报与定位扩展 |
| microSD 卡（可选） | 后续统计数据记录与导出 |

硬件资料：[Cardputer ADV](https://docs.m5stack.com/en/core/Cardputer-Adv) · [Cap LoRa-1262](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)。早期 Cap LoRa868 与新版 LoRa-1262 存在差异，不能直接套用初始化配置。

## 开发方向

1. **先完成单机计数**：增加 ADV 板级配置，验证 Wi-Fi / BLE 计数，适配屏幕与键盘，提供暂停、清零、翻页和必要参数设置。
2. **验证精简交付**：关闭无关功能，记录应用二进制与分区占用，生成适合 M5Launcher 的应用固件，验证安装、启动和切换。
3. **按需扩展**：趋势图、GNSS 定位、SD 统计 CSV 和 LoRaWAN 上报，分别验证后再纳入版本。

首版不以多传感器平台或完整网络工具箱为目标。GPS、SD、LoRaWAN 按需加入；没有实测前不承诺具体固件大小、节省空间比例或续航。

详细范围、硬件注意事项和验收条件见 [ADV 适配路线](docs/cardputer-adv.md)。

## 计数的含义

Paxcounter 统计的是扫描窗口内检测到的无线设备，不能直接等同于人数；Wi-Fi 与 BLE 数量也不能简单相加当作人数。MAC 随机化、设备无线状态和扫描环境会影响结果，初期用于观察设备数量与人流趋势。

延续上游只做汇总计数的方向：不新增原始 MAC 持久化、个体追踪或去随机化功能。后续 SD 记录与无线传输以时间窗口统计值为主。

## 构建与固件

当前仓库中的构建说明和配置来自上游，**尚无本 fork 经验证的 Cardputer ADV 构建入口、Launcher 分区方案或可用固件下载**。请勿将其他开发板的构建产物当作 ADV 固件直接刷入。

适配完成后，每次交付应附源码版本、构建命令、应用二进制大小、分区要求、校验值及实机验证结果。

## 上游与许可

- 本 fork：[sheneyan/ESP32-Paxcounter](https://github.com/sheneyan/ESP32-Paxcounter)
- 上游项目：[cyberman54/ESP32-Paxcounter](https://github.com/cyberman54/ESP32-Paxcounter)
- 上游原始 README（本 fork 初始化时保存）：[README.upstream.md](README.upstream.md)
- 上游文档：[paxcounter.org](https://paxcounter.org/)，描述上游通用能力，不代表本 fork 已完成 ADV 适配。

保留上游版权、许可与致谢。上游主体采用 Apache License 2.0，部分文件有单独许可说明，详见 [LICENSE](LICENSE)、[上游版权与致谢](README.upstream.md#license) 及各源文件头部声明。
