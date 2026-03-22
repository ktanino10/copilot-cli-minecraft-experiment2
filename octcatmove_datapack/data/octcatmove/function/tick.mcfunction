# Build phase: one frame per tick
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 0 run function octcatmove:frame_0
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 1 run function octcatmove:frame_1
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 2 run function octcatmove:frame_2
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 3 run function octcatmove:frame_3
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 4 run function octcatmove:frame_4
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 5 run function octcatmove:frame_5
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 6 run function octcatmove:frame_6
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 7 run function octcatmove:frame_7
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 8 run function octcatmove:frame_8
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 9 run function octcatmove:frame_9
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 10 run function octcatmove:frame_10
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 11 run function octcatmove:frame_11
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 12 run function octcatmove:frame_12
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 13 run function octcatmove:frame_13
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 14 run function octcatmove:frame_14
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 15 run function octcatmove:frame_15
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 16 run function octcatmove:frame_16
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 17 run function octcatmove:frame_17
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 18 run function octcatmove:frame_18
execute as @e[tag=octcatmove_origin] at @s if score #build octcatmove_anim matches 19 run function octcatmove:finish_setup
execute if score #build octcatmove_anim matches 0..18 run scoreboard players add #build octcatmove_anim 1

# Animation phase
execute if score #playing octcatmove_anim matches 1 run scoreboard players add #tick octcatmove_anim 1
execute as @e[tag=octcatmove_origin] at @s if score #playing octcatmove_anim matches 1 if score #tick octcatmove_anim matches 3.. run function octcatmove:advance
