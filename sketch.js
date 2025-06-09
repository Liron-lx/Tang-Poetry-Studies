// 全局变量
let locationData = [];
let tangBoundary = null;
// 修改地图尺寸变量 - 放大地图内容
let mapWidth = 1200;
let mapHeight = 800;
// 调整地图范围以放大显示并上移
let minLat = 20, maxLat = 50;  // 从15-55调整为20-50，缩小纬度范围实现放大
let minLon = 75, maxLon = 135; // 从70-140调整为75-135，缩小经度范围实现放大
let tooltip;

// 添加缺失的动画变量
let animationStartTime = 0;
let animationDuration = 800; // 从1500毫秒改为800毫秒（0.8秒）
let isAnimating = true;

// 颜色映射 - 根据用户指定的颜色方案更新
const colorMap = {
    '京城': '#BB7C73',        // 温暖红棕色
    '边塞': '#4D6883',        // 深蓝色
    '内陆城市': '#5A96A3',    // 青蓝色
    '关隘': '#C29F7B',        // 暖棕色
    '其他': '#83AA9A'         // 青绿色
};

// 在文件顶部添加变量
let tangMapData = null;
let locationTable = null;
let dataLoaded = false;
let hoveredLegendType = null;
let clickedLegendType = null;
// 新增动画相关变量
let scaleAnimationProgress = 0;
let targetScale = 1.0;
let currentScale = 1.0;
let animationSpeed = 0.15; // 动画速度

function preload() {
    console.log('开始加载数据...');
    tangMapData = loadJSON('tang_dynasty_detailed_boundary.json'); // 改为详细边界文件
    
    // 使用回调函数确保数据加载完成
    locationTable = loadTable('地方名称及经纬度.csv', 'csv', 'header', 
        function(table) {
            console.log('CSV数据加载完成，行数:', table.getRowCount());
            processLocationData(table);
        },
        function(error) {
            console.error('CSV加载失败:', error);
        }
    );
}

function setup() {
    console.log('Setup开始...');
    let canvas = createCanvas(mapWidth, mapHeight);
    canvas.parent('map-container');
    
    tooltip = select('#tooltip');
    
    // 设置画布样式 - 改为透明背景
    clear(); // 使用clear()来创建透明背景
    
    // 初始化动画时间
    animationStartTime = millis();
    
    // 添加图例初始化（新增）
    setTimeout(() => {
        initializeLegend();
        setupLegendEvents();
    }, 100); // 延迟执行确保DOM已加载
    
    console.log('Setup完成');
}

// 处理位置数据的函数
function processLocationData(table) {
    console.log('开始处理位置数据...');
    
    if (!table) {
        console.error('位置数据表未加载');
        return;
    }
    
    // 清空现有数据
    locationData = [];
    
    // 处理CSV数据
    for (let r = 0; r < table.getRowCount(); r++) {
        let row = table.getRow(r);
        
        // 获取基本信息
        let name = row.getString(0) || '未知地点';
        let frequency = parseInt(row.getString(1)) || 1;
        let historicalNames = row.getString(2) || '无历史地名记录';
        let coordStr = row.getString(3);
        let type = row.getString(4) || '其他';
        
        console.log(`处理地点 ${r + 1}: ${name}, 坐标: ${coordStr}, 类型: ${type}`);
        
        if (!coordStr) {
            console.log(`跳过无坐标地点: ${name}`);
            continue;
        }
        
        // 解析坐标
        let coords = coordStr.split(',');
        if (coords.length < 2) {
            console.log(`坐标格式错误: ${name} - ${coordStr}`);
            continue;
        }
        
        // 移除度数符号和方向字母，处理各种可能的格式
        let latStr = coords[0].replace(/[°NS\s]/g, '').trim();
        let lonStr = coords[1].replace(/[°EW\s]/g, '').trim();
        
        let lat = parseFloat(latStr);
        let lon = parseFloat(lonStr);
        
        // 检查坐标是否有效
        if (isNaN(lat) || isNaN(lon)) {
            console.log(`无效坐标: ${name} - lat: ${latStr} -> ${lat}, lon: ${lonStr} -> ${lon}`);
            continue;
        }
        
        // 检查坐标是否在地图范围内
        if (lat >= minLat && lat <= maxLat && lon >= minLon && lon <= maxLon) {
            let x = map(lon, minLon, maxLon, 50, mapWidth - 50);
            let y = map(lat, maxLat, minLat, 50, mapHeight - 50);
            
            let location = {
                name: name,
                frequency: frequency,
                historicalNames: historicalNames,
                type: type,
                x: x,
                y: y,
                lat: lat,
                lon: lon
            };
            
            locationData.push(location);
            console.log(`成功添加地点: ${name} (${lat}°N, ${lon}°E) -> (${x.toFixed(1)}, ${y.toFixed(1)})`);
        } else {
            console.log(`地点超出地图范围: ${name} (${lat}°N, ${lon}°E)`);
        }
    }
    
    dataLoaded = true;
    
    // 添加调试信息
    console.log('=== 数据处理完成 ===');
    console.log('加载的地点数量:', locationData.length);
    console.log('前5个地点:', locationData.slice(0, 5));
    
    // 检查colorMap中的类型
    let types = new Set(locationData.map(loc => loc.type));
    console.log('数据中的所有类型:', Array.from(types));
    console.log('colorMap中的类型:', Object.keys(colorMap));
    
    // 检查是否有未映射的类型
    let unmappedTypes = Array.from(types).filter(type => !colorMap[type]);
    if (unmappedTypes.length > 0) {
        console.warn('未映射的类型:', unmappedTypes);
    }
}

// 在文件末尾添加图例相关函数
function initializeLegend() {
    const legendItems = document.querySelectorAll('.legend-item');
    
    legendItems.forEach(item => {
        const canvas = item.querySelector('.legend-triangle');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            const type = item.getAttribute('data-type');
            
            // 获取对应颜色
            let color = colorMap[type] || '#999999';
            
            drawLegendTriangle(ctx, color, 20, 15);
        }
    });
}

function drawLegendTriangle(ctx, color, width, height) {
    // 创建渐变
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    
    // 解析颜色
    const r = parseInt(color.slice(1, 3), 16);
    const g = parseInt(color.slice(3, 5), 16);
    const b = parseInt(color.slice(5, 7), 16);
    
    gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, 1.0)`);
    gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0.1)`);
    
    ctx.fillStyle = gradient;
    
    // 绘制三角形
    ctx.beginPath();
    ctx.moveTo(width/2, 0); // 顶点
    ctx.lineTo(0, height); // 左下角
    ctx.lineTo(width, height); // 右下角
    ctx.closePath();
    ctx.fill();
}

function setupLegendEvents() {
    const legendItems = document.querySelectorAll('.legend-item');
    
    legendItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            hoveredLegendType = item.getAttribute('data-type');
        });
        
        item.addEventListener('mouseleave', () => {
            hoveredLegendType = null;
        });
        
        // 修改点击事件，添加动画触发
        item.addEventListener('click', () => {
            const clickedType = item.getAttribute('data-type');
            
            // 如果点击的是已选中的图例，则取消选择
            if (clickedLegendType === clickedType) {
                clickedLegendType = null;
                targetScale = 1.0; // 目标缩放回正常大小
            } else {
                clickedLegendType = clickedType;
                targetScale = 1.5; // 目标缩放到1.5倍
            }
            
            // 重置动画进度
            scaleAnimationProgress = 0;
            
            // 更新图例样式
            updateLegendStyles();
        });
    });
}

// 新增：更新图例样式的函数
function updateLegendStyles() {
    const legendItems = document.querySelectorAll('.legend-item');
    
    legendItems.forEach(item => {
        const itemType = item.getAttribute('data-type');
        const canvas = item.querySelector('.legend-triangle');
        const ctx = canvas.getContext('2d');
        
        // 清除画布
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // 获取颜色
        let color = colorMap[itemType] || '#999999';
        
        // 如果有选中的图例且不是当前项，则变灰
        if (clickedLegendType && clickedLegendType !== itemType) {
            color = '#808080';
        }
        
        // 图例中的三角形始终保持相同大小，只改变颜色
        drawLegendTriangle(ctx, color, 20, 15); // 始终使用正常大小
    });
}

function draw() {
    clear(); // 使用clear()替代background()来保持透明
    
    // 绘制网格点（参考图样式）
    drawGrid();
    
    // 绘制唐代疆域轮廓（简化）
    drawTangBoundary();
    
    // 绘制地点气泡
    drawLocationBubbles();
    
    // 绘制标题
    drawTitle();
}

function drawGrid() {
    stroke(200, 200, 200, 100);
    strokeWeight(1);
    
    // 绘制网格点
    for (let x = 50; x < mapWidth - 50; x += 15) {
        for (let y = 50; y < mapHeight - 50; y += 15) {
            point(x, y);
        }
    }
}

function drawTangBoundary() {
    if (!tangMapData) return;
    
    // 绘制内部小点填充
    drawInteriorDots();
    
    // 可选：绘制重要城市
    drawHistoricalCities();
}

// 新增函数：在疆域内部绘制小点填充
function drawInteriorDots() {
    if (!tangMapData || !tangMapData.boundary) return;
    
    // 使用详细边界文件的正确数据结构
    let boundary = tangMapData.boundary.coordinates[0];
    
    // 创建密集的点阵
    let dotSpacing = 8; // 点间距
    let baseDotSize = 2.5; // 基础点大小
    
    for (let x = 50; x < mapWidth - 50; x += dotSpacing) {
        for (let y = 50; y < mapHeight - 50; y += dotSpacing) {
            // 将屏幕坐标转换为地理坐标
            let lon = map(x, 50, mapWidth - 50, minLon, maxLon);
            let lat = map(y, 50, mapHeight - 50, maxLat, minLat);
            
            // 检查点是否在疆域内部
            if (isPointInPolygon(lon, lat, boundary)) {
                // 计算该点的热力值
                let heatValue = calculateHeatValue(x, y);
                
                // 根据热力值计算点的样式
                let pointStyle = calculatePointStyle(heatValue);
                
                fill(pointStyle.r, pointStyle.g, pointStyle.b, pointStyle.a);
                noStroke();
                // 将圆形改为方块，方块中心对齐
                rect(x - pointStyle.size/2, y - pointStyle.size/2, pointStyle.size, pointStyle.size);
            }
        }
    }
}

// 新增函数：计算热力值（所有地区的综合影响）
function calculateHeatValue(x, y) {
    if (!dataLoaded || locationData.length === 0) return 0;
    
    let totalHeat = 0;
    let maxInfluenceDistance = 100; // 最大影响距离
    
    for (let location of locationData) {
        let distance = dist(x, y, location.x, location.y);
        
        if (distance < maxInfluenceDistance) {
            // 每个地点的影响范围和强度都相同，不考虑频次
            let influence = (maxInfluenceDistance - distance) / maxInfluenceDistance;
            let heat = influence * influence; // 平方衰减，但不乘以频次
            totalHeat += heat;
        }
    }
    
    return totalHeat;
}

// 新增函数：根据热力值计算点的样式
function calculatePointStyle(heatValue) {
    // 将热力值映射到颜色和大小
    let normalizedHeat = Math.min(heatValue / 50, 1); // 归一化到0-1
    
    // 基础颜色：浅灰色到深灰色渐变
    let baseR = 200; // 浅灰色起始值
    let baseG = 200;
    let baseB = 200;
    
    // 根据热力值调整颜色深度（越热越深）
    let r = Math.floor(baseR - normalizedHeat * 150); // 200 -> 50 (深灰色)
    let g = Math.floor(baseG - normalizedHeat * 150); // 200 -> 50
    let b = Math.floor(baseB - normalizedHeat * 150); // 200 -> 50
    let a = Math.floor(80 + normalizedHeat * 70); // 透明度80-150
    
    // 根据热力值调整大小
    let size = 2.5 + normalizedHeat * 7; // 大小2.5-9.5像素
    
    return { r, g, b, a, size };
}

// 新增函数：检查点是否在多边形内部（射线法）
function isPointInPolygon(x, y, polygon) {
    let inside = false;
    let j = polygon.length - 1;
    
    for (let i = 0; i < polygon.length; i++) {
        let xi = polygon[i][0], yi = polygon[i][1];
        let xj = polygon[j][0], yj = polygon[j][1];
        
        if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) {
            inside = !inside;
        }
        j = i;
    }
    
    return inside;
}

function drawRivers() {
    if (!tangMapData || !tangMapData.rivers) return;
    
    stroke(100, 149, 237, 150);
    strokeWeight(2);
    noFill();
    
    for (let riverName in tangMapData.rivers) {
        let river = tangMapData.rivers[riverName];
        beginShape();
        noFill();
        for (let point of river.coordinates) {
            let lon = point[0];
            let lat = point[1];
            let x = map(lon, minLon, maxLon, 50, mapWidth - 50);
            let y = map(lat, maxLat, minLat, 50, mapHeight - 50);
            vertex(x, y);
        }
        endShape();
    }
}

function drawHistoricalCities() {
    if (!tangMapData || !tangMapData.cities) return;
    
    // 注释掉整个城市绘制循环，不显示棕色大点
    /*
    for (let cityName in tangMapData.cities) {
        let city = tangMapData.cities[cityName];
        let lon = city.coordinates[0];
        let lat = city.coordinates[1];
        let x = map(lon, minLon, maxLon, 50, mapWidth - 50);
        let y = map(lat, maxLat, minLat, 50, mapHeight - 50);
        
        // 根据城市重要性设置大小
        let size = map(city.importance, 1, 10, 3, 8);
        
        fill(139, 69, 19, 180); // 棕色
        noStroke();
        ellipse(x, y, size);
        
        // 移除重要城市名称显示
        // if (city.importance >= 8) {
        //     fill(139, 69, 19);
        //     textAlign(CENTER);
        //     textSize(10);
        //     text(cityName, x, y - size);
        // }
    }
    */
}

// 添加颜色解析辅助函数
function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

function drawLocationBubbles() {
    console.log('=== 开始绘制三角形 ===');
    console.log('dataLoaded:', dataLoaded);
    console.log('locationData长度:', locationData ? locationData.length : 'undefined');
    
    // 如果数据还没加载完成，直接返回
    if (!dataLoaded || !locationData || locationData.length === 0) {
        console.log('数据未加载或为空，跳过绘制');
        return;
    }
    
    // 计算动画进度
    let currentTime = millis();
    let elapsed = currentTime - animationStartTime;
    let animationProgress = Math.min(elapsed / animationDuration, 1.0);
    
    // 使用缓动函数让动画更自然
    let easeProgress = 1 - Math.pow(1 - animationProgress, 3); // ease-out cubic
    
    let hoveredLocation = null;
    let drawnCount = 0;
    
    for (let i = 0; i < locationData.length; i++) {
        let location = locationData[i];
        
        // 调整坐标映射，增加放大倍数并上移
        let x = map(location.lon, minLon, maxLon, 80, mapWidth - 80); // 增加边距从50到80
        let y = map(location.lat, maxLat, minLat, 30, mapHeight - 100); // 上移：从50改为30，下边距增加到100
        
        // 计算三角形高度（基于频次）- 增大尺寸
        let fullTriangleHeight = map(location.frequency, 1, 50, 25, 100); // 从15-60改为25-100
        let triangleBaseWidth = 35; // 从20改为35，增大底边宽度
        
        // 移除延迟，让所有三角形同时出现
        let delay = 0; // 从 i * 50 改为 0
        let triangleProgress = Math.max(0, Math.min((elapsed - delay) / animationDuration, 1.0));
        let triangleEase = 1 - Math.pow(1 - triangleProgress, 3);
        
        // 根据动画进度调整三角形高度
        let triangleHeight = fullTriangleHeight * triangleEase;
        
        // 如果三角形还没开始生长，跳过绘制
        if (triangleHeight <= 0) {
            continue;
        }
        
        // 获取颜色
        let bubbleColor = colorMap[location.type] || '#999999';
        
        // 检查是否应该变灰或高亮
        let shouldBeGray = false;
        let shouldBeHighlighted = false;
        let scaleFactor = 1.0;
        
        if (clickedLegendType) {
            // 更新动画进度
            if (scaleAnimationProgress < 1.0) {
                scaleAnimationProgress += animationSpeed;
                scaleAnimationProgress = Math.min(scaleAnimationProgress, 1.0);
            }
            
            // 使用缓动函数计算当前缩放值
            let easedProgress = easeOutBack(scaleAnimationProgress);
            currentScale = 1.0 + (targetScale - 1.0) * easedProgress;
            
            // 如果有点击的图例
            if (clickedLegendType === location.type) {
                shouldBeHighlighted = true;
                scaleFactor = currentScale; // 使用动画缩放值
            } else {
                shouldBeGray = true;
            }
        } else if (hoveredLegendType) {
            // 如果没有点击但有悬浮
            shouldBeGray = hoveredLegendType !== location.type;
        }
        
        // 如果应该变灰，使用灰色
        if (shouldBeGray) {
            bubbleColor = '#D0D0D0';  // 使用更浅的灰色
        }
        
        // 应用缩放因子
        let scaledTriangleHeight = triangleHeight * scaleFactor;
        let scaledTriangleBaseWidth = triangleBaseWidth * scaleFactor;
        
        // 解析颜色
        let rgb = hexToRgb(bubbleColor);
        if (!rgb) {
            rgb = {r: 153, g: 153, b: 153}; // 默认灰色
        }
        
        // 创建渐变效果（和图例一样）
        let gradient = drawingContext.createLinearGradient(
            location.x, location.y - scaledTriangleHeight, // 渐变起点（三角形顶部）
            location.x, location.y                         // 渐变终点（三角形底部）
        );
        
        // 设置渐变色停
        if (shouldBeHighlighted) {
            // 高亮时使用更鲜艳的颜色
            gradient.addColorStop(0, `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 1.0)`);
            gradient.addColorStop(1, `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.3)`);
        } else {
            gradient.addColorStop(0, `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 1.0)`);
            gradient.addColorStop(1, `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.1)`);
        }
        
        // 使用渐变填充
        drawingContext.fillStyle = gradient;
        
        // 去掉描边
        noStroke();
        
        // 绘制三角形（从底部向上生长）
        beginShape();
        vertex(location.x, location.y - scaledTriangleHeight); // 顶点
        vertex(location.x - scaledTriangleBaseWidth/2, location.y); // 左下角
        vertex(location.x + scaledTriangleBaseWidth/2, location.y); // 右下角
        endShape(CLOSE);
        
        drawnCount++;
        
        // 每绘制前5个三角形时输出调试信息
        if (i < 5) {
            console.log(`绘制渐变三角形 ${i + 1}: ${location.name} 在 (${location.x.toFixed(1)}, ${location.y.toFixed(1)}), 高度: ${triangleHeight.toFixed(1)}, 进度: ${(triangleEase * 100).toFixed(1)}%`);
        }
        
        // 检查鼠标悬浮（只有完全显示的三角形才能悬浮）
        if (triangleProgress >= 1.0) {
            let isHovered = isPointInTriangle(mouseX, mouseY, location.x, location.y, triangleBaseWidth, fullTriangleHeight);
            if (isHovered) {
                hoveredLocation = location;
            }
        }
    }
    
    // 动画完成后停止动画状态
    if (animationProgress >= 1.0) {
        isAnimating = false;
    }
    
    console.log(`实际绘制了 ${drawnCount} 个渐变三角形，总动画进度: ${(animationProgress * 100).toFixed(1)}%`);
    
    // 处理tooltip显示
    if (hoveredLocation) {
        showTooltip(hoveredLocation);
    } else {
        hideTooltip();
    }
}

// 新增函数：检测点是否在三角形内
function isPointInTriangle(px, py, centerX, centerY, baseWidth, height) {
    // 三角形的三个顶点
    let x1 = centerX;                    // 顶点
    let y1 = centerY - height;
    let x2 = centerX - baseWidth/2;      // 左下角
    let y2 = centerY;
    let x3 = centerX + baseWidth/2;      // 右下角
    let y3 = centerY;
    
    // 使用重心坐标法判断点是否在三角形内
    let denominator = ((y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3));
    if (Math.abs(denominator) < 0.001) return false;
    
    let a = ((y2 - y3)*(px - x3) + (x3 - x2)*(py - y3)) / denominator;
    let b = ((y3 - y1)*(px - x3) + (x1 - x3)*(py - y3)) / denominator;
    let c = 1 - a - b;
    
    return a >= 0 && b >= 0 && c >= 0;
}

function drawTitle() {
    fill(139, 69, 19);
    noStroke();
    textAlign(CENTER, TOP);
    textSize(20);
    // text('唐代侠义诗地理名称频次分布', mapWidth/2, 10); // 已删除
    
    // 绘制北方向标识
    textAlign(LEFT, CENTER);
    textSize(16);
    // text('北', 80, 80); // 已删除
    //text('宋', 80, 100);
}

function showTooltip(location) {
    tooltip.style('display', 'block');
    
    // 计算tooltip的位置，避免超出屏幕边界
    let tooltipX = mouseX + 10;
    let tooltipY = mouseY - 10;
    
    // 检查右边界 - 如果tooltip会超出画布右边，则显示在鼠标左侧
    if (tooltipX + 200 > mapWidth) { // 假设tooltip宽度约200px
        tooltipX = mouseX - 210;
    }
    
    // 检查下边界 - 如果tooltip会超出画布下边，则显示在鼠标上方
    if (tooltipY + 80 > mapHeight) { // 假设tooltip高度约80px
        tooltipY = mouseY - 90;
    }
    
    // 检查左边界
    if (tooltipX < 0) {
        tooltipX = 10;
    }
    
    // 检查上边界
    if (tooltipY < 0) {
        tooltipY = 10;
    }
    
    tooltip.style('left', tooltipX + 'px');
    tooltip.style('top', tooltipY + 'px');
    
    // 确保所有字段都有值，避免显示undefined或null
    let currentName = location.name || '未知地名';
    let historicalNames = location.historicalNames || '无历史地名记录';
    let frequency = location.frequency || 0;
    
    let content = `
        现今地名: ${currentName}<br>
        历史地名: ${historicalNames}<br>
        出现频次: ${frequency}次
    `;
    
    tooltip.html(content);
}

function hideTooltip() {
    tooltip.style('display', 'none');
}

// 窗口大小改变时重新调整
function windowResized() {
    // 可以在这里添加响应式调整逻辑
}

// 新增：缓动函数
function easeOutBack(t) {
    const c1 = 1.70158;
    const c3 = c1 + 1;
    return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
}

function easeOutElastic(t) {
    const c4 = (2 * Math.PI) / 3;
    return t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
}