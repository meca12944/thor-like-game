"""Felt exterior asset list (PixelLab map-objects, high top-down). size = canvas px; the composer trims transparent margins."""
STYLE = ('dark fantasy slum on the outskirts of a burned royal capital, soot-stained, poor and patched, muted browns and greys, '
         'late afternoon light, 16-bit JRPG pixel art, no text, no letters')
B = 'building, front door facing the viewer (south), '
ASSETS = [
 # id, size (w,h), description
 ('bld_weapon',  (128, 128), B + 'small used-weapon shop of soot-stained stone and old timber, sagging dark slate roof, hanging sign with a crossed swords icon, rack of rusty swords and shields beside the door'),
 ('bld_tool',    (128, 128), B + 'small general goods shop, patched wooden walls, faded striped cloth awning over the door, hanging sign with a potion bottle icon, sacks and crates out front'),
 ('bld_smith',   (160, 144), B + 'stone blacksmith forge with a tall smoking chimney, open front with glowing furnace and anvil, heap of scavenged scrap metal'),
 ('bld_chief',   (160, 160), B + 'larger two-story half-timbered house of the village elder, patched roof with missing tiles, blank wooden plaque over the door, old royal banner scrap on the wall'),
 ('bld_herb',    (112, 112), B + 'small herbalist hut, thatched roof, bundles of drying herbs hanging under the eaves, clay pots and a bench'),
 ('bld_guard',   (96, 160), B + 'wooden guard watchtower on a stone base with a small guard hut at its foot, lantern, spears leaning on the wall'),
 ('bld_inn',     (160, 160), B + 'two-story timber inn and tavern with a small balcony, warm lit windows, hanging tankard sign, barrels by the door'),
 ('bld_chapel',  (160, 176), B + 'old ruined stone chapel with a square bell tower, part of the roof collapsed, candle light inside the arched door'),
 ('bld_atelier', (160, 144), B + 'ruined royal tailor workshop of carved pale stone with a broken gilded arch, colorful cloth draped over the cracked walls, a dress mannequin by the door'),
 ('bld_atelier2', (160, 144), B + 'whole small workshop building with cracked pale carved stone walls and a roof partly collapsed and patched with colorful cloth drapes, broken gilded arch over the front door, dress mannequin and fabric bolts beside the door'),
 ('bld_stall',   (112, 96), 'merchant wooden cart stall with a red tiled canopy, goods and bottles on display, a wooden wheel'),
 ('bld_shack1',  (96, 96), B + 'poor ramshackle plank shack with a patched sagging roof and a crooked chimney'),
 ('bld_shack2',  (96, 96), B + 'tiny refugee hovel built from scavenged boards and stones, cloth roof patch'),
 ('bld_burned',  (128, 112), 'burned-out ruined stone house, roofless, charred black beams, rubble inside'),
 ('ruin_wall1',  (256, 128), 'long section of a burned crumbling royal city wall with a broken tower, blackened stone, weeds'),
 ('ruin_wall2',  (256, 128), 'long section of a burned crumbling royal city wall with a collapsed gate arch, blackened stone, rubble'),
 ('fountain',    (80, 64),   'cracked old round stone fountain still trickling water, mossy basin'),
 ('web_ruin',    (112, 112), 'ruined stone archway completely covered in thick grey spider webs, dark opening, broken fence'),
 ('p_crates',    (48, 48),   'stack of old wooden crates'),
 ('p_cart',      (64, 64),   'broken wooden hand cart'),
 ('p_lamp',      (32, 64),   'old iron street lamp post with a dim lantern'),
 ('p_deadtree',  (64, 96),   'dead leafless gnarled tree, charred bark'),
 ('p_fence',     (96, 32),   'broken wooden fence segment, horizontal'),
 ('p_rubble',    (64, 48),   'pile of broken stone rubble and charred wood'),
 ('p_web',       (48, 48),   'thick grey spider web in a corner'),
 ('p_pillar',    (48, 64),   'broken stone pillar stump'),
 ('p_board',     (48, 64),   'wooden notice board with torn paper notes, no text'),
 ('p_sacks',     (48, 48),   'pile of grain sacks'),
 ('p_brazier',   (32, 48),   'iron fire brazier with a small flame'),
 ('p_bench',     (64, 32),   'old wooden bench'),
]
