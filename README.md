# 唐代侠义诗可视化

这是一个以唐代咏侠诗为对象的静态数字人文可视化项目，包含地理分布、词频、情感强度和作者—聚类关系等页面。

## 本地运行

项目使用浏览器端 HTML、D3、ECharts 和 p5.js，不需要构建步骤。由于页面需要通过 `fetch`、`d3.csv` 和 JSON 请求加载资源，请通过静态服务器访问：

```bash
npm run dev
```

或直接使用 Python：

```bash
python3 -m http.server 8000
```

然后打开 <http://127.0.0.1:8000/index.html>。

## 页面入口

- `index.html`：项目首页
- `interactive.html`：唐代咏侠诗地理分布（p5.js）
- `poetry-emotion.html`：词频类别可视化
- `word-association.html`：诗词情感强度可视化
- `keyword-river.html`：作者与聚类类别关系图
- `circular_sankey.html`：关系弦图备用页面
- `geography.html`：ECharts 地理分布备用页面

## 数据

权威数据位于 `data/`：

- `poetry_with_detailed_clusters_sankey.csv`：100 条诗歌记录及聚类类别
- `地方名称及经纬度.csv`：地点、频次、坐标和类型
- `tang_dynasty_detailed_boundary.json`：唐代边界、城市和路线数据

当前项目以 CSV 中的 100 条诗歌记录作为样本量口径。运行数据校验：

```bash
npm run validate
```

页面依赖的 D3、ECharts、p5.js 和 Google Fonts 当前通过 CDN 加载；如果需要离线部署，下一阶段可以再将这些依赖本地化。
