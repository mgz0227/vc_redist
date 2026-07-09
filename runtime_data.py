# runtime_data.py

RUNTIMES = [
    {
        "id": "vc2026_x64",
        "name": "VC++ 2017-2026 x64",
        "version_key": "14.0",
        "arch": "x64",
        "url": "https://aka.ms/vc14/vc_redist.x64.exe",
        "offline_path": "offline/2017-2026/VC_redist.x64.exe",
        "cloud_version_check": True,
        "registry_checks": ["SOFTWARE\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x64"],
        "sha256": "",
        "silent_args": "/install /quiet /norestart"
    },
    {
        "id": "vc2026_x86",
        "name": "VC++ 2017-2026 x86",
        "version_key": "14.0",
        "arch": "x86",
        "url": "https://aka.ms/vc14/vc_redist.x86.exe",
        "offline_path": "offline/2017-2026/VC_redist.x86.exe",
        "cloud_version_check": True,
        "registry_checks": ["SOFTWARE\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x86"],
        "sha256": "",
        "silent_args": "/install /quiet /norestart"
    },
    {
        "id": "vc2013_x64",
        "name": "VC++ 2013 x64",
        "version_key": "12.0",
        "arch": "x64",
        "url": "https://download.visualstudio.microsoft.com/download/pr/10912041/cee5d6bca2ddbcd039da727bf4acb48a/vcredist_x64.exe",
        "offline_path": "offline/2013/vcredist_x64.exe",
        "registry_checks": ["SOFTWARE\\Microsoft\\VisualStudio\\12.0\\VC\\Runtimes\\x64"],
        "sha256": "",
        "silent_args": "/install /quiet /norestart"
    },
    {
        "id": "vc2013_x86",
        "name": "VC++ 2013 x86",
        "version_key": "12.0",
        "arch": "x86",
        "url": "https://download.visualstudio.microsoft.com/download/pr/10912113/5da66ddebb0ad32ebd4b922fd82e8e25/vcredist_x86.exe",
        "offline_path": "offline/2013/vcredist_x86.exe",
        "registry_checks": ["SOFTWARE\\Microsoft\\VisualStudio\\12.0\\VC\\Runtimes\\x86"],
        "sha256": "",
        "silent_args": "/install /quiet /norestart"
    },
    {
        "id": "vc2012_x64",
        "name": "VC++ 2012 x64",
        "version_key": "11.0",
        "arch": "x64",
        "url": "http://download.microsoft.com/download/1/6/B/16B06F60-3B20-4FF2-B699-5E9B7962F9AE/VSU_4/vcredist_x64.exe",
        "offline_path": "offline/2012/vcredist_x64.exe",
        "registry_checks": ["SOFTWARE\\Microsoft\\VisualStudio\\11.0\\VC\\Runtimes\\x64"],
        "sha256": "",
        "silent_args": "/install /quiet /norestart"
    },
    {
        "id": "vc2012_x86",
        "name": "VC++ 2012 x86",
        "version_key": "11.0",
        "arch": "x86",
        "url": "http://download.microsoft.com/download/1/6/B/16B06F60-3B20-4FF2-B699-5E9B7962F9AE/VSU_4/vcredist_x86.exe",
        "offline_path": "offline/2012/vcredist_x86.exe",
        "registry_checks": ["SOFTWARE\\Microsoft\\VisualStudio\\11.0\\VC\\Runtimes\\x86"],
        "sha256": "",
        "silent_args": "/install /quiet /norestart"
    },
    {
        "id": "vc2010_x64",
        "name": "VC++ 2010 x64",
        "version_key": "10.0",
        "arch": "x64",
        "url": "http://download.microsoft.com/download/E/E/0/EE05C9EF-A661-4D9E-BCE2-6961ECDF087F/vcredist_x64.exe",
        "offline_path": "offline/2010/vcredist_x64.exe",
        "registry_checks": ["SOFTWARE\\Microsoft\\VisualStudio\\10.0\\VC\\VCRedist\\x64"],
        "sha256": "",
        "silent_args": "/q /norestart"
    },
    {
        "id": "vc2010_x86",
        "name": "VC++ 2010 x86",
        "version_key": "10.0",
        "arch": "x86",
        "url": "http://download.microsoft.com/download/E/E/0/EE05C9EF-A661-4D9E-BCE2-6961ECDF087F/vcredist_x86.exe",
        "offline_path": "offline/2010/vcredist_x86.exe",
        "registry_checks": ["SOFTWARE\\Microsoft\\VisualStudio\\10.0\\VC\\VCRedist\\x86"],
        "sha256": "",
        "silent_args": "/q /norestart"
    },
    {
        "id": "vc2008_x64",
        "name": "VC++ 2008 SP1 x64",
        "version_key": "9.0",
        "arch": "x64",
        "url": "https://gitlab.com/stdout12/adns/uploads/0f07341a2ba4f97011c7d9f567dc1684/vcredist_x64_9.0.30729.7523.exe",
        "offline_path": "offline/2008/vcredist_x64.exe",
        "registry_checks": ["SOFTWARE\\Microsoft\\DevDiv\\VC\\Servicing\\9.0\\RED\\1033"],
        "sha256": "",
        "silent_args": "/q /norestart"
    },
    {
        "id": "vc2008_x86",
        "name": "VC++ 2008 SP1 x86",
        "version_key": "9.0",
        "arch": "x86",
        "url": "https://gitlab.com/stdout12/adns/uploads/bba8b7855325681d9849c766f439a614/vcredist_x86_9.0.30729.7523.exe",
        "offline_path": "offline/2008/vcredist_x86.exe",
        "registry_checks": ["SOFTWARE\\Microsoft\\DevDiv\\VC\\Servicing\\9.0\\RED\\1033"],
        "sha256": "",
        "silent_args": "/q /norestart"
    },
    {
        "id": "vc2005_x64",
        "name": "VC++ 2005 SP1 x64",
        "version_key": "8.0",
        "arch": "x64",
        "url": "https://gitlab.com/stdout12/adns/uploads/c1aa6269e6bc0559c640c9dc2b11f98b/vcredist_x64_8.0.50727.6229.exe",
        "offline_path": "offline/2005/vcredist_x64.exe",
        "registry_checks": ["SOFTWARE\\Microsoft\\DevDiv\\VC\\Servicing\\8.0\\RED\\1033"],
        "sha256": "",
        "silent_args": "/q /norestart"
    },
    {
        "id": "vc2005_x86",
        "name": "VC++ 2005 SP1 x86",
        "version_key": "8.0",
        "arch": "x86",
        "url": "https://gitlab.com/stdout12/adns/uploads/6e4cb29579c9ff812e79ffd7746d243a/vcredist_x86_8.0.50727.6229.exe",
        "offline_path": "offline/2005/vcredist_x86.exe",
        "registry_checks": ["SOFTWARE\\Microsoft\\DevDiv\\VC\\Servicing\\8.0\\RED\\1033"],
        "sha256": "",
        "silent_args": "/q /norestart"
    }
]