# reservation-monitor

## Instructions (mac)

### Get Python3
Open your terminal and run these commands.
```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
```
echo 'export PATH=/usr/local/bin:$PATH' >>~/.bash_profile
```
```
source ~/.bash_profile
```
```
brew install python 3
```

### Environment
```
python3 -m venv my_env
```
Now download chromedriver
[here](https://sites.google.com/a/chromium.org/chromedriver/) and put it in my_env/bin
```
source my_env/bin/activate
```

### Configuration
Modify config.py to put your phone number and phone provider in there.
You can also modify the refresh rate but it may get blocked if you refresh too fast.


### Run
The arguments for the app are a month then days you are interested in. You will get a
text message when one of the requested dates is available.

For example if you were looking for December 8th and 25th you would run:
```
python3 monitor.py December 8 25
```
