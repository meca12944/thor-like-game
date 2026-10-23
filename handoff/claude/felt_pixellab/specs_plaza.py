"""Felt plaza vignette (one screen, 24x14 tiles): richer parts. (id, size, description, seeds, extra map-object params)"""
STYLE = ('dark fantasy slum plaza beside a burned royal capital, soot-stained and patched, muted browns and greys with warm lantern light, '
         'late afternoon, highly detailed 16-bit JRPG pixel art, no text, no letters')
HD = {'detail': 'high detail', 'shading': 'detailed shading'}
FLAT = {'detail': 'medium detail', 'shading': 'basic shading', 'outline': 'lineless'}
TWO, ONE = [301, 402], [301]
ASSETS = [
 ('pz_fountain', (160, 128), 'large old round stone fountain on a raised circular dais with three worn steps, cracked basin with trickling water, weathered statue of a crowned king with a broken arm in the middle, moss and scattered coins', TWO, HD),
 ('pz_statue',   (112, 112), 'fallen statue of a royal knight lying broken across a cracked stone pedestal, rubble around it', TWO, HD),
 ('pz_stall_a',  (128, 112), 'market stall with a patched brown cloth awning on crooked poles, baskets of shriveled vegetables, hanging dried fish and garlic', TWO, HD),
 ('pz_stall_b',  (128, 112), 'market stall with a faded red-striped awning, shelves of clay pottery and candles, a small lantern', TWO, HD),
 ('pz_tent',     (128, 112), 'refugee lean-to tent of patched canvas and wooden poles, bedroll and cooking pots inside, small campfire with a hanging kettle in front', TWO, HD),
 ('pz_house_a',  (176, 160), 'building, front door facing the viewer: tall narrow half-timbered townhouse with an overhanging upper floor, soot-stained plaster, crooked shutters, hanging lantern by the door', TWO, HD),
 ('pz_house_b',  (176, 160), 'building, front door facing the viewer: stone and timber row house with a broken wooden balcony, laundry line with grey rags, patched slate roof', TWO, HD),
 ('pz_house_c',  (176, 160), 'building, front door facing the viewer: tailor shop in a fire-scarred stone house, boarded upper window, hanging sign with a needle and thread icon, bolts of cloth by the door', TWO, HD),
 ('pz_lamp',     (32, 80),   'ornate old iron street lamp post with a lit lantern glowing warm orange', ONE, HD),
 ('pz_lanterns', (192, 48),  'sagging rope strung horizontally with small glowing paper lanterns and tattered cloth pennants, seen from above at an angle', ONE, HD),
 ('pz_crates',   (96, 80),   'pile of wooden crates, barrels and grain sacks stacked against each other', ONE, HD),
 ('pz_well',     (80, 88),   'small stone well with a wooden roof, rope and bucket', ONE, HD),
 ('pz_board',    (64, 80),   'wooden notice board covered with many torn paper notices and a wanted poster with a face drawing, no text', ONE, HD),
 ('pz_bench',    (64, 40),   'worn wooden bench with a cracked plank', ONE, HD),
 ('pz_cart',     (96, 64),   'wooden cart with one broken wheel, loaded with sacks and a tarp', ONE, HD),
 ('pz_deadtree', (96, 128),  'dead twisted tree with tattered cloth strips tied to its bare branches, roots breaking the cobblestones', ONE, HD),
 ('pz_crows',    (48, 32),   'three black crows standing on the ground', ONE, HD),
 ('pz_webs',     (96, 96),   'thick grey spider webs stretched between two broken wooden posts and rubble', ONE, HD),
 ('pz_rubble',   (80, 48),   'pile of broken masonry blocks and charred beams', ONE, HD),
 ('pz_pots',     (48, 40),   'cluster of clay pots and jars', ONE, HD),
 ('pz_brazier',  (40, 56),   'iron brazier with a burning fire', ONE, HD),
 ('pz_planter',  (48, 40),   'cracked stone planter with withered flowers', ONE, HD),
 ('dc_puddle',   (64, 32),   'flat ground decal: dark shallow rain puddle reflecting the sky between cobblestones, top-down', ONE, FLAT),
 ('dc_cracks',   (64, 48),   'flat ground decal: patch of broken cracked cobblestones with weeds growing in the gaps, top-down', ONE, FLAT),
 ('dc_ash',      (64, 48),   'flat ground decal: scattered black ash and soot stains on the ground, top-down', ONE, FLAT),
 ('dc_moss',     (48, 32),   'flat ground decal: green moss and small weeds between stones, top-down', ONE, FLAT),
 ('dc_leaves',   (48, 32),   'flat ground decal: scattered dead brown leaves and torn paper scraps, top-down', ONE, FLAT),
]
