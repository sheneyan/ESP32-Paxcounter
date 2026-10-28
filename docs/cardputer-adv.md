# Cardputer ADV 适配路线

记录日期：2026-10-28。当前阶段：项目初始化与范围确认，尚未开始 ADV 固件实现和实机验证。

## 已确定的方向

- 从 cyberman54/ESP32-Paxcounter fork，保留来源与历史，便于同步上游修复。
- 目标硬件为 Cardputer ADV + Cap LoRa-1262。
- 以 M5Launcher 多固件共存为主要交付场景，优先单机计数和小体积固件。
- 复用上游计数核心及已有 ESP32-S3 / SX1262 基础，先验证依赖在 ADV 上可用，再逐步适配外设。
- 本轮只初始化文档和仓库信息，不代表已完成构建、刷机或功能验收。

## 分阶段范围

| 阶段 | 计划内容 | 验收证据 |
| --- | --- | --- |
| 1：最小可用 | ADV 构建配置、Wi-Fi / BLE 计数、屏幕显示、键盘操作 | 可重复构建；实机启动、计数、暂停/恢复、清零、翻页；进入设置→修改参数→保存→设备体现 |
| 2：Launcher 交付 | 关闭无关功能、整理应用固件与分区要求 | 应用 bin 大小、可用槽位/空间记录、Launcher 版本、安装与切换实测 |
| 3：可选扩展 | 趋势图、GNSS、SD 统计 CSV、LoRaWAN | 各项分别记录实际结果，通过验证后更新支持状态 |

阶段 1 的基础构建不强制启用 GNSS、SD 记录或 LoRaWAN。优先排除不使用的传感器、显示后端、OTA 与其他外围功能；仅移除确定无关的依赖，不为减小体积破坏计数核心。

## 硬件适配注意事项

以下为官方文档与上游源码提供的适配依据，均不等于本设备已验证：

- 上游已有 `platformio_orig_s3.ini`，以及 `shared/hal/heltecv3.h`、`shared/hal/ttgot3s3.h` 等 SX1262 配置，可作为起点。
- ADV 使用 240×135 彩屏；显示和键盘需适配 ADV 对应实现。
- Cap LoRa-1262 的 LoRa 引脚：SCK=G40、MISO=G39、MOSI=G14、NSS=G5、RST=G3、IRQ=G4、BUSY=G6。
- 新版 Cap 需通过 PI4IOE5V6408 的 P0 开启射频天线开关；不能仅替换 SPI 引脚。TCXO、DIO2 等射频配置也应逐项核对。
- GNSS：ADV RX=G15、TX=G13，官方默认 UART 115200、NMEA 输出。
- SD 与 LoRa 的总线使用和访问互斥需要核对，不能只凭分别能初始化就认定可以并行运行。
- 官方标注 Cap 工作频段为 868–923 MHz。LoRaWAN 上报需匹配目标网络、网关和区域参数，不能默认沿用上游 EU868 配置。

参考：[ADV 官方文档](https://docs.m5stack.com/en/core/Cardputer-Adv)、[Cap 官方文档](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)、[上游 S3 配置](https://github.com/cyberman54/ESP32-Paxcounter/blob/master/platformio_orig_s3.ini)。

## 体积与交付约束

目标是降低固件占用和多固件切换的空间压力。应用 bin 大小、Flash 分区布局和 Launcher 的空间管理分别记录，不能仅凭 bin 变小推断无需移除其他固件。

固件交付应记录：

- 源码提交、依赖版本和可复现构建命令。
- 应用 bin 大小、SHA-256、Flash / 分区要求。
- M5Launcher 版本、安装方式、设备可用空间和切换结果。
- 屏幕、键盘、扫描及已启用扩展的实测状态。

以适合 Launcher 的应用固件为目标；具体分区兼容性待验证。复制 bin 到 SD 卡只算文件准备，安装、启动、切换和功能正常需分别验证。

## 功能边界

计数用于无线设备数量与变化趋势观察，不能直接标为准确人数。Wi-Fi 与 BLE 不做跨协议身份匹配，不新增原始 MAC 存档、个体轨迹或去随机化功能。

LoRaWAN 与 LoRa 点对点是两条不同的协议路线。本项目优先复用上游 LoRaWAN；点对点收发当前不在承诺范围。趋势图和 GNSS 统计可以后续讨论，但完整地图导航与 Meshtastic 协议不在当前范围内。

## 当前待验证

- 上游计数核心与依赖是否能在 ADV 目标环境稳定构建和运行。
- 显示、键盘、保存配置和扫描任务是否能稳定共存。
- 精简后的实际大小及 Launcher 安装/切换效果。
- 后续扩展的射频收发、GNSS、SD 并发和续航。
