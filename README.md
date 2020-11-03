# SaltyBot SaltyBet Software

This project creates a saltybot that, once logged in, will determine the most likely winner and place a 5-10% of total money as a bet. It uses ELO (https://en.wikipedia.org/wiki/Elo_rating_system) as the algorithm to determining the most likely winner - useful for fighters that have never faced each other prior.

## Features

* All output is displayed in the console
* Details are also archived into a results.json file at the root level for later analysis

## To-Do

Future major enhancements and larger projects:

* Build data analysis on results using pandas
* Build Web UI for Raspberry Pi touchscreen (using Flask?)

## Usage

1. clone the repo
2. install dependencies
```
$ pip install -r requirements.txt
```
3. run saltybet.py
'''
$ python saltybet.py
'''
4. login with your email and password for saltybet

---

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](http://opensource.org/licenses/mit-license.php)**