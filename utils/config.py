emojis_conversor = {
  '<:pokeball:899807489334333460>': 'pokeball',
  '<:greatball:888645319313727529>': 'greatball',
  '<:ultraball:887870688390680597>': 'ultraball',
  '<:masterball:887870688139018290>': 'masterball'
}

all_emojis = {
  'pokeball': '<:pokeball:899807489334333460>',
  'greatball': '<:greatball:888645319313727529>',
  'ultraball': '<:ultraball:887870688390680597>',
  'masterball': '<:masterball:887870688139018290>',
  'cb': '<:cb:898244478672965702>',
  'ub': '<:ub:898244478928838719>',
  'rb': '<:rb:898244479243415642>',
  'mb': '<:mb:897597753746673674>'
}

emojis_pokeball = {
  'pokeball': '<:pokeball:899807489334333460>',
  'greatball': '<:greatball:888645319313727529>',
  'ultraball': '<:ultraball:887870688390680597>',
  'masterball': '<:masterball:887870688139018290>',
}

badges_order = ['Developer', 'Collaborator', 'Betatester']

badges = {
  'developer': '<:developer:894069601078493255>',
  'collaborator': '<:collaborator:894069601183346708>',
  'betatester': '<:betatester:894069600763916339>'
}

pokemon_rarity = ['exclusive', 'ultra-beast', 'legendary', 'mythical', 'rare', 'uncommon', 'common']

pokemon_rarity_prices = {
  'exclusive': 0,
  'ultra-beast': 4000,
  'legendary': 1000,
  'mythical': 450,
  'rare': 100,
  'uncommon': 50,
  'common': 25
}

pokemon_rarity_ordem = {k:v for v,k in enumerate(['common', 'uncommon', 'rare', 'mythical', 'legendary', 'ultra-beast', 'exclusive'])}

emojis_rarity = {
  'exclusive': '🪐',
  'ultra-beast': '💫',
  'legendary': '🌟',
  'mythical': '✨',
  'rare': '⭐',
  'uncommon': '🏵',
  'common': '🔰'
}

chances_pokeball = {
  'pokeball': {'ultra-beast': 1, 'legendary': 2, 'mythical': 3, 'rare': 10, 'uncommon': 30, 'common': 40},
  'greatball': {'ultra-beast': 7, 'legendary': 9, 'mythical': 15, 'rare': 40, 'uncommon': 65, 'common': 75},
  'ultraball': {'ultra-beast': 12, 'legendary': 15, 'mythical': 20, 'rare': 60, 'uncommon': 80, 'common': 90}
}

items_ordem = ['Pokeball', 'Greatball', 'Ultraball', 'Masterball', 'Cb', 'Ub', 'Rb', 'Mb']

all_items = {
  'Pokeball',
  'Greatball',
  'Ultraball',
  'Masterball',
  'Cb',
  'Ub',
  'Rb',
  'Mb'
}

box_ids = {'Cb': 1,'Ub': 2,'Rb': 3,'Mb': 4}

box_images = {
  'Cb': 'https://media.discordapp.net/attachments/887158781832749086/898244244203003984/cb.png',
  'Ub': 'https://media.discordapp.net/attachments/887158781832749086/898244245322879076/ub.png',
  'Rb': 'https://media.discordapp.net/attachments/887158781832749086/898244246925111306/rb.png',
  'Mb': 'https://media.discordapp.net/attachments/887158781832749086/897596534626074724/mb.png'
}

price_itens = {
  'Pokeball': 10,
  'Greatball': 50,
  'Ultraball': 100
}

classes = {
  0: ['Treinador novato', 1800.0, 1000, 3],
  1: ['Treinador novato II', 1710.0, 2000, 3],
  2: ['Treinador novato III', 1620.0, 3000, 3],
  3: ['Treinador', 1530.0, 4000, 4],
  4: ['Treinador II', 1440.0, 5000, 4],
  5: ['Treinador III', 1350.0, 6000, 4],
  6: ['Treinador de Elite', 1260.0, 7000, 5],
  7: ['Treinador de Elite II', 1170.0, 8000, 5],
  8: ['Treinador de Elite III', 1080.0, 9000, 5],
  9: ['Professor Pokémon', 990.0, 10000, 6],
  10: ['Professor Pokémon II', 900.0, 11000, 6],
  11: ['Professor Pokémon III', 810.0, 12000, 6],
  12: ['Mestre Pokémon', 720.0, 0, 8]
}