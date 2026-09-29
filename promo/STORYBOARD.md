# THE UNREASONABLE BEAUTY — 分镜构思 (Storyboard)

> 数学 · 物理 · 计算机 三学科之美的动画宣传片（英文画面文字）
> 工具：Manim Community (3Blue1Brown 同款开源数学动画引擎) + LaTeX + NumPy + FFmpeg；背景音乐由 NumPy 程序合成。

## 核心构思

片名取自物理学家 Wigner 的名文 *"The Unreasonable Effectiveness of Mathematics in the Natural Sciences"*。

一条贯穿全片的主线：

- **Mathematics is the language**（数学是语言）— 蓝色
- **Physics is the story**（物理是故事）— 橙色
- **Computation is the pen**（计算是笔）— 绿色

每一章右上角用三个彩色圆点标注本章涉及的学科。三门学科不是轮流登场，而是在同一个画面里互相推动：
数列 → 二进制 → 质数 → 黎曼猜想；微积分 → 牛顿引力 → 计算机逐步数值积分 → 神经网络梯度下降；
欧拉公式 → 傅里叶级数 → 电磁波 / 量子波函数 → MP3/JPEG 压缩 → 量子比特。
结尾所有线索回到片头的那三个点。

难度从小学一路讲到研究前沿：

| 章 | 标题 | 层次 | 内容 | 学科 |
|---|---|---|---|---|
| 0 | Opening | — | 一个点 → 分裂成三个点 → 片名 | 全部 |
| I | NUMBER | 小学 | 高斯求和的图形证明；二进制计数；埃拉托斯特尼筛法找质数 | 数学 · 计算机 |
| II | SHAPE | 初中 | 勾股定理拼图证明；圆滚动展开 π 并画出摆线（最速降线）；伽利略名言 | 数学 · 物理 |
| III | CHANGE | 高中 / 大一 | 导数（切线）、积分（黎曼和）；牛顿万有引力 + 计算机逐步积分出轨道；三体"8字形"周期解 | 全部 |
| IV | WAVES | 大学 | 欧拉公式 e^{iπ}+1=0 与单位圆；傅里叶级数：旋转圆圈画出 π | 全部 |
| V | LIGHT & QUANTA | 大学 | 麦克斯韦方程组与电磁波；双缝干涉：波函数、单个粒子一颗颗堆出干涉条纹 | 数学 · 物理 |
| VI | COMPUTATION | 大学 | 图灵机做二进制加一；快速排序；康威生命游戏；曼德博集合放大 | 全部 |
| VII | LEARNING | 前沿应用 | 神经网络前向传播；损失曲面上的梯度下降 | 数学 · 计算机 |
| VIII | THE FRONTIER | 研究前沿 | 广义相对论时空弯曲与引力波；量子比特（Bloch 球）；黎曼 ζ 函数在临界线上的轨迹与零点；未解之谜 | 全部 |
| ∞ | Finale | — | 三个点重聚："The next chapter is unwritten. Come write it." | 全部 |

## 制作方式

- `promo/film.py` — 全部场景代码（每章一个 Scene 类）
- `promo/music.py` — 用 NumPy 合成环境氛围配乐（和弦铺底 + 钟声琶音），时长与画面自动匹配
- `promo/build.sh` — 渲染所有场景、拼接、混入音乐，输出 `promo/output/the_unreasonable_beauty.mp4`
