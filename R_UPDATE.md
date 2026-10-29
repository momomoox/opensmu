# R 电阻扫描更新

本更新基于 momomoox/opensmu 的 1442aaf。只包含修改的源码，不包含 .venv、config/config.json、测量数据和打包文件。

1. 关闭 OpenSMU，备份现有源码文件夹。
2. 将 ZIP 内的 model、presenter、view、test 文件夹及 README.md 合并复制到现有源码项目根目录（run.py 所在文件夹），替换同名文件。不要删掉原项目中的其他文件。
3. 在项目根目录运行：
   .venv\Scripts\python run.py
4. Configuration → SMU Control：选择 Keithley 2450、正确 USB 地址、FRONT/REAR 接口和 R 模式；仪器选原生 SCPI。
5. R 页设置扫描电压和电流限制。默认四线，需要接好 FORCE 和 SENSE；两线请取消勾选。File 页选择可写的保存目录。
6. Start 后显示 R、拟合标准误差、R²、offset、V–I 图及拟合线。R 文件保存原始测量及拟合结果。
7. 硬件测量确认后重新打包：
   .venv\Scripts\python -m PyInstaller installer\opensmu.spec --distpath installer\dist --workpath installer\build --clean --noconfirm
8. GitHub Desktop 查看 Changes → Commit → Push origin，即可把更新上传到自己的仓库。

已通过 73 项自动测试，包含模拟测量、UI、拟合与错误处理。尚未用真实 2450 或 Windows 打包验证。R 模式暂支持 2450 和 Simulation；IV/RT 设置保留。
