import subprocess
from exchange import Messenger, SystemCmdEvents, CommonEvents

messenger = Messenger("localhost")


def handle_event(event):
    try:
        if event.is_an(SystemCmdEvents.EventTurnMopidyOn):
            subprocess.call(['nohup mopidy &'], shell=True)
        elif event.is_an(SystemCmdEvents.EventTurnMopidyOff):
            subprocess.call(['pkill mopidy'], shell=True)
        elif event.is_an(SystemCmdEvents.EventTurnTvOn):
            subprocess.call(['echo on 0 | cec-client -s -d 1'], shell=True)
        elif event.is_an(SystemCmdEvents.EventTurnTvOff):
            subprocess.call(['echo standby 0 | cec-client -s -d 1'], shell=True)
        elif event.is_an(SystemCmdEvents.EventForceTvSource):
            subprocess.call(['echo as | cec-client -s -d 1'], shell=True)
        return CommonEvents.EventSuccess()
    except:
        return CommonEvents.EventFailure()


if __name__ == "__main__":
    messenger.subscribe_backend("systemcmd", handle_event)
    print("registered!")

    messenger.wait_for_messages(False)
