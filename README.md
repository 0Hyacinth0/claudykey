# ClaudyKey — AI 智能键盘连点器

一个运行在 Windows 11 上的智能自动化工具，支持键盘宏编辑、图像识别触发和 OCR 文字识别触发，本地 GPU 加速。

---

## ⚡ 一键包（推荐）— 解压即用，不污染系统环境

### 构建独立运行包（首次，约 10-30 分钟）

双击 **`build_bundle.bat`**，脚本会自动完成：

1. 下载 Python 3.11 嵌入式运行时 → `env\`
2. 安装 PyTorch CUDA + EasyOCR + 所有依赖 → `env\`
3. 预下载 EasyOCR 语言模型

> **CUDA 版本**：默认 `cu121`（CUDA 12.x）。如果你的驱动是 CUDA 11.8，请在 `build_bundle.bat` 第 18 行把 `cu121` 改为 `cu118`。

### 启动程序

| 文件 | 用途 |
|---|---|
| **`ClaudyKey.bat`** | 正常启动（无控制台窗口） |
| `ClaudyKey_debug.bat` | 调试启动（显示错误输出） |

### 分发给他人

构建完成后，将整个 `claudykey\` 文件夹（含 `env\`）压缩为 ZIP，对方解压后直接双击 `ClaudyKey.bat` 即可，**无需安装任何软件**。

> ⚠️ 打包体积约 3-5GB（主要是 PyTorch CUDA 库），属于正常大小。

---

## 功能特性

- **键盘宏循环编辑器** — 创建包含鼠标点击、按键、延时、嵌套循环的动作序列
- **图像触发器** — 屏幕特定区域出现目标图标时自动触发动作（OpenCV 模板匹配，<5ms）
- **文字触发器** — 屏幕特定区域识别到目标文字时触发（EasyOCR CUDA 加速）
- **可视化框选工具** — 全屏半透明遮罩，拖拽选择监控区域
- **坐标拾取器** — 点击屏幕任意位置直接获取坐标
- **全局热键** — `F9` 一键开始/停止运行
- **项目保存/加载** — 所有配置存为 JSON 文件

---

## 安装方法

### 1. 环境要求

- Windows 11
- Python 3.10+
- NVIDIA GPU（CUDA 11.x 或 12.x）

### 2. 安装 PyTorch（CUDA 版）

> 必须先安装 CUDA 版 PyTorch，否则 EasyOCR 将使用 CPU 模式

```bash
# CUDA 12.1（根据你的 CUDA 版本选择）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 3. 安装其余依赖

```bash
cd claudykey
pip install -r requirements.txt
```

### 4. 启动程序

```bash
python main.py
```

首次启动会在后台下载 EasyOCR 语言模型（约 200MB），之后会缓存到本地。

---

## 使用说明

### 创建宏序列
1. 点击左侧 **＋** 新建宏
2. 在右侧编辑区点击 **➕ 添加动作**
3. 选择动作类型（点击、按键、延时、循环…）
4. 坐标可点击 **🎯 屏幕拾取坐标** 直接在屏幕上选取
5. 配置完成后按 **▶ 运行** 或 `F9` 启动

### 配置图像触发器
1. 左侧触发器面板点 **＋** 新建触发器
2. 选择类型 **🖼 图像识别**
3. 点击 **📷 截取模板** — 全屏遮罩出现，拖拽框选目标图标（同时自动设定检测区域）
4. 调整 **相似度阈值**（默认 0.80，越高要求越严格）
5. 设置触发后执行的动作（执行宏 / 点击 / 按键）

### 配置文字触发器
1. 新建触发器，选择类型 **📝 文字识别**
2. 点击 **🔲 框选区域** 选定文字监控区域
3. 输入 **目标文字**，选择匹配方式（包含 / 精确 / 正则）
4. 设置触发后动作

### 热键
| 快捷键 | 功能 |
|--------|------|
| `F9` | 全局开始 / 停止 |
| `ESC` | 退出框选（在遮罩界面） |

---

## 项目结构

```
claudykey/
├── main.py              # 程序入口
├── requirements.txt
├── config/macros/       # 项目配置文件 (.json)
├── assets/templates/    # 图像模板存储目录
├── core/
│   ├── macro.py         # 数据模型
│   ├── screen.py        # 屏幕截图 (mss)
│   ├── image_match.py   # 图像匹配 (OpenCV)
│   ├── ocr.py           # 文字识别 (EasyOCR)
│   ├── executor.py      # 宏执行引擎
│   └── trigger.py       # 触发器引擎
└── gui/
    ├── main_window.py   # 主窗口
    ├── macro_editor.py  # 宏编辑器
    ├── trigger_editor.py# 触发器编辑器
    ├── region_selector.py# 框选工具
    └── theme.py         # 深色主题
```

---

## 注意事项

- **管理员权限**：若 pynput 无法监控全局热键或注入输入，请以管理员身份运行 `python main.py`
- **DPI 缩放**：如启用了 Windows 显示缩放（非 100%），模板匹配坐标可能偏移。建议在显示设置中将缩放设为 100%，或在程序中手动换算 DPI 比例
- **OCR 首次加载**：EasyOCR 首次启动约需 5-10 秒加载模型，之后为毫秒级响应
