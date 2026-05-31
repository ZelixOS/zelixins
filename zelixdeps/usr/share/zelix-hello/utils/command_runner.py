from PyQt6.QtCore import QThread, pyqtSignal
import subprocess

class CommandRunner(QThread):
    output_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int)

    def __init__(self, command, use_pkexec=False):
        super().__init__()
        if use_pkexec:
            self.command = ["pkexec"] + (command if isinstance(command, list) else command.split())
        else:
            self.command = command if isinstance(command, list) else command.split()

    def run(self):
        try:
            # We use Popen to read output incrementally
            process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.output_signal.emit(output.strip())
            
            # Check for remaining stderr
            err = process.stderr.read()
            if err:
                self.error_signal.emit(err.strip())
                
            rc = process.poll()
            self.finished_signal.emit(rc)
            
        except Exception as e:
            self.error_signal.emit(str(e))
            self.finished_signal.emit(-1)
