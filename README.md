Pomodoro-Sublime-Plugin
=========================

This is a sublime plugin which implements functions like pomodoro.

Usage: 
-----------------------------
Add the line below to your **"Preferences: Key Bindings - User"** settings:  
{ "keys": ["ctrl+shift+alt+p"], "command": "pomodoro", "args": {"workingMins": 25, "restingMins": 5, "longBreakWorkingCount": 4, "longBreakMins": 15, "autoStart": false} }

Here are some arguments you can configure(all configurations have default values)

* workingMins: configure your working time in minutes. 
* restingMins: configure your rest time in minutes.
* longBreakWorkingCount: configure the number of working sessions before a long break.
* longBreakMins: configure the long break time in minutes.
* autoStart: configure whether pomodoro should be auto started or not once sublime was launched.

You can stop pomodoro by pressing the binding key(e.g. "ctrl+shift+alt+p") again, and resume it by pressing it again one more time.:smiley:

Preview:
-----------------------------
*working progress*:

![](https://raw.githubusercontent.com/Neway6655/Sublime-Pomodoro/master/images/pomodoro_working_status_sample.jpg)

*taking a break*:

![](https://raw.githubusercontent.com/Neway6655/Sublime-Pomodoro/master/images/pomodoro_rest_status_sample.jpg)
