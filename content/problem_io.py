import sys
import base64
import json

class IO:
    def __init__(self):
        self._input = None
    @property
    def input(self):
        if self._input:
            return self._input
        else:
            file_name = base64.b64decode(sys.argv[1].encode()).decode()
            with open(file_name,"rb") as file:
                file_content = file.read().decode()
            if file_content.endswith("\n"):
                self._input=file_content[:-1]
            else:
                self._input=file_content
            return self._input
    def output(self,output,part=1):
        if "2" in str(part):
            print('__AOC_CI_SYSTEM_OUTPUT_CALL_2:'+base64.b64encode(str(output).encode()).decode())
        else:
            print('__AOC_CI_SYSTEM_OUTPUT_CALL:'+base64.b64encode(str(output).encode()).decode())
        print('__AOC_CLI_SYSTEM_OUTPUT_CALL:'+base64.b64encode(json.dumps({"output":str(output).encode(), "part": part})).decode())
io = IO()
