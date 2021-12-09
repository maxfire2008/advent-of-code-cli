import sys
import base64
import json

class IO:
    def __init__(self):
        self._input = None
        self._raw_input = None
    def _get_raw_input(self):
        if self._raw_input:
            return self._raw_input
        else:
            input_stuff = json.loads(
                base64.b64decode(sys.argv[1].encode()).decode())
            self._raw_input = input_stuff
            return self._raw_input
    @property
    def input(self):
        if self._input:
            return self._input
        else:
            input_stuff = self._get_raw_input()
            file_name = input_stuff["f"]
            with open(file_name,"rb") as file:
                file_content = file.read().decode().replace("\r\n","\n")
            if file_content.endswith("\n"):
                self._input=file_content[:-1]
            else:
                self._input=file_content
            return self._input
    def output(self,output,part=1):
        print('__AOC_CLI_SYSTEM_OUTPUT_CALL:'+base64.b64encode(
        json.dumps(
        {"output":str(output),
        "part": str(part)}
        ).encode()).decode())
        if self._get_raw_input()["n"] == True:
            print("==== PART",part,"ANSWER ====")
            print(str(output))
            print("="*(22+len(str(part))))
io = IO()
