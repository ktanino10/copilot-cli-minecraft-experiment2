# Build complete
scoreboard players set #build octcatmove_anim -1
clone ~0 ~0 ~300 ~127 ~127 ~300 ~0 ~0 ~0 replace
scoreboard players set #playing octcatmove_anim 1
tellraw @a [{"text":"octcatmove animation started! (19 frames)","color":"green"}]
tellraw @a [{"text":"Stop: /function octcatmove:stop","color":"yellow"}]
tellraw @a [{"text":"Remove: /function octcatmove:remove","color":"gray"}]
