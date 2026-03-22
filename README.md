# 🎞️ Copilot CLI × Minecraft GIF アニメーション実験 / GIF Animation Experiment

> **GitHub Copilot CLI を使って GIF アニメーションを Minecraft Java Edition 内でリアルタイム再生する実験です。**
>
> **An experiment using GitHub Copilot CLI to play GIF animations in real-time inside Minecraft Java Edition.**

| 元の GIF / Original GIF | Minecraft で再生 / Playback in Minecraft |
|:------------------------:|:----------------------------------------:|
| <img src="images/hula_loop_octodex03.gif" width="300"> | <!-- TODO: Minecraftスクリーンショットを追加 --> *画像は後から追加 / Image to be added* |

<!-- TODO: 動画リンクを追加 / Add video link -->
<!-- [![Octocat Animation Demo](https://img.youtube.com/vi/XXXXX/0.jpg)](https://youtu.be/XXXXX) -->

📌 **前回の実験 / Previous Experiment**: [copilot-cli-minecraft-experiment](https://github.com/ktanino10/copilot-cli-minecraft-experiment) — ブロックアート・東京タワー・計算機 / Block art, Tokyo Tower, Calculator

---

## 📖 目次 / Table of Contents

- [日本語](#-概要)
- [English](#-overview)

---

## 🇯🇵 概要

GitHub の Octocat（[Octodex](https://octodex.github.com/) の Hula Hoop Octocat）の GIF アニメーション（19フレーム）を、Minecraft Java Edition 内で 128×128 ブロックのアニメーションとして再生するデータパックを、GitHub Copilot CLI との対話だけで構築しました。

### セットアップ

#### 必要なもの

| ツール | バージョン / 備考 |
|--------|------------------|
| [Minecraft Java Edition](https://www.minecraft.net/ja-jp/store/minecraft-java-bedrock-edition-pc) | 1.21.x 推奨 |
| [GitHub Copilot CLI](https://docs.github.com/en/copilot/copilot-cli/using-github-copilot-cli) | `gh copilot` コマンド |
| [GitHub CLI (`gh`)](https://cli.github.com/) | 認証済みであること |
| Python 3 + Pillow | `pip install Pillow` |
| WSL2 (Windows の場合) | Linux 環境として使用 |

#### 使い方

```bash
# 1. GIF からデータパックを生成＆デプロイ
python3 create_gif_animation.py <GIF画像パス> <パック名> [サイズ] [ティック遅延]

# 例: Octodex Hula GIF を 128×128、3tick遅延で変換
python3 create_gif_animation.py hula_loop_octodex03.gif octcatmove 128 3

# 2. Minecraft 内で実行
/reload
/function octcatmove:place    # セットアップ＆自動再生開始
/function octcatmove:stop     # 一時停止
/function octcatmove:start    # 再開
/function octcatmove:remove   # 撤去
```

---

### 🔧 アニメーションの仕組み

#### システム構成

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│  GIF 分解    │ →  │ ブロック変換   │ →  │  データパック  │
│  19フレーム   │    │ CIE Lab色空間 │    │  tick.json   │
│  896×896px   │    │ ディザリング   │    │  marker方式  │
└─────────────┘    └──────────────┘    └──────────────┘
```

#### 再生の流れ

```
[ place コマンド実行 ]
     │
     ▼
┌──────────────────────────┐
│ 1. marker entity を召喚   │  ← 設置位置を記憶
│ 2. スコアボード初期化     │
│ 3. フレーム格納領域を確保  │  ← Z=300〜318 に forceload
└──────────────────────────┘
     │
     ▼
┌──────────────────────────┐
│ tick.json（毎ティック実行） │
│                          │
│ [ビルドフェーズ]           │  ← 1ティック1フレーム構築
│   #build = 0 → frame_0   │
│   #build = 1 → frame_1   │
│   ...                    │
│   #build = 18 → frame_18 │
│   #build = 19 → 完了!     │
│                          │
│ [アニメフェーズ]           │
│   3ティックごとに advance  │
│   clone で格納→表示壁コピー│  ← 高速・ちらつきなし
│   #frame を 0〜18 で循環   │
└──────────────────────────┘
```

#### 技術的なポイント

| 技術 | 説明 |
|------|------|
| **tick.json** | `data/minecraft/tags/function/tick.json` でティック関数を登録。コマンドブロック不使用でバージョン互換性が高い |
| **marker entity** | `summon marker` で設置位置を記憶。`execute as @e[tag=...] at @s` で正確な相対座標を実現 |
| **clone コマンド** | 格納エリアから表示壁へ1ティック内で一括コピー。ダブルバッファリングと同じ原理でちらつきなし |
| **CIE Lab 色空間** | 人間の色知覚に基づく色差計算。RGB ユークリッド距離より遥かに自然な色選択 |
| **Floyd-Steinberg ディザリング** | 量子化誤差を隣接ピクセルに拡散。78色でもグラデーションが滑らかに |
| **フラッドフィル背景除去** | 四隅から背景色を推定し、端から繋がった領域のみ透明化。キャラ内部の白（顔など）は保持 |

---

### 🎬 実際のアニメーションとの比較

| 要素 | 実際のアニメーション（映像） | Minecraft アニメーション |
|------|--------------------------|------------------------|
| **フレーム** | セル画 / デジタル画像（24fps が標準） | `.mcfunction` ファイル（1ファイル = 1フレーム） |
| **再生速度** | 1秒24コマ（映画）/ 30fps（TV） | 約6.7fps（3tick × 50ms = 150ms/フレーム） |
| **色数** | 1677万色（24bit カラー） | 78色（Minecraft ブロック限定パレット） |
| **色再現** | sRGB / DCI-P3 色空間 | CIE Lab 色空間で最近接ブロック選択 |
| **なめらかさの工夫** | 中割り / トゥイーニング | Floyd-Steinberg ディザリング |
| **フレーム切替** | フィルム送り / デジタルバッファ切替 | `clone` コマンドで格納エリアから一括コピー |
| **ループ制御** | タイムライン / ループ再生 | スコアボード変数でフレーム番号を循環 |
| **透明背景** | アルファチャンネル / クロマキー合成 | フラッドフィル方式で背景色を `air` に変換 |

#### 共通する原理

- **パラパラ漫画と同じ原理**: 人間の目の残像効果（persistence of vision）を利用し、連続する静止画を高速で切り替えることで動きを知覚させます。Minecraft でも同じ原理をブロックの置き換えで実現。
- **スプライトアニメーション**: ゲーム開発で使われるスプライトシート（1枚の画像に全フレームを並べたもの）と同様に、Minecraft では格納エリア（Z=300〜318）に全フレームを事前配置し、`clone` で表示壁にコピーします。
- **ダブルバッファリング**: 映像のちらつき防止技術と同様に、格納エリアから表示壁への `clone` は1ティック内で完了するため、ちらつきなく滑らかに切り替わります。

---

### 🚧 試行錯誤の記録

#### ❌ 失敗1: コマンドブロック方式

最初のアプローチでは、`repeating_command_block` を mcfunction ファイル内で `setblock` コマンドにより設置し、アニメーションのティックループを駆動しようとしました。

```mcfunction
# ❌ この構文がMinecraft 1.21+でパースエラー → 関数全体がロード失敗
setblock ~-3 ~-1 ~-1 minecraft:repeating_command_block{Command:"function octcatmove:build_step",auto:1b}
```

**原因**: Minecraft 1.20.5 以降でブロックエンティティの NBT 構文が変更され、`setblock` コマンド内の `{Command:"...",auto:1b}` がパースエラーに。結果として `place.mcfunction` だけがロード不可になり、他の関数は正常に表示されるが `place` だけが見つからないという現象が発生。

#### ❌ 失敗2: RGB ユークリッド距離による色選択

```python
# ❌ RGB空間での距離は人間の色知覚と大きくずれる
d = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
```

| 原画の色 | RGB距離の結果 | 問題 |
|---------|-------------|------|
| 肌色 `RGB(255,220,176)` | → `white_concrete` | 肌色が真っ白に |
| 暗紫灰 `RGB(42,37,47)` | → `gray_concrete` | キャラの体色が灰色に |
| ベージュ `RGB(217,188,156)` | → `white_concrete` | 暖色が全て白に |

#### ✅ 最終的に成功した方法

| 改善点 | 詳細 |
|--------|------|
| **tick.json 方式** | コマンドブロック不使用。バージョン互換性が高い |
| **marker entity** | 設置位置を正確に記憶 |
| **CIE Lab 色空間** | 知覚ベースの色差計算 |
| **Floyd-Steinberg ディザリング** | 78色でもグラデーションが滑らか |
| **パレット拡張** | 56色 → 78色（`blackstone`, `deepslate`, 木材系を追加） |

#### 色品質の比較

| 原画の色 | 旧方式（RGB距離） | 新方式（CIE Lab） |
|---------|-------------------|-------------------|
| 肌色 `(255,220,176)` | `white_concrete` ❌ | `end_stone_bricks` ✅ |
| 暗紫灰 `(42,37,47)` | `gray_concrete` ❌ | `polished_blackstone` ✅ |
| ベージュ `(217,188,156)` | `white_concrete` ❌ | `smooth_sandstone` ✅ |
| 暗い茶灰 `(85,75,63)` | `green_concrete` ❌ | `deepslate` ✅ |
| 中間灰 `(150,150,150)` | `light_gray_concrete` | `smooth_stone` ✅ |

---

### 🏫 教育版 Minecraft（Minecraft Education）での可能性

#### 実現可能な部分
- **ブロックアート（静止画）**: 教育版でも `setblock` コマンドは利用可能
- **スコアボードによる変数管理**: `scoreboard` コマンドは利用可能
- **基本的な `function` コマンド**: ビヘイビアパック形式でサポート

#### 課題・制限
- **`clone` コマンドの制限**: 128×128（16,384ブロック）の一括コピーは失敗する可能性あり
- **`tick.json` 非対応**: 代わりに `/tickingarea` や `system` イベントで代替が必要
- **`marker` エンティティ不在**: 透明なアーマースタンド等で代替が必要
- **パフォーマンス**: 低スペック端末では 87,000 ブロックは重い。64×64 以下への縮小推奨

#### 教育的な活用アイデア
- **小規模アニメーション（32×32, 4〜8フレーム）** から始めれば教育版でも実現可能
- **プログラミング教育**: 「画像をドット絵にする」「ループで動かす」を視覚的に学べる
- **数学**: 色空間の変換（RGB → Lab）は座標変換の実例
- **アート**: 限られた色数での表現は創造性を育てる

---

### やってみてわかったこと

- GIF アニメーションの再生という高度な課題にも、Copilot CLI との対話で試行錯誤しながら到達できた
- **失敗から学ぶプロセス**（コマンドブロック NBT 構文の非互換 → tick.json 方式への切り替え）も Copilot CLI が支援
- CIE Lab 色空間やディザリングといった**画像処理の専門知識**も、Copilot CLI が適切に適用
- 実際のアニメーション技術（パラパラ漫画、スプライト、ダブルバッファリング）と同じ原理が Minecraft 内で再現できることを実証

---

## 🇬🇧 Overview

This project demonstrates playing a **19-frame GIF animation** of GitHub's Octocat ([Octodex](https://octodex.github.com/) Hula Hoop Octocat) in real-time inside **Minecraft Java Edition**, as a 128×128 block animation — built entirely through conversation with **GitHub Copilot CLI**.

### Setup

#### Prerequisites

| Tool | Version / Notes |
|------|----------------|
| [Minecraft Java Edition](https://www.minecraft.net/en-us/store/minecraft-java-bedrock-edition-pc) | 1.21.x recommended |
| [GitHub Copilot CLI](https://docs.github.com/en/copilot/copilot-cli/using-github-copilot-cli) | `gh copilot` command |
| [GitHub CLI (`gh`)](https://cli.github.com/) | Must be authenticated |
| Python 3 + Pillow | `pip install Pillow` |
| WSL2 (on Windows) | Used as Linux environment |

#### Usage

```bash
# 1. Generate & deploy datapack from GIF
python3 create_gif_animation.py <gif_path> <pack_name> [size] [tick_delay]

# Example: Convert Octodex Hula GIF at 128×128, 3-tick delay
python3 create_gif_animation.py hula_loop_octodex03.gif octcatmove 128 3

# 2. Run in Minecraft
/reload
/function octcatmove:place    # Setup & auto-play
/function octcatmove:stop     # Pause
/function octcatmove:start    # Resume
/function octcatmove:remove   # Remove
```

---

### 🔧 How the Animation Works

#### System Architecture

```
┌──────────────┐    ┌───────────────┐    ┌──────────────┐
│ GIF Decompose │ →  │ Block Convert  │ →  │   Datapack   │
│  19 frames    │    │ CIE Lab color  │    │   tick.json  │
│  896×896px    │    │  Dithering     │    │ marker-based │
└──────────────┘    └───────────────┘    └──────────────┘
```

#### Playback Flow

```
[ /function octcatmove:place ]
     │
     ▼
┌───────────────────────────┐
│ 1. Summon marker entity    │  ← Remembers placement position
│ 2. Initialize scoreboards  │
│ 3. Forceload storage area  │  ← Z=300–318
└───────────────────────────┘
     │
     ▼
┌───────────────────────────┐
│ tick.json (runs every tick) │
│                            │
│ [Build Phase]              │  ← 1 frame per tick
│   #build = 0 → frame_0    │
│   #build = 1 → frame_1    │
│   ...                     │
│   #build = 18 → frame_18  │
│   #build = 19 → done!     │
│                            │
│ [Animation Phase]          │
│   Every 3 ticks → advance  │
│   clone: storage → display │  ← Fast, flicker-free
│   #frame cycles 0–18       │
└───────────────────────────┘
```

#### Technical Details

| Technology | Description |
|-----------|-------------|
| **tick.json** | Registers tick function via `data/minecraft/tags/function/tick.json`. Zero command blocks — high version compatibility |
| **marker entity** | `summon marker` remembers placement position. `execute as @e[tag=...] at @s` for accurate relative coordinates |
| **clone command** | Bulk copy from storage to display wall in 1 tick. Same principle as double buffering — no flicker |
| **CIE Lab color space** | Perceptually-based color distance. Far more natural color selection than RGB Euclidean distance |
| **Floyd-Steinberg dithering** | Spreads quantization error to neighboring pixels. Smooth gradients even with 78 colors |
| **Flood-fill background removal** | Detects background color from corners, removes only edge-connected regions. Preserves internal whites (e.g., face) |

---

### 🎬 Comparison with Real Animation

| Element | Traditional Animation | Minecraft Animation |
|---------|----------------------|---------------------|
| **Frames** | Cel drawings / digital images (24fps) | `.mcfunction` files (1 file = 1 frame) |
| **Playback Speed** | 24fps (film) / 30fps (TV) | ~6.7fps (3 ticks × 50ms = 150ms/frame) |
| **Colors** | 16.7M colors (24-bit) | 78 colors (Minecraft block palette) |
| **Color Reproduction** | sRGB / DCI-P3 color space | CIE Lab nearest-block selection |
| **Smoothness Technique** | In-betweening / tweening | Floyd-Steinberg dithering |
| **Frame Switching** | Film advance / digital buffer swap | `clone` command: bulk copy from storage |
| **Loop Control** | Timeline / loop playback | Scoreboard variables cycling frame numbers |
| **Transparent Background** | Alpha channel / chroma key | Flood-fill background detection → `air` blocks |

#### Shared Principles

- **Flipbook Principle**: Both use *persistence of vision* — rapidly switching static images to create the illusion of motion. Minecraft achieves this by replacing blocks at high speed.
- **Sprite Animation**: Similar to sprite sheets in game development (all frames in one image), Minecraft pre-places all frames in a storage area (Z=300–318) and uses `clone` to copy to the display wall.
- **Double Buffering**: Just as video systems prevent flicker by writing to an off-screen buffer, the `clone` command completes in a single tick, ensuring smooth, flicker-free transitions.

---

### 🚧 Trial and Error

#### ❌ Failure 1: Command Block Method

The initial approach tried to place `repeating_command_block` via `setblock` inside mcfunction to drive the animation tick loop.

```mcfunction
# ❌ Parse error in Minecraft 1.21+ — entire function fails to load
setblock ~-3 ~-1 ~-1 minecraft:repeating_command_block{Command:"function octcatmove:build_step",auto:1b}
```

**Root Cause**: Since Minecraft 1.20.5, block entity NBT syntax in `setblock` changed. The `{Command:"...",auto:1b}` caused a parse error, preventing `place.mcfunction` from loading. Other functions appeared normally — only `place` was missing.

#### ❌ Failure 2: RGB Euclidean Distance for Color Selection

```python
# ❌ RGB-space distance doesn't match human color perception
d = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
```

| Original Color | RGB Distance Result | Problem |
|---------------|--------------------|---------| 
| Skin `RGB(255,220,176)` | → `white_concrete` | Skin turned white |
| Dark purple-gray `RGB(42,37,47)` | → `gray_concrete` | Character body became gray |
| Beige `RGB(217,188,156)` | → `white_concrete` | All warm tones mapped to white |

#### ✅ What Worked: tick.json + marker entity + CIE Lab

| Improvement | Details |
|-------------|---------|
| **tick.json** | Zero command blocks — high version compatibility |
| **marker entity** | Accurately remembers placement position |
| **CIE Lab color space** | Perceptually-based color matching |
| **Floyd-Steinberg dithering** | Smooth gradients even with 78 colors |
| **Expanded palette** | 56 → 78 colors (added `blackstone`, `deepslate`, wood planks) |

#### Color Quality Comparison

| Original Color | Old (RGB) | New (CIE Lab) |
|----------------|-----------|---------------|
| Skin `(255,220,176)` | `white_concrete` ❌ | `end_stone_bricks` ✅ |
| Dark purple-gray `(42,37,47)` | `gray_concrete` ❌ | `polished_blackstone` ✅ |
| Beige `(217,188,156)` | `white_concrete` ❌ | `smooth_sandstone` ✅ |
| Dark brown-gray `(85,75,63)` | `green_concrete` ❌ | `deepslate` ✅ |
| Mid gray `(150,150,150)` | `light_gray_concrete` | `smooth_stone` ✅ |

---

### 🏫 Minecraft Education Edition — Feasibility

#### What's Possible
- **Block art (still images)**: `setblock` commands work in Education Edition
- **Scoreboard variables**: `scoreboard` commands are available
- **Basic `function` command**: Supported via behavior pack format

#### Challenges
- **`clone` limits**: 128×128 (16,384 blocks) may fail. Recommend 64×64 or smaller
- **No `tick.json`**: Use `/tickingarea` or system events instead
- **No `marker` entity**: Use invisible armor stands as alternative
- **Performance**: 87,000 blocks may be heavy on low-spec devices. Scale down to 32×32

#### Educational Ideas
- **Small animations (32×32, 4–8 frames)** are feasible in Education Edition
- **Programming**: "Decomposing images into pixels" and "loop-based animation" become visually tangible
- **Mathematics**: Color space conversion (RGB → Lab) as a coordinate transformation example
- **Art**: Creating within limited color palettes fosters creativity

---

### Key Takeaways

- **GIF animation playback** in Minecraft — an advanced challenge — was achieved through iterative conversation with Copilot CLI
- The **learning-from-failure process** (command block NBT → tick.json migration) was guided by Copilot CLI
- Specialized **image processing knowledge** (CIE Lab, dithering) was correctly applied by Copilot CLI
- Real animation principles (flipbook, sprite sheets, double buffering) were successfully reproduced in Minecraft

---

## ⚠️ ロゴの使用について / Logo Usage Disclaimer

Octocat および GitHub ロゴは [GitHub Logos and Usage](https://github.com/logos) のガイドラインに従っています。本リポジトリは**非商用・教育目的**での使用であり、GitHub の商標を侵害する意図はありません。Octodex のイラストは [GitHub Octodex](https://octodex.github.com/) からのもので、GitHub, Inc. に帰属します。

The Octocat and GitHub logos are used in accordance with the [GitHub Logos and Usage](https://github.com/logos) guidelines. This repository is for **non-commercial, educational purposes only** and does not intend to infringe on GitHub's trademarks. Octodex illustrations are from [GitHub Octodex](https://octodex.github.com/) and belong to GitHub, Inc.

---

## 📝 License

MIT License — see [LICENSE](LICENSE)

## 🔗 参考リンク / References

- [前回の実験 / Previous Experiment: copilot-cli-minecraft-experiment](https://github.com/ktanino10/copilot-cli-minecraft-experiment)
- [GitHub Copilot CLI Documentation](https://docs.github.com/en/copilot/copilot-cli/using-github-copilot-cli)
- [GitHub CLI](https://cli.github.com/)
- [Minecraft Java Edition Datapacks](https://minecraft.wiki/w/Data_pack)
- [GitHub Logos and Usage Guidelines](https://github.com/logos)
- [GitHub Octodex](https://octodex.github.com/)
- [Minecraft Wiki - Commands](https://minecraft.wiki/w/Commands)
- [CIE Lab Color Space (Wikipedia)](https://en.wikipedia.org/wiki/CIELAB_color_space)
- [Floyd-Steinberg Dithering (Wikipedia)](https://en.wikipedia.org/wiki/Floyd%E2%80%93Steinberg_dithering)
