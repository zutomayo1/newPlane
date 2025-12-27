# 音效包文件夹

此文件夹存放各种音效包的音效文件。

## 文件夹结构
```
sfx_packs/
├── classic/      # 经典街机风格
│   ├── shoot.wav
│   ├── explosion.wav
│   ├── hit.wav
│   ├── laser.wav
│   ├── levelup.wav
│   └── powerup.wav
├── cyber/        # 赛博朋克风格
├── retro/        # 复古芯片风格
├── kawaii/       # 可爱甜心风格
├── dark/         # 暗黑深渊风格
└── scifi/        # 星际科幻风格
```

## 工作原理
1. **首次使用**：系统会根据配置参数自动生成音效并保存为 `.wav` 文件
2. **后续加载**：直接读取已生成的文件，无需重新生成
3. **自定义覆盖**：将你自己的 `.wav` 文件放入对应文件夹即可替换

## 自定义音效
- 支持格式：`.wav` (推荐 22050Hz, 16-bit, mono)
- 文件名必须与系统音效名一致：
  - `shoot.wav` - 射击音效
  - `explosion.wav` - 爆炸音效
  - `hit.wav` - 击中音效
  - `laser.wav` - 激光音效
  - `levelup.wav` - 升级音效
  - `powerup.wav` - 能量提升音效

## 创建自定义音效包
1. 在此文件夹创建一个新文件夹（如 `my_pack`）
2. 放入上述6个音效文件
3. 在 `custom_audio.json` 中添加配置
