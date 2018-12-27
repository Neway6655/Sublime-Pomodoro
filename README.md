Pomodoro-Sublime-Plugin
=========================

This is a sublime plugin which implements functions like pomodoro.

Usage: 
-----------------------------
Add the line below to your **"Preferences: Key Bindings - User"** settings:  
{ "keys": ["ctrl+shift+alt+p"], "command": "pomodoro" },   
{ "keys": ["ctrl+shift+9"], "command": "pomodoro_pause" }

In **"Preferences: Package Settings - Pomodoro - Settings-Default"** are some arguments you can configure(all configurations have default values). We recommend you copy these values and paste in **"Preferences: Package Settings - Pomodoro - Settings-User"**

* workingMins: configure your working time in minutes. 
* restingMins: configure your rest time in minutes.
* longBreakWorkingCount: configure the number of working sessions before a long break.
* longBreakMins: configure the long break time in minutes.
* autoStart: configure whether pomodoro should be auto started or not once sublime was launched.

You can stop pomodoro by pressing the binding key(e.g. "ctrl+shift+alt+p") again, and resume it by pressing it again one more time.:smiley:

You can pause/unpause pomodoro by pressing "ctrl+shift+9".

Preview:
-----------------------------
*working progress*:

![](https://raw.githubusercontent.com/Neway6655/Sublime-Pomodoro/master/images/pomodoro_working_status_sample.jpg)

*taking a break*:

![](https://raw.githubusercontent.com/Neway6655/Sublime-Pomodoro/master/images/pomodoro_rest_status_sample.jpg)

*pause*:
![](https://raw.githubusercontent.com/Neway6655/Sublime-Pomodoro/master/images/pomodoro_pause_status_sample.png)