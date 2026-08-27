# AstrBot Lost Sword 攻略插件

从[番茄盒子 Lost Sword 兑换码页](https://fanqiebox.com/games/lost-sword/tools/codes/)抓取兑换码、奖励、状态、有效期和出处，供 AstrBot 在群聊中查询；同时保留攻略页查询能力。

## 使用

```text
/ls
/ls 兑换码
/ls 城门
/ls 冰法
/ls 暗法
/ls 大乱斗
/ls 水猫岛
/ls 山羊岛
/ls 火岛
/ls 黑狼岛

# 旧版攻略命令仍可用
/lost_sword 埃塞尔城
/lost_sword ethel-city
```

插件只允许抓取 `fanqiebox.com/games/lost-sword/` 下的 HTTPS 页面，默认缓存 5 分钟、请求间隔至少 1 秒。兑换码命令返回页面列出的全部代码及状态，不自行判断日期；`/ls 城门`、`/ls 冰法`、`/ls 暗法` 会发送对应阿瓦隆阵容图，`/ls 大乱斗` 会发送四类岛屿作业图，其余岛屿关键词同理。图片中的阵容文字仍以原图为准，插件不会对图片做 OCR。

## 安装

在 AstrBot 插件管理中填入本仓库地址，或将整个目录复制到 AstrBot 的 `data/plugins/` 目录。AstrBot 4.5+ 推荐使用 `metadata.yaml` 自动识别插件信息。

依赖安装：

```bash
pip install -r requirements.txt
```

## 开发测试

```bash
python -m pytest -q
```

## 版权与使用说明

本项目只保存抓取代码，不镜像番茄盒子的正文或图片文件。内容版权归原网站及原作者所有；请遵守目标网站的使用条款、robots 规则和合理请求频率。本插件与 Lost Sword 官方及番茄盒子没有隶属关系。
