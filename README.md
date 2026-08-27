# AstrBot Lost Sword 攻略插件

从[番茄盒子 Lost Sword 攻略](https://fanqiebox.com/games/lost-sword/guides/avalon/ethel-city/)抓取页面标题、说明、章节和攻略图片，供 AstrBot 在群聊中查询。

## 使用

```text
/lost_sword
/lost_sword 埃塞尔城
/lost_sword ethel-city
/lost_sword https://fanqiebox.com/games/lost-sword/guides/avalon/ethel-city/
```

插件只允许抓取 `fanqiebox.com/games/lost-sword/` 下的 HTTPS 页面，默认缓存 5 分钟并最多返回 3 张攻略图。图片中的阵容文字仍以原图为准，插件不会对图片做 OCR。

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
