# Visual C++ Redistributable 下载合集（2005–2026）

本仓库整理了多个版本的 Microsoft Visual C++ Redistributable 运行库下载地址，适用于程序缺少 DLL、运行报错等常见问题。

---

## 📌 2017–2026（VC++ 14.x / 最新支持）

- [vc_redist.x64.exe（2017–2026）](https://aka.ms/vc14/vc_redist.x64.exe)
- [vc_redist.x86.exe（2017–2026）](https://aka.ms/vc14/vc_redist.x86.exe)

---

## 📌 2013（VC++ 12.0）

- [vcredist_x64.exe](https://download.visualstudio.microsoft.com/download/pr/10912041/cee5d6bca2ddbcd039da727bf4acb48a/vcredist_x64.exe)
- [vcredist_x86.exe](https://download.visualstudio.microsoft.com/download/pr/10912113/5da66ddebb0ad32ebd4b922fd82e8e25/vcredist_x86.exe)

---

## 📌 2012（VC++ 11.0）

- [vcredist_x64.exe](http://download.microsoft.com/download/1/6/B/16B06F60-3B20-4FF2-B699-5E9B7962F9AE/VSU_4/vcredist_x64.exe)
- [vcredist_x86.exe](http://download.microsoft.com/download/1/6/B/16B06F60-3B20-4FF2-B699-5E9B7962F9AE/VSU_4/vcredist_x86.exe)

---

## 📌 2010（VC++ 10.0）

- [vcredist_x64.exe](http://download.microsoft.com/download/E/E/0/EE05C9EF-A661-4D9E-BCE2-6961ECDF087F/vcredist_x64.exe)
- [vcredist_x86.exe](http://download.microsoft.com/download/E/E/0/EE05C9EF-A661-4D9E-BCE2-6961ECDF087F/vcredist_x86.exe)

---

## 📌 2008（VC++ 9.0）

- [vcredist_x64_9.0.30729.7523.exe](https://gitlab.com/stdout12/adns/uploads/0f07341a2ba4f97011c7d9f567dc1684/vcredist_x64_9.0.30729.7523.exe)
- [vcredist_x86_9.0.30729.7523.exe](https://gitlab.com/stdout12/adns/uploads/bba8b7855325681d9849c766f439a614/vcredist_x86_9.0.30729.7523.exe)

---

## 📌 2005（VC++ 8.0）

- [vcredist_x64_8.0.50727.6229.exe](https://gitlab.com/stdout12/adns/uploads/c1aa6269e6bc0559c640c9dc2b11f98b/vcredist_x64_8.0.50727.6229.exe)
- [vcredist_x86_8.0.50727.6229.exe](https://gitlab.com/stdout12/adns/uploads/6e4cb29579c9ff812e79ffd7746d243a/vcredist_x86_8.0.50727.6229.exe)

---

## ⚠️ 使用说明

- `x86`：适用于 32 位程序  
- `x64`：适用于 64 位程序  
- 建议：所有版本可以共存安装，不会冲突  

---

## 自动化安装

本项目已内置 2005、2008、2010、2012、2013、2017-2026 的 x86/x64 自动安装配置，配置文件在 `runtime_data.py`。

### 1. 安装 Python 依赖

```powershell
pip install -r requirements.txt
```

### 2. 启动图形安装器

```powershell
python gui.py
```

点击“检测并安装”后，程序会：

- 按注册表检测已安装的 VC++ 运行库；
- 只安装缺失项；
- 优先复用 `offline/` 目录下已有离线安装包；
- 离线包不存在时按配置地址下载；
- 使用静默参数自动安装并禁止自动重启。

### 3. 注意事项

- 请用管理员权限运行终端或 VS Code，否则安装程序可能无法写入系统目录和注册表；
- 64 位 Windows 会同时检测并安装 x86 与 x64，32 位 Windows 只处理 x86；
- 安装返回码 `0` 通常表示成功，`3010` 通常表示安装成功但需要重启。
