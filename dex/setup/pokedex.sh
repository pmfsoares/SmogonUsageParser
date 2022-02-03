#!/bin/bash

url=https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data/pokedex.ts

curl ${url} > pokedex.js

sed -i "1s/.*/let Pokedex = {/" pokedex.js
echo "console.log(JSON.stringify(Pokedex));" >> pokedex.js
node pokedex.js > ../pokedex.json 