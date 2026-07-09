# VC++ Runtime Manager

一个用于检测、准备和静默安装 Microsoft Visual C++ Redistributable 的 Windows 桌面工具。它覆盖 VC++ 2005、2008、2010、2012、2013 以及 2017-2026 的 x86/x64 运行库。

## 功能

- 读取 Windows 注册表，分别识别 x86 与 x64 运行库的安装状态和本机版本。
- 仅自动选择缺失项目；已安装项目仍可手动选择以获取最新包。
- 优先使用仓库中的 `offline/` 安装包，并对每个内置包进行 SHA-256 校验。
- 下载使用临时 `.part` 文件和原子替换，未完成的下载不会被当作可安装文件。
- 对 2017-2026 包，在用户选择安装后获取最新线上版本并与本机版本比较。
- 清楚区分“在线源可达”和“存在更新”：扫描页不会把前者误报为更新。
- 安装过程展示包准备、静默安装、返回代码与重启需求。

## 运行

需要 Windows 以及 Python 3.10 或更高版本。建议从管理员终端启动，以便安装程序能够写入系统目录和注册表。

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe gui.py
```

主界面会自动扫描。通常只需确认“待安装”项目，然后点击左下角的安装按钮。

## 使用说明

- `重新扫描`：重新读取本机状态，并检查 2017-2026 包的在线源可用性。
- `选择待处理项`：选择尚未安装的、当前系统可支持的运行库。
- `全选可用项`：包含已安装项目；适合需要重新运行安装器或检查最新版的场景。
- `打开离线包目录`：查看或替换缓存的安装包。替换后需要同时更新 `runtime_data.py` 中对应的 SHA-256。

安装器的返回代码 `0` 表示成功，`1638` 表示相同或更高版本已存在，`3010` 和 `1641` 表示安装完成后需要重启 Windows。

## 项目结构

```text
gui.py             CustomTkinter 图形界面
checker.py         注册表检测
downloader.py      下载、原子写入与包校验
installer.py       静默安装与返回代码处理
runtime_data.py    运行库元数据、下载源与 SHA-256
version_utils.py   版本比较和在线包信息
offline/           随仓库提供的离线安装包
tests/             自动化测试
```

## 验证

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

在线源验证依赖正常的 TLS 证书链。网络受代理或企业证书策略影响时，工具会保留 TLS 校验并回退到已校验的离线包，不会通过关闭证书验证来继续下载。
