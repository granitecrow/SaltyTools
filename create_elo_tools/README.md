# Create Database

The generate.py script is used to build a functioning ELO database from historical match data. It's imperfect but it makes use of the only data available.


## What does it do

1. Downloads the latest database from https://salty.imaprettykitty.com
2. Removes unecessary tables
3. Alters the rankings table to add ELO at a starting value of 1000 (where K = 30)
4. Iterates through the fights table to simulate each fight historically
* There are imperfections with this approach as the existing database looks to track historical PvP win-loss
* For our purposes, we are going to pretend its the historical report of each fight in chronological time-series order
* Limitations are the order is not correct and we disregard multiple victories replacing with just one; but seeing how there isn't a historical archive, we must make do


## Usage

1. make sure you've already cloned and installed dependencies from the repo
2. run generate.py
```
$ python generate.py
```
4. Let it run overnight
5. Copy it to your root directory for use with the saltybet tools

---

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](http://opensource.org/licenses/mit-license.php)**