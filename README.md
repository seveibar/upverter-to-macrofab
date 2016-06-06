# Upverter to Macrofab

*Boards generated using this script are have worked in the past, however I cannot
guarantee that it will work for all boards out of macrofab

## Usage

1. Export your design into the upverter format, save it in this directory as
`upverter.upv`
2. Export your design into Upverter's Tempo Automation format (note [Tempo
  Automation appears not to actually support this format](https://forum.upverter.com/t/tempo-automation-not-supported/23033/7)) and
  rename it to tempo.json
3. Run `python upverter-to-macrofab.py upverter.upv tempo.json`

After running the script a component key file will be generated, you can use this
in future runs by using `python upverter-to-macrofab.py upverter.upv tempo.json keyfile.json`

## TODOs

* Remove tempo automation dependency
