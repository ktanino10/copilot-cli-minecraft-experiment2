# octcatmove GIF Animation - Setup (19 frames, 128x128)

kill @e[tag=octcatmove_origin]
summon marker ~ ~ ~
tag @e[type=marker,sort=nearest,limit=1,distance=..1] add octcatmove_origin

scoreboard objectives add octcatmove_anim dummy
scoreboard players set #tick octcatmove_anim 0
scoreboard players set #frame octcatmove_anim 0
scoreboard players set #build octcatmove_anim 0
scoreboard players set #playing octcatmove_anim 0

forceload add ~0 ~300 ~127 ~318
fill ~0 ~0 ~0 ~127 ~127 ~0 air

tellraw @a [{"text":"Building octcatmove: 19 frames...","color":"yellow"}]
