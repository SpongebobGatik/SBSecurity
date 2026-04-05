#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mcpi.minecraft import Minecraft
from mcpi import block
import sys
import mcpi_fast_query as mcq
import picraft
from picraft import Vector

block_alphabet = {
    'A': block.WOOD.id, 'B': block.STONE.id,
    'C': block.BRICK_BLOCK.id, 'D': block.DIAMOND_BLOCK.id,
    'E': block.COBBLESTONE.id, 'F': block.SAND.id,
    'G': block.GRAVEL.id, 'H': block.GOLD_ORE.id,
    'I': block.IRON_ORE.id, 'J': block.COAL_ORE.id,
    'K': block.STAIRS_STONE_BRICK.id, 'L': block.LAPIS_LAZULI_ORE.id,
    'M': block.LAPIS_LAZULI_BLOCK.id, 'N': block.COBWEB.id,
    'O': block.STONE_SLAB_DOUBLE.id, 'P': block.FURNACE_INACTIVE.id,
    'Q': block.FENCE_ACACIA.id, 'R': block.STAIRS_COBBLESTONE.id,
    'S': block.REDSTONE_ORE.id, 'T': block.SNOW_BLOCK.id,
    'U': block.STAINED_GLASS.id, 'V': block.FENCE_GATE.id,
    'W': block.FENCE_NETHER_BRICK.id, 'X': block.GLOWING_OBSIDIAN.id,
    'Y': (block.WOOL.id, 9), 'Z': (block.WOOL.id, 10),
    'a': block.WOOD.id, 'b': block.STONE.id,
    'c': block.BRICK_BLOCK.id, 'd': block.DIAMOND_BLOCK.id,
    'e': block.COBBLESTONE.id, 'f': block.SAND.id,
    'g': block.GRAVEL.id, 'h': block.GOLD_ORE.id,
    'i': block.IRON_ORE.id, 'j': block.COAL_ORE.id,
    'k': block.STAIRS_STONE_BRICK.id, 'l': block.LAPIS_LAZULI_ORE.id,
    'm': block.LAPIS_LAZULI_BLOCK.id, 'n': block.COBWEB.id,
    'o': block.STONE_SLAB_DOUBLE.id, 'p': block.FURNACE_INACTIVE.id,
    'q': block.FENCE_ACACIA.id, 'r': block.STAIRS_COBBLESTONE.id,
    's': block.REDSTONE_ORE.id, 't': block.SNOW_BLOCK.id,
    'u': block.STAINED_GLASS.id, 'v': block.FENCE_GATE.id,
    'w': block.FENCE_NETHER_BRICK.id, 'x': block.GLOWING_OBSIDIAN.id,
    'y': (block.WOOL.id, 9), 'z': (block.WOOL.id, 10),
    'А': block.GOLD_BLOCK.id, 'Б': block.IRON_BLOCK.id,
    'В': (block.WOOL.id, 1),
    'Г': block.GRASS.id, 'Д': (block.WOOL.id, 11),
    'Е': block.EMERALD_ORE.id, 'Ё': block.END_STONE.id,
    'Ж': block.WOOD_PLANKS.id, 'З': block.OBSIDIAN.id,
    'И': block.STAIRS_SANDSTONE.id, 'Й': block.CLAY.id,
    'К': block.BOOKSHELF.id, 'Л': (block.WOOL.id, 3),
    'М': block.MOSS_STONE.id, 'Н': block.NETHERRACK.id,
    'О': (block.WOOL.id, 6), 'П': block.PUMPKIN.id,
    'Р': (block.WOOL.id, 8), 'С': block.SANDSTONE.id,
    'Т': block.FENCE_DARK_OAK.id, 'У': block.W2.id,
    'Ф': (block.WOOL.id, 12), 'Х': block.DIAMOND_ORE.id,
    'Ц': (block.WOOL.id, 7), 'Ч': block.GLASS_PANE.id,
    'Ш': block.FENCE_BIRCH.id, 'Щ': block.STONE_BRICK.id,
    'Ъ': (block.WOOL.id, 4), 'Ы': block.WOODEN_SLAB.id,
    'Ь': block.TRAPDOOR.id, 'Э': (block.WOOL.id, 5),
    'Ю': block.SNOW.id, 'Я': block.GLOWSTONE_BLOCK.id,
    'а': block.GOLD_BLOCK.id, 'б': block.IRON_BLOCK.id,
    'в': (block.WOOL.id, 1),
    'г': block.GRASS.id, 'д': (block.WOOL.id, 11),
    'е': block.EMERALD_ORE.id, 'ё': block.END_STONE.id,
    'ж': (block.WOOL.id, 2), 'з': block.OBSIDIAN.id,
    'и': block.STAIRS_SANDSTONE.id, 'й': block.CLAY.id,
    'к': block.BOOKSHELF.id, 'л': (block.WOOL.id, 3),
    'м': block.MOSS_STONE.id, 'н': block.NETHERRACK.id,
    'о': (block.WOOL.id, 6), 'п': block.PUMPKIN.id,
    'р': (block.WOOL.id, 8), 'с': block.SANDSTONE.id,
    'т': block.FENCE_DARK_OAK.id, 'у': block.W2.id,
    'ф':(block.WOOL.id, 12), 'х': block.DIAMOND_ORE.id,
    'ц': (block.WOOL.id, 7), 'ч': block.GLASS_PANE.id,
    'ш': block.FENCE_BIRCH.id, 'щ': block.STONE_BRICK.id,
    'ъ': (block.WOOL.id, 4), 'ы': block.WOODEN_SLAB.id,
    'ь': block.TRAPDOOR.id, 'э': (block.WOOL.id, 5),
    'ю': block.SNOW.id, 'я': block.GLOWSTONE_BLOCK.id,
    '0': block.WH1.id, '1': block.WH2.id,
    '2': block.WH3.id, '3': block.WH4.id,
    '4': block.WH5.id, '5': block.WH6.id,
    '6': block.WH7.id, '7': block.WH8.id,
    '8': block.WH9.id, '9': block.WH0.id,
    '~': block.Q1.id, '!': block.Q17.id,
    '#': block.Q2.id, '@': block.Q18.id,
    '$': (block.WOOL.id, 13), '%': block.Q6.id,
    '^': block.Q4.id, '&': block.Q20.id,
    '*': block.Q5.id, '(': block.Q21.id,
    ')': block.FENCE_SPRUCE.id, '=': block.Q22.id,
    '_': block.Q7.id, '-': block.Q23.id,
    '+': block.Q8.id, '{': block.Q24.id,
    '!': block.Q9.id, '}': block.Q25.id,
    '[': block.Q10.id, ']': block.Q26.id,
    '|': block.Q11.id, "\\": block.W1.id,
    "'": block.Q12.id, ':': block.Q27.id,
    '"': block.Q13.id, ';': block.Q28.id,
    '>': block.Q14.id, ',': block.Q29.id,
    '<': block.Q15.id, '.': block.Q30.id,
    '?': block.Q16.id, '/': block.Q31.id,
    '\n': block.BEDROCK.id, ' ': block.Q0.id
}

def analyze_text(text):
    lines = text.split('\n')
    longest_line_length = max(len(line) for line in lines)
    line_count = len(lines)
    return longest_line_length, line_count

def encrypt_to_blocks(text):
    longest_line_length, line_count = analyze_text(text)
    header = f'{line_count}\n{longest_line_length}\n'
    text = header + text
    blocks = []
    x_offset = 0
    z_offset = 0
    for char in text:
        if char == '\n':
            blocks.append((block_alphabet[char], x_offset, 0, z_offset))
            z_offset += 1
            x_offset = 0
        elif char in block_alphabet:
            if char.islower():
                blocks.append((block.MELON.id, x_offset, 0, z_offset))
                x_offset += 1
                blocks.append((block_alphabet[char], x_offset, 0, z_offset))
            else:
                blocks.append((block_alphabet[char], x_offset, 0, z_offset))
        else:
            blocks.append((block.AIR.id, x_offset, 0, z_offset))
        x_offset += 1
    blocks.append((block.BARRIER.id, x_offset, 0, z_offset))
    return blocks

def decrypt_blocks_to_text(blocks):
    text = ''
    is_next_char_lowercase = False
    for block_id, x_offset, y_offset, z_offset in blocks:
        if block_id == block.BEDROCK.id:
            text += '\n'
            is_next_char_lowercase = False
        else:
            for char, id in block_alphabet.items():
                if isinstance(id, tuple) and id[0] == block_id:
                    if is_next_char_lowercase:
                        text += char.lower()
                        is_next_char_lowercase = False
                    else:
                        text += char.upper()
                    break
                elif id == block_id:
                    if is_next_char_lowercase:
                        text += char.lower()
                        is_next_char_lowercase = False
                    else:
                        text += char.upper()
                    break
            else:
                if block_id == block.MELON.id:
                    is_next_char_lowercase = True
                else:
                    text += ' '
    return text

def decrypt_from_blocks(mc, start_pos, root):
    blocksheader = []
    z_offset = 0
    x_offset = 0
    count = 0
    countvalue = 0
    while count != 2:
        block_id = mc.getBlock(start_pos.x + x_offset, start_pos.y, start_pos.z + z_offset)
        blocksheader.append((block_id, x_offset, 0, z_offset))
        if (block_id == block.AIR.id and x_offset == 0 and z_offset == 0) or (block_id == block.AIR.id and x_offset == 1 and z_offset > 0):
            return "Not root0"
        x_offset += 1
        if countvalue > 6 or not(block_id == block.AIR.id or block_id == block.BEDROCK.id or block_id == block.WH1.id or block_id == block.WH2.id or block_id == block.WH3.id or block_id == block.WH4.id or block_id == block.WH5.id or block_id == block.WH6.id or block_id == block.WH7.id or block_id == block.WH8.id or block_id == block.WH9.id or block_id == block.WH0.id): 
            return f"Not root4 {countvalue} {block_id}"
        if block_id == block.WH1.id or block_id == block.WH2.id or block_id == block.WH3.id or block_id == block.WH4.id or block_id == block.WH5.id or block_id == block.WH6.id or block_id == block.WH7.id or block_id == block.WH8.id or block_id == block.WH9.id or block_id == block.WH0.id:
            countvalue += 1
        if block_id == block.BEDROCK.id:
            z_offset += 1
            x_offset = 0
            countvalue = 0
            count += 1
    lines = [line for line in decrypt_blocks_to_text(blocksheader).split('\n') if line.strip()]
    line_count, longest_line_length = list(map(int, lines))
    if root != "0" and root != "1":
        return "Not root1"
    if root == "0" and (line_count * longest_line_length > 100000 or line_count * longest_line_length <= 0):
        return "Not root2"
    if root == "1" and (line_count * longest_line_length > 200000 or line_count * longest_line_length <= 0):
        return "Not root3"
    world = picraft.World()
    blocks = {}
    blocks2 = []
    cuboid = picraft.vector_range(
        Vector(0, 4, z_offset),
        Vector(longest_line_length*2, 5, z_offset + line_count),
        Vector(1, 1, 1),
        order = 'yxz',
    )
    for pos, blk in mcq.query_blocks(
            world.connection,
            cuboid,
            "world.getBlockWithData(%d,%d,%d)",
            lambda ans: tuple(map(int, ans.split(","))),
            thread_count=0):
        blocks[pos] = blk
    x = mcq.alt_picraft_getblock_vrange(world, cuboid)
    h = mcq.alt_picraft_getheight_vrange(world, cuboid)
    i=0
    for vector in h:
        if x[i].id == 0:
            i += 1
            continue
        if x[i].id == 35:
            blocks2.append(((x[i].id, x[i].data), vector.x, vector.y, vector.z))
        else:
            blocks2.append((x[i].id, vector.x, vector.y, vector.z))
        i += 1
    return decrypt_blocks_to_text(blocks2)

def read_input(source):
    if source.endswith('.txt'):
        with open(source, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        return source

def perform_action(action, root, source):
    if action == 'encrypt':
        mc = Minecraft.create()
        mc.postToChat("SBSecurity")
        mc.player.setTilePos(0, 4, 0)
        text = read_input(source)
        encrypted_blocks = encrypt_to_blocks(text)
        start_pos = mc.player.getTilePos()
        for block_id, x_offset, y_offset, z_offset in encrypted_blocks:
            mc.setBlock(start_pos.x + x_offset, start_pos.y + y_offset, start_pos.z + z_offset, block_id)
    elif action == 'decrypt':
        mc = Minecraft.create()
        mc.postToChat("SBSecurity")
        mc.player.setTilePos(0, 4, 0)
        start_pos = mc.player.getTilePos()
        decrypted_text = decrypt_from_blocks(mc, start_pos, root)
        print(decrypted_text)
        
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Error1")
        sys.exit(1)
    
    action = sys.argv[1]
    root = sys.argv[2]
    if action == 'encrypt':
        source = sys.argv[3]
        perform_action(action, root, source)
    elif action == 'decrypt':
        perform_action(action, root, '')
    else:
        print("Error2")
        sys.exit(1)
