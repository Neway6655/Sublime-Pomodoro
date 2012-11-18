import sublime
import sublime_plugin
from threading import Thread
import functools
import time


def drawProgressbar(totalSize, currPos, charStartBar, charEndBar, charBackground, charPos):
    s = charStartBar
    for c in range(1, currPos - 1):
        s = s + charBackground
    s = s + charPos
    for c in range(currPos, totalSize):
        s = s + charBackground
    s = s + charEndBar
    return s


def updateWorkingTimeStatus(totMins, leftMins):
    sublime.status_message('Working time remaining: ' + str(leftMins) + 'mins ' + drawProgressbar(totMins, totMins - leftMins + 1, '[', ']', '-', 'O'))


def updateRestingTimeStatus(totMins, leftMins):
    sublime.status_message('Resting time remaining: ' + str(leftMins) + 'mins ' + drawProgressbar(totMins, totMins - leftMins + 1, '[', ']', '-', 'O'))


class TimeRecorder(Thread):
    def __init__(self, view, workingMins, restingMins):
        self.view = view
        self.workingMins = workingMins
        self.restingMins = restingMins
        Thread.__init__(self)

    def recording(self, runningMins, displayCallback):
        leftMins = runningMins
        while leftMins > 0:
            for i in range(1, 12):
                sublime.set_timeout(functools.partial(displayCallback, runningMins, leftMins), 10)
                time.sleep(5)
            leftMins = leftMins - 1

    def run(self):
        while 1:
            self.recording(self.workingMins, updateWorkingTimeStatus)
            rest = sublime.ok_cancel_dialog('Hey, you are working too hard, take a rest.', 'OK')
            if rest:
                self.recording(self.restingMins, updateRestingTimeStatus)
                work = sublime.ok_cancel_dialog("Come on, let's continue.", 'OK')
                if not work:
                    break
            else:
                break
        self.stop()

    def stop(self):
        if self.isAlive():
            self._Thread__stop()


class PomodoroCommand(sublime_plugin.TextCommand):
    _timeRecorder_thread = None

    def run(self, edit, workingMins, restingMins):
        if (self._timeRecorder_thread is not None):
            self._timeRecorder_thread.stop()

        self._timeRecorder_thread = TimeRecorder(self.view, workingMins, restingMins)
        self._timeRecorder_thread.start()

    def is_enabled(self):
        if self._timeRecorder_thread is None or not self._timeRecorder_thread.isAlive():
            return True
        else:
            return False
