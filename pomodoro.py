import sublime
import sublime_plugin
import threading
import functools
import time

ST_VERSION = 3000 if sublime.version() == '' else int(sublime.version())

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


def updateWorkingTimeStatus(kwargs):
    leftMins = kwargs.get('leftMins')
    totMins = kwargs.get('runningMins')
    current_pomodoro = kwargs.get('current_pomodoro')
    total_pomodoros = kwargs.get('total_pomodoros')
    sublime.status_message(
        'Working time remaining: ' + str(leftMins) + 'mins | pomodoro: ' +
        str(current_pomodoro + 1) + '/' + str(total_pomodoros) + ' ' +
        drawProgressbar(totMins, totMins - leftMins + 1, '[', ']', '-', 'O')
    )


def updateRestingTimeStatus(kwargs):
    leftMins = kwargs.get('leftMins')
    totMins = kwargs.get('runningMins')
    current_pomodoro = kwargs.get('current_pomodoro')
    total_pomodoros = kwargs.get('total_pomodoros')
    if current_pomodoro == 0:
        current_pomodoro = total_pomodoros

    sublime.status_message(
        'Resting time remaining: ' + str(leftMins) + 'mins ' + '| break: ' +
        str(current_pomodoro) + '/' + str(total_pomodoros) + ' ' +
        drawProgressbar(totMins, totMins - leftMins + 1, '[', ']', '-', 'O')
    )


def stopRecording():
    sublime.status_message('')


def pauseRecording():
    sublime.status_message('Pomodoro Paused ||')
    time.sleep(1)
    sublime.status_message('')
    time.sleep(1)


class TimeRecorder(threading.Thread):
    def __init__(self, view, workingMins, restingMins, longBreakWorkingCount, longBreakMins):
        super(TimeRecorder, self).__init__()
        self.view = view
        self.workingMins = workingMins
        self.restingMins = restingMins
        self.longBreakWorkingCount = longBreakWorkingCount
        self.longBreakMins = longBreakMins
        self.stopFlag = threading.Event()
        self.workingSessionCount = 0
        self.is_paused = False

    def recording(self, runningMins, displayCallback):
        leftMins = runningMins
        while leftMins > 1:

            for i in range(1, 60):
                while self.is_paused:
                    pauseRecording()
                if self.stopped():
                    stopRecording()
                    break
                kwargs = {
                    'runningMins': runningMins,
                    'leftMins': leftMins,
                    'current_pomodoro': self.workingSessionCount,
                    'total_pomodoros': self.longBreakWorkingCount
                }
                sublime.set_timeout(functools.partial(displayCallback, kwargs), 10)
                time.sleep(1)
            leftMins = leftMins - 1

        if leftMins == 1:
            for i in range(1, 12):
                while self.is_paused:
                    pauseRecording()
                if self.stopped():
                    stopRecording()
                    break
                kwargs = {
                    'runningMins': runningMins,
                    'leftMins': leftMins,
                    'current_pomodoro': self.workingSessionCount,
                    'total_pomodoros': self.longBreakWorkingCount
                }
                sublime.set_timeout(functools.partial(displayCallback, kwargs), 10)
                time.sleep(5)
            leftMins = leftMins - 1

    def longBreak(self, workingSessionCount):
        return workingSessionCount >= self.longBreakWorkingCount

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

            if Notify.is_ready():
                sublime.run_command("sub_notify", {"title": "", "msg": "Hey, you are working too hard, take a rest."})
                rest = True
            else:
                rest = sublime.ok_cancel_dialog('Hey, you are working too hard, take a rest.', 'OK')
            # increase work session count
            self.workingSessionCount += 1

            if rest:
                restingMins = self.restingMins
                if self.longBreak(self.workingSessionCount):
                    restingMins = self.longBreakMins
                    self.workingSessionCount = 0
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

    def pause(self):
        self.is_paused = not self.is_paused


class PomodoroCommand(sublime_plugin.TextCommand):

    def run(self, edit, **kwargs):
        global timeRecorder_thread
        autoStart, workingMins, restingMins, longBreakWorkingCount, longBreakMins = load_settings()
        if timeRecorder_thread is None:
            timeRecorder_thread = TimeRecorder(
                self.view, workingMins, restingMins, longBreakWorkingCount, longBreakMins
            )
            timeRecorder_thread.start()
        elif timeRecorder_thread.stopped():
            timeRecorder_thread.resume()
        else:
            timeRecorder_thread.stop()


class PomodoroPauseCommand(sublime_plugin.TextCommand):

    def run(self, edit, **kwargs):
        if timeRecorder_thread:
            timeRecorder_thread.pause()


def load_settings():
    s = sublime.load_settings("Pomodoro.sublime-settings")
    autoStart = s.get("autoStart", False)
    workingMins = s.get("workingMins", 25)
    restingMins = s.get("restingMins", 5)
    longBreakWorkingCount = s.get("longBreakWorkingCount", 4)
    longBreakMins = s.get("longBreakMins", 15)
    return autoStart, workingMins, restingMins, longBreakWorkingCount, longBreakMins


def plugin_loaded():
    autoStart, workingMins, restingMins, longBreakWorkingCount, longBreakMins = load_settings()
    if autoStart:
        sublime.active_window().run_command(
            'pomodoro',
        )


if ST_VERSION < 3000:
    autoStart, workingMins, restingMins, longBreakWorkingCount, longBreakMins = load_settings()
    if autoStart:
        sublime.active_window().run_command(
            'pomodoro',
            {
                'workingMins': workingMins,
                "restingMins": restingMins,
                "longBreakWorkingCount": longBreakWorkingCount,
                "longBreakMins": longBreakMins
            }
        )
