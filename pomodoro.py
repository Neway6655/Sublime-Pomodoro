import sublime
import sublime_plugin
import threading
import functools
import time

try:
    from SubNotify.sub_notify import SubNotifyIsReadyCommand as Notify
except Exception:
    class Notify(object):
        """Notify fallback."""

        @classmethod
        def is_ready(cls):
            """Return false to effectively disable SubNotify."""
            return False
timeRecorder_thread = None

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

def stopRecording():
    sublime.status_message('')

class TimeRecorder(threading.Thread):
    def __init__(self, view, workingMins, restingMins, longBreakWorkingCount, longBreakMins):
        super(TimeRecorder, self).__init__()
        self.view = view
        self.workingMins = workingMins
        self.restingMins = restingMins
        self.longBreakWorkingCount = longBreakWorkingCount
        self.longBreakMins = longBreakMins
        self.stopFlag = threading.Event()

    def recording(self, runningMins, displayCallback):
        leftMins = runningMins
        while leftMins > 1:
            for i in range(1, 60):
                if self.stopped():
                    stopRecording()
                    break

                sublime.set_timeout(functools.partial(displayCallback, runningMins, leftMins), 10)
                time.sleep(1)
            leftMins = leftMins - 1

        if leftMins == 1:
            for i in range(1, 12):
                if self.stopped():
                    stopRecording()
                    break

                sublime.set_timeout(functools.partial(displayCallback, runningMins, leftMins), 10)
                time.sleep(5)
            leftMins = leftMins - 1

    def longBreak(self, workingSessionCount):
        return workingSessionCount >= self.longBreakWorkingCount

    def run(self):
        workingSessionCount = 0
        while 1:
            if self.stopped():
                stopRecording()
                time.sleep(2)
                continue

            self.recording(self.workingMins, updateWorkingTimeStatus)

            if self.stopped():
                stopRecording()
                time.sleep(2)
                continue

            if Notify.is_ready():
                sublime.run_command("sub_notify", {"title": "", "msg": "Hey, you are working too hard, take a rest."})
                rest = True
            else:
                rest = sublime.ok_cancel_dialog('Hey, you are working too hard, take a rest.', 'OK')
            # increase work session count
            workingSessionCount += 1

            if rest:
                restingMins = self.restingMins
                if self.longBreak(workingSessionCount):
                    restingMins = self.longBreakMins
                    workingSessionCount = 0
                self.recording(restingMins, updateRestingTimeStatus)
                if self.stopped():
                    stopRecording()
                    time.sleep(2)
                    continue
                if Notify.is_ready():
                    sublime.run_command("sub_notify", {"title": "", "msg": "Come on, let's continue."})
                    work = True
                else:    
                    work = sublime.ok_cancel_dialog("Come on, let's continue.", 'OK')
                if not work:
                    self.stop()
            time.sleep(2)

    def stop(self):
        self.stopFlag.set()

    def stopped(self):
        return self.stopFlag.isSet()

    def resume(self):
        self.stopFlag.clear()
        

class PomodoroCommand(sublime_plugin.TextCommand):

    def run(self, edit, workingMins, restingMins, longBreakWorkingCount, longBreakMins):
        global timeRecorder_thread
        if timeRecorder_thread is None: 
            timeRecorder_thread = TimeRecorder(self.view, workingMins, restingMins, longBreakWorkingCount, longBreakMins)
            timeRecorder_thread.start()
        elif timeRecorder_thread.stopped():
            timeRecorder_thread.resume()
        else:
            timeRecorder_thread.stop()
