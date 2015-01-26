import sublime
import sublime_plugin
import threading
import functools
import time

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
    def __init__(self, view, workingMins, restingMins):
        super(TimeRecorder, self).__init__()
        self.view = view
        self.workingMins = workingMins
        self.restingMins = restingMins
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

    def run(self):
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

            rest = sublime.ok_cancel_dialog('Hey, you are working too hard, take a rest.', 'OK')
            if rest:
                self.recording(self.restingMins, updateRestingTimeStatus)
                if self.stopped():
                    stopRecording()
                    time.sleep(2)
                    continue
                work = sublime.ok_cancel_dialog("Come on, let's continue.", 'OK')
                if not work:
                    stop()
            time.sleep(2)

    def stop(self):
        self.stopFlag.set()

    def stopped(self):
        return self.stopFlag.isSet()

    def resume(self):
        self.stopFlag.clear()
        

class PomodoroCommand(sublime_plugin.TextCommand):

    def run(self, edit, workingMins, restingMins):
        global timeRecorder_thread
        if timeRecorder_thread is None: 
            timeRecorder_thread = TimeRecorder(self.view, workingMins, restingMins)
            timeRecorder_thread.start()
        elif timeRecorder_thread.stopped():
            timeRecorder_thread.resume()
        else:
            timeRecorder_thread.stop()