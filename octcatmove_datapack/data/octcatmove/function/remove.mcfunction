scoreboard players set #playing octcatmove_anim 0
scoreboard players set #build octcatmove_anim -1
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~0 ~127 ~127 ~0 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~300 ~127 ~127 ~300 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~301 ~127 ~127 ~301 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~302 ~127 ~127 ~302 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~303 ~127 ~127 ~303 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~304 ~127 ~127 ~304 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~305 ~127 ~127 ~305 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~306 ~127 ~127 ~306 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~307 ~127 ~127 ~307 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~308 ~127 ~127 ~308 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~309 ~127 ~127 ~309 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~310 ~127 ~127 ~310 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~311 ~127 ~127 ~311 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~312 ~127 ~127 ~312 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~313 ~127 ~127 ~313 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~314 ~127 ~127 ~314 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~315 ~127 ~127 ~315 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~316 ~127 ~127 ~316 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~317 ~127 ~127 ~317 air
execute as @e[tag=octcatmove_origin] at @s run fill ~0 ~0 ~318 ~127 ~127 ~318 air
execute as @e[tag=octcatmove_origin] at @s run forceload remove ~0 ~300 ~127 ~318
kill @e[tag=octcatmove_origin]
scoreboard objectives remove octcatmove_anim
tellraw @a [{"text":"octcatmove animation removed","color":"red"}]
