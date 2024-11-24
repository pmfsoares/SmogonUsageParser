
<h1  align="center">Welcome to SmogonUsageParser </h1>

<p>

<img  alt="Version"  src="https://img.shields.io/badge/version-0.5-blue.svg?cacheSeconds=2592000"  />

</p>

  

> Smogon's Pokemon Showdown usage statistics parser

## TODO

* Finish the option to load the pickles of a chosen mode, and export the corresponding JSON.
* ~Search a pokemon on a chosen mode, and print its stats.~

  

## Usage

  
To run the parser without having to download the JSON and txt with wget or another tool, just run with following command.(this option is considerably slower, on my pc takes between 15 and 20 minutes to parser the files for every mode):
```sh

python smogonParser.py -w | --web

```
If you don't mind to download the files first, you can download both the chaos JSON and moveset txt, with the following commands, they will download the files into the `stats/chaos` and `stats/moveset`(you have to replace {year} and {month} with the desired year and month:

```sh
wget -r -nc -np -nH --cut-dirs=2 -A txt -P ./stats https://www.smogon.com/stats/{year}-{month}/moveset/

wget -r -nc -np -nH --cut-dirs=2 -A json -P ./stats https://www.smogon.com/stats/{year}-{month}/chaos/

```

After you have downloaded the files, and assuming you didn't move the files, you can just run the script as:
```sh

python smogonParser.py -l | --local
```

  

## Author



👤 **Pedro Soares**

* Github: [@pmfsoares](https://github.com/pmfsoares)
* LinkedIn: [@pmfsoares](https://www.linkedin.com/in/pmfsoares/)
  

## Show your support

  

Give a ⭐️ if this project helped you!

***
_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_
