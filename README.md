# Script/Prompt kiddies need not apply, download, nor use, go use ChatGPT, or go capture some Pokemons ;).

## Anywho..

Salutations! This is a tool like many other OSINT tools, is used to obtain information on lets say a 'friend'.
Information such as their Occupation, Address, Phone number, Relatives (names only), A brief description and more.
With multiple ways to view this data, either as a dataframe within the terminal, or written to a file (allowed
extensions are .json, .csv, .xlsx). All from the comfort of your terminal!  

-n is required First Name Last Name will show data in a DataFrame  
-ei City State is optional (though helps narrow the search)  
-json | -csv | -xlsx are optional. Files need to be labeled properly for this to work correctly   

Example: uv run whitepages.py -n Juan Valdez -json juan.json

The example above searches for one of the greatest coffee farmer known to man and provide some contact information
(Juan Valdez is a fictional character appeared in advertisements throughout the latin americas, carribeans, etc)
and writes anyone matching the name to a juan.json file.
## ¡Disfrute de un buen café! (Enjoy a good coffee!)

## Required Dependencies: AioHttp, Pandas, OpenPyXl
## 1) Download and install uv. -> https://docs.astral.sh/uv/getting-started/installation/
## 2) The pyproject.toml file contains the required dependencies.
## 3) uv run whitepages.py -n Juan Valdez 

## usage: whitepages.py [-h] -n FIRSTNAME LASTNAME [-ei CITY STATE] [-json JSONFILE] [-csv CSVFILE] [-xlsx XLSXFILE]

# P.S. IF YOU USE THIS FOR NEFARIOUS REASONS, YOUR ASS IS HELD RESPONSIBLE, NOT MINES.

# P.P.S DON'T BE AN ASS.
