#!/usr/bin/env python3
"""
Minecraft GIF Animation Data Pack Generator (v2)

GIFアニメーションをMinecraftデータパックに変換。
スコアボードベースのアニメーション制御（レバー不要）。
50色以上の拡張パレットで肌色・暖色系を正確に再現。

使い方:
  python3 create_gif_animation.py <gif_path> [pack_name] [size] [tick_delay]

例:
  python3 create_gif_animation.py /mnt/c/Users/81908/Downloads/hula_loop_octodex03.gif hula 64 3
"""

import sys
import os
import json
import shutil
from PIL import Image

# === 設定 ===
PROJECT_DIR = "/home/ktanino/project"
MINECRAFT_SAVES = "/mnt/c/Users/81908/AppData/Roaming/.minecraft/saves"
WORLD_NAME = "PCN Express"
DATAPACKS_DIR = f"{MINECRAFT_SAVES}/{WORLD_NAME}/datapacks"

# === CIE Lab 色空間変換（知覚的に正確な色マッチング） ===
import math

def _srgb_to_linear(c):
    """sRGB [0-255] → リニア [0-1]"""
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def rgb_to_lab(r, g, b):
    """RGB → CIE Lab 変換"""
    lr, lg, lb = _srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b)
    # RGB → XYZ (D65)
    x = (lr * 0.4124564 + lg * 0.3575761 + lb * 0.1804375) / 0.95047
    y = (lr * 0.2126729 + lg * 0.7151522 + lb * 0.0721750)
    z = (lr * 0.0193339 + lg * 0.1191920 + lb * 0.9503041) / 1.08883
    # XYZ → Lab
    def f(t):
        return t ** (1/3) if t > 0.008856 else (7.787 * t + 16/116)
    fx, fy, fz = f(x), f(y), f(z)
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b_val = 200 * (fy - fz)
    return (L, a, b_val)

def lab_distance(lab1, lab2):
    """CIE76 色差（Lab 空間のユークリッド距離）"""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(lab1, lab2)))

# 拡張カラーパレット — テクスチャが滑らかなブロックのみ使用
# ピクセルアートに最適: コンクリート(最滑) > ウール > テラコッタ > 滑らかな石系
COLOR_BLOCKS = [
    # === コンクリート (16色) — 最も滑らかで均一 ===
    ((8,   10,  15),  "minecraft:black_concrete"),
    ((55,  58,  62),  "minecraft:gray_concrete"),
    ((125, 125, 115), "minecraft:light_gray_concrete"),
    ((207, 213, 214), "minecraft:white_concrete"),
    ((142, 33,  33),  "minecraft:red_concrete"),
    ((224, 97,  1),   "minecraft:orange_concrete"),
    ((241, 175, 21),  "minecraft:yellow_concrete"),
    ((73,  91,  36),  "minecraft:green_concrete"),
    ((94,  169, 25),  "minecraft:lime_concrete"),
    ((45,  47,  143), "minecraft:blue_concrete"),
    ((36,  137, 199), "minecraft:light_blue_concrete"),
    ((21,  119, 136), "minecraft:cyan_concrete"),
    ((100, 32,  156), "minecraft:purple_concrete"),
    ((214, 101, 143), "minecraft:pink_concrete"),
    ((96,  60,  32),  "minecraft:brown_concrete"),
    ((169, 48,  159), "minecraft:magenta_concrete"),
    # === テラコッタ (16色) — 暖色・肌色に最適 ===
    ((209, 178, 161), "minecraft:white_terracotta"),
    ((161, 83,  37),  "minecraft:orange_terracotta"),
    ((143, 61,  47),  "minecraft:red_terracotta"),
    ((77,  51,  36),  "minecraft:brown_terracotta"),
    ((186, 133, 35),  "minecraft:yellow_terracotta"),
    ((76,  83,  42),  "minecraft:green_terracotta"),
    ((103, 117, 53),  "minecraft:lime_terracotta"),
    ((113, 109, 138), "minecraft:blue_terracotta"),
    ((114, 137, 218), "minecraft:light_blue_terracotta"),
    ((86,  91,  91),  "minecraft:cyan_terracotta"),
    ((118, 70,  86),  "minecraft:purple_terracotta"),
    ((162, 78,  79),  "minecraft:pink_terracotta"),
    ((154, 129, 114), "minecraft:light_gray_terracotta"),
    ((58,  42,  36),  "minecraft:gray_terracotta"),
    ((37,  23,  16),  "minecraft:black_terracotta"),
    ((149, 88,  109), "minecraft:magenta_terracotta"),
    # === ウール (16色) — 滑らかで柔らかいテクスチャ ===
    ((234, 236, 236), "minecraft:white_wool"),
    ((244, 174, 168), "minecraft:pink_wool"),
    ((249, 198, 40),  "minecraft:yellow_wool"),
    ((199, 199, 199), "minecraft:light_gray_wool"),
    ((63,  68,  72),  "minecraft:gray_wool"),
    ((25,  22,  22),  "minecraft:black_wool"),
    ((180, 137, 103), "minecraft:brown_wool"),
    ((237, 141, 172), "minecraft:magenta_wool"),
    ((240, 118, 19),  "minecraft:orange_wool"),
    ((191, 68,  69),  "minecraft:red_wool"),
    ((112, 185, 26),  "minecraft:lime_wool"),
    ((58,  175, 56),  "minecraft:green_wool"),
    ((53,  57,  157), "minecraft:blue_wool"),
    ((28,  135, 162), "minecraft:cyan_wool"),
    ((122, 42,  173), "minecraft:purple_wool"),
    ((66,  214, 182), "minecraft:light_blue_wool"),
    # === 滑らかな石系ブロック ===
    ((216, 201, 163), "minecraft:smooth_sandstone"),
    ((213, 205, 195), "minecraft:calcite"),
    ((197, 179, 163), "minecraft:smooth_quartz"),
    ((236, 230, 224), "minecraft:quartz_block"),
    ((229, 225, 207), "minecraft:bone_block"),
    ((237, 201, 142), "minecraft:end_stone_bricks"),
    ((107, 153, 108), "minecraft:oxidized_copper"),
    ((181, 101, 77),  "minecraft:copper_block"),
    # === 追加ブロック — 不足色域の補強 ===
    ((74,  74,  74),  "minecraft:deepslate"),              # 暗灰色
    ((59,  59,  59),  "minecraft:deepslate_bricks"),       # 暗い灰色
    ((48,  45,  52),  "minecraft:blackstone"),             # 暗紫灰（キャラ体色に重要）
    ((40,  37,  43),  "minecraft:polished_blackstone"),    # さらに暗い紫灰
    ((130, 100, 70),  "minecraft:packed_mud"),             # 暖かい茶色
    ((134, 107, 80),  "minecraft:mud_bricks"),             # 中間茶色
    ((167, 139, 107), "minecraft:birch_planks"),           # 明るい木色（肌色近似）
    ((148, 103, 60),  "minecraft:jungle_planks"),          # 中間木色
    ((108, 78,  50),  "minecraft:spruce_planks"),          # 暗い木色
    ((85,  85,  85),  "minecraft:cobbled_deepslate"),      # 中間暗灰
    ((50,  50,  53),  "minecraft:polished_deepslate"),     # 暗灰
    ((160, 160, 155), "minecraft:smooth_stone"),           # 中間灰
    ((188, 152, 98),  "minecraft:stripped_birch_log"),     # 明るいベージュ
    ((255, 252, 245), "minecraft:snow_block"),             # 純白に近い
    ((78,  59,  37),  "minecraft:dark_oak_planks"),        # 暗い木色
    ((120, 82,  46),  "minecraft:oak_planks"),             # 中間木色
    ((188, 100, 68),  "minecraft:exposed_copper"),         # 暖色銅
    ((116, 167, 118), "minecraft:weathered_copper"),       # 緑がかった銅
    ((50,  44,  45),  "minecraft:basalt"),                 # 暗灰紫
    ((171, 175, 176), "minecraft:polished_andesite"),      # 明るい灰
    ((136, 136, 136), "minecraft:andesite"),               # 中間灰
    ((184, 178, 172), "minecraft:polished_diorite"),       # 明るい灰白
]

# パレットの Lab 値を事前計算（高速化）
_PALETTE_LAB = [(rgb_to_lab(r, g, b), block) for (r, g, b), block in COLOR_BLOCKS]


def detect_background_color(frame):
    """画像の四隅から背景色を推定"""
    w, h = frame.size
    corners = [
        frame.getpixel((0, 0)),
        frame.getpixel((w-1, 0)),
        frame.getpixel((0, h-1)),
        frame.getpixel((w-1, h-1)),
    ]
    avg_r = sum(c[0] for c in corners) // 4
    avg_g = sum(c[1] for c in corners) // 4
    avg_b = sum(c[2] for c in corners) // 4
    return (avg_r, avg_g, avg_b)


def create_background_mask(frame, bg_color, threshold=30):
    """フラッドフィル方式で背景マスクを生成。
    画像の端から繋がった背景色領域のみを背景とする。
    キャラクター内部の白い部分（顔など）は保持される。"""
    from collections import deque
    w, h = frame.size
    bg_mask = [[False] * w for _ in range(h)]
    visited = [[False] * w for _ in range(h)]
    br, bg_r, bb = bg_color
    threshold_sq = threshold ** 2

    def is_bg_color(x, y):
        r, g, b, a = frame.getpixel((x, y))
        if a < 128:
            return True
        return (r - br) ** 2 + (g - bg_r) ** 2 + (b - bb) ** 2 < threshold_sq

    # 端のピクセルからフラッドフィル開始
    queue = deque()
    for x in range(w):
        for y in [0, h - 1]:
            if is_bg_color(x, y):
                queue.append((x, y))
                visited[y][x] = True
                bg_mask[y][x] = True
    for y in range(h):
        for x in [0, w - 1]:
            if not visited[y][x] and is_bg_color(x, y):
                queue.append((x, y))
                visited[y][x] = True
                bg_mask[y][x] = True

    while queue:
        cx, cy = queue.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx]:
                visited[ny][nx] = True
                if is_bg_color(nx, ny):
                    bg_mask[ny][nx] = True
                    queue.append((nx, ny))

    return bg_mask


def nearest_block(r, g, b, a=255):
    """CIE Lab 色空間で最も近い色のMinecraftブロックを返す"""
    if a < 128:
        return "minecraft:air"
    pixel_lab = rgb_to_lab(r, g, b)
    best = None
    best_dist = float('inf')
    for block_lab, block in _PALETTE_LAB:
        d = lab_distance(pixel_lab, block_lab)
        if d < best_dist:
            best_dist = d
            best = block
    return best


def nearest_block_with_rgb(r, g, b, a=255):
    """CIE Lab で最近接ブロックを返し、そのブロックの RGB 値も返す（ディザリング用）"""
    if a < 128:
        return "minecraft:air", (r, g, b)
    pixel_lab = rgb_to_lab(r, g, b)
    best = None
    best_dist = float('inf')
    best_rgb = (r, g, b)
    for i, (block_lab, block) in enumerate(_PALETTE_LAB):
        d = lab_distance(pixel_lab, block_lab)
        if d < best_dist:
            best_dist = d
            best = block
            best_rgb = COLOR_BLOCKS[i][0]
    return best, best_rgb


def create_gif_animation(gif_path, pack_name="hula", size=128, tick_delay=3, dither=True):
    """GIFからMinecraftアニメーションデータパックを生成"""

    # GIF読み込み
    img = Image.open(gif_path)
    n_frames = img.n_frames
    print(f"📖 GIF読込: {img.size[0]}x{img.size[1]}, {n_frames}フレーム")

    # 背景色を最初のフレームから検出
    img.seek(0)
    first_frame = img.convert("RGBA").resize((size, size), Image.LANCZOS)
    bg_color = detect_background_color(first_frame)
    print(f"🎨 背景色検出: RGB{bg_color}")
    print(f"🎨 拡張パレット: {len(COLOR_BLOCKS)}色 (CIE Lab + {'ディザリングON' if dither else 'ディザリングOFF'})")

    # 全フレーム抽出・変換（フラッドフィル背景除去 + Floyd-Steinberg ディザリング）
    frames = []
    for i in range(n_frames):
        img.seek(i)
        frame = img.convert("RGBA").resize((size, size), Image.LANCZOS)

        # 端から繋がった背景色のみ除去（キャラ内部の白=顔は保持）
        bg_mask = create_background_mask(frame, bg_color, threshold=35)

        # Floyd-Steinberg ディザリング用のピクセルバッファ
        pixels = [[list(frame.getpixel((px, py))) for px in range(size)] for py in range(size)]

        block_data = []
        for py in range(size):
            for px in range(size):
                if bg_mask[py][px]:
                    continue
                r, g, b, a = [int(max(0, min(255, v))) for v in pixels[py][px]]
                if a < 128:
                    continue

                block, block_rgb = nearest_block_with_rgb(r, g, b, a)
                if block == "minecraft:air":
                    continue

                # Floyd-Steinberg: 量子化誤差を隣接ピクセルに拡散
                if dither:
                    err_r = r - block_rgb[0]
                    err_g = g - block_rgb[1]
                    err_b = b - block_rgb[2]
                    # 拡散係数: 右 7/16, 左下 3/16, 下 5/16, 右下 1/16
                    for dx, dy, w in [(1,0,7/16), (-1,1,3/16), (0,1,5/16), (1,1,1/16)]:
                        nx, ny = px + dx, py + dy
                        if 0 <= nx < size and 0 <= ny < size and not bg_mask[ny][nx]:
                            pixels[ny][nx][0] += err_r * w
                            pixels[ny][nx][1] += err_g * w
                            pixels[ny][nx][2] += err_b * w

                x = px
                y = size - 1 - py  # Y軸反転（画像上→Minecraft上）
                block_data.append((x, y, block))

        frames.append(block_data)
        print(f"  フレーム {i}: {len(block_data)} ブロック（背景除去後）")

    # データパックディレクトリ作成
    pack_dir = f"{PROJECT_DIR}/{pack_name}_datapack"
    func_dir = f"{pack_dir}/data/{pack_name}/function"
    tag_dir = f"{pack_dir}/data/minecraft/tags/function"
    if os.path.exists(pack_dir):
        shutil.rmtree(pack_dir)
    os.makedirs(func_dir, exist_ok=True)
    os.makedirs(tag_dir, exist_ok=True)

    # pack.mcmeta
    with open(f"{pack_dir}/pack.mcmeta", "w") as f:
        json.dump({
            "pack": {
                "pack_format": 71,
                "description": f"{pack_name} GIF animation ({n_frames} frames)"
            }
        }, f, indent=2)

    # tick.json - tick function registration (no command blocks needed)
    with open(f"{tag_dir}/tick.json", "w") as f:
        json.dump({"values": [f"{pack_name}:tick"]}, f, indent=2)

    STORAGE_Z = 300
    TAG = f"{pack_name}_origin"
    SB = f"{pack_name}_anim"

    # ========================================
    # frame_N.mcfunction (setblock commands per frame)
    # ========================================
    for i, block_data in enumerate(frames):
        frame_z = STORAGE_Z + i
        commands = [f"# Frame {i} - {len(block_data)} blocks at Z={frame_z}"]
        for x, y, block in block_data:
            commands.append(f"setblock ~{x} ~{y} ~{frame_z} {block}")
        with open(f"{func_dir}/frame_{i}.mcfunction", "w") as f:
            f.write("\n".join(commands) + "\n")

    # ========================================
    # place.mcfunction - simple setup, NO command blocks
    # ========================================
    place_cmds = [
        f"# {pack_name} GIF Animation - Setup ({n_frames} frames, {size}x{size})",
        "",
        f"kill @e[tag={TAG}]",
        f"summon marker ~ ~ ~",
        f'tag @e[type=marker,sort=nearest,limit=1,distance=..1] add {TAG}',
        "",
        f"scoreboard objectives add {SB} dummy",
        f"scoreboard players set #tick {SB} 0",
        f"scoreboard players set #frame {SB} 0",
        f"scoreboard players set #build {SB} 0",
        f"scoreboard players set #playing {SB} 0",
        "",
        f"forceload add ~0 ~{STORAGE_Z} ~{size - 1} ~{STORAGE_Z + n_frames - 1}",
        f"fill ~0 ~0 ~0 ~{size - 1} ~{size - 1} ~0 air",
        "",
        f'tellraw @a [{{"text":"Building {pack_name}: {n_frames} frames...","color":"yellow"}}]',
    ]
    with open(f"{func_dir}/place.mcfunction", "w") as f:
        f.write("\n".join(place_cmds) + "\n")

    # ========================================
    # tick.mcfunction - runs every game tick via tick.json
    # Handles both build phase and animation phase
    # ========================================
    tick_cmds = [
        f"# Build phase: one frame per tick",
    ]
    for i in range(n_frames):
        tick_cmds.append(
            f"execute as @e[tag={TAG}] at @s "
            f"if score #build {SB} matches {i} "
            f"run function {pack_name}:frame_{i}"
        )
    tick_cmds.append(
        f"execute as @e[tag={TAG}] at @s "
        f"if score #build {SB} matches {n_frames} "
        f"run function {pack_name}:finish_setup"
    )
    tick_cmds.append(
        f"execute if score #build {SB} matches 0..{n_frames - 1} "
        f"run scoreboard players add #build {SB} 1"
    )
    tick_cmds.extend([
        "",
        f"# Animation phase",
        f"execute if score #playing {SB} matches 1 "
        f"run scoreboard players add #tick {SB} 1",
        f"execute as @e[tag={TAG}] at @s "
        f"if score #playing {SB} matches 1 "
        f"if score #tick {SB} matches {tick_delay}.. "
        f"run function {pack_name}:advance",
    ])
    with open(f"{func_dir}/tick.mcfunction", "w") as f:
        f.write("\n".join(tick_cmds) + "\n")

    # ========================================
    # finish_setup.mcfunction - called at marker position
    # ========================================
    finish_cmds = [
        f"# Build complete",
        f"scoreboard players set #build {SB} -1",
        f"clone ~0 ~0 ~{STORAGE_Z} ~{size - 1} ~{size - 1} ~{STORAGE_Z} ~0 ~0 ~0 replace",
        f"scoreboard players set #playing {SB} 1",
        f'tellraw @a [{{"text":"{pack_name} animation started! ({n_frames} frames)","color":"green"}}]',
        f'tellraw @a [{{"text":"Stop: /function {pack_name}:stop","color":"yellow"}}]',
        f'tellraw @a [{{"text":"Remove: /function {pack_name}:remove","color":"gray"}}]',
    ]
    with open(f"{func_dir}/finish_setup.mcfunction", "w") as f:
        f.write("\n".join(finish_cmds) + "\n")

    # ========================================
    # advance.mcfunction - frame transition (runs at marker position)
    # ========================================
    advance_cmds = [
        f"scoreboard players set #tick {SB} 0",
        f"scoreboard players add #frame {SB} 1",
        f"execute if score #frame {SB} matches {n_frames}.. "
        f"run scoreboard players set #frame {SB} 0",
    ]
    for i in range(n_frames):
        fz = STORAGE_Z + i
        advance_cmds.append(
            f"execute if score #frame {SB} matches {i} "
            f"run clone ~0 ~0 ~{fz} ~{size - 1} ~{size - 1} ~{fz} ~0 ~0 ~0 replace"
        )
    with open(f"{func_dir}/advance.mcfunction", "w") as f:
        f.write("\n".join(advance_cmds) + "\n")

    # ========================================
    # start / stop / remove
    # ========================================
    with open(f"{func_dir}/start.mcfunction", "w") as f:
        f.write(f"scoreboard players set #playing {SB} 1\n")
        f.write(f'tellraw @a [{{"text":"Animation started","color":"green"}}]\n')

    with open(f"{func_dir}/stop.mcfunction", "w") as f:
        f.write(f"scoreboard players set #playing {SB} 0\n")
        f.write(f"scoreboard players set #tick {SB} 0\n")
        f.write(f'tellraw @a [{{"text":"Animation stopped","color":"yellow"}}]\n')

    remove_cmds = [
        f"scoreboard players set #playing {SB} 0",
        f"scoreboard players set #build {SB} -1",
        f"execute as @e[tag={TAG}] at @s run fill ~0 ~0 ~0 ~{size - 1} ~{size - 1} ~0 air",
    ]
    for i in range(n_frames):
        fz = STORAGE_Z + i
        remove_cmds.append(
            f"execute as @e[tag={TAG}] at @s run fill ~0 ~0 ~{fz} ~{size - 1} ~{size - 1} ~{fz} air"
        )
    remove_cmds.extend([
        f"execute as @e[tag={TAG}] at @s run forceload remove ~0 ~{STORAGE_Z} ~{size - 1} ~{STORAGE_Z + n_frames - 1}",
        f"kill @e[tag={TAG}]",
        f"scoreboard objectives remove {SB}",
        f'tellraw @a [{{"text":"{pack_name} animation removed","color":"red"}}]',
    ])
    with open(f"{func_dir}/remove.mcfunction", "w") as f:
        f.write("\n".join(remove_cmds) + "\n")

    # サマリー
    total_blocks = sum(len(f) for f in frames)
    print(f"\n✅ データパック生成完了: {pack_dir}")
    print(f"   フレーム数: {n_frames}")
    print(f"   表示サイズ: {size}x{size}")
    print(f"   総ブロック数: {total_blocks:,}")
    print(f"   ティック遅延: {tick_delay} ({tick_delay * 50}ms/フレーム)")
    print(f"   方式: tick.json + marker entity (コマンドブロック不使用)")
    print(f"\n📋 使い方:")
    print(f"   1. Minecraft で /reload")
    print(f"   2. 広い平地で /function {pack_name}:place")
    print(f"   3. 構築完了後、自動でアニメーション開始！")
    print(f"   4. 停止: /function {pack_name}:stop")
    print(f"   5. 再開: /function {pack_name}:start")
    print(f"   6. 撤去: /function {pack_name}:remove")

    return pack_dir


def deploy(pack_name):
    """データパックをMinecraftにデプロイ"""
    if not pack_name.endswith("_datapack"):
        pack_name = f"{pack_name}_datapack"

    src = f"{PROJECT_DIR}/{pack_name}"
    dst = f"{DATAPACKS_DIR}/{pack_name}"

    if not os.path.exists(src):
        print(f"❌ データパックが見つかりません: {src}")
        sys.exit(1)

    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f"\n🚀 デプロイ完了: {dst}")
    print(f"   Minecraft で /reload を実行してください")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    gif_path = sys.argv[1]
    pack_name = sys.argv[2] if len(sys.argv) > 2 else "hula"
    size = int(sys.argv[3]) if len(sys.argv) > 3 else 128
    tick_delay = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    dither = "--no-dither" not in sys.argv

    pack_dir = create_gif_animation(gif_path, pack_name, size, tick_delay, dither=dither)
    deploy(pack_name)
