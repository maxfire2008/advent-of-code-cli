import requests
import click
import subprocess
import os
import base64
import json
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception as e:
        base_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(base_path, relative_path)

os.environ['REQUESTS_CA_BUNDLE'] = resource_path("content/cacert.pem")

@click.group()
def main():
    """
    Simple CLI for Advent of Code v2.0.1
    """
    pass

@main.command()
@click.argument('init', nargs=-1)
@click.option('--year', '-y', required=True)
@click.option('--day', '-d', required=True)
@click.option('--session_cookie', '-s')
def init(init, year, day, session_cookie):
    """Initilise day of Advent of Code"""
##    click.echo(year+day)
    if not os.path.exists(".advent-of-code-cli"):
        manifest_data = {
            "year": year,
            "day": day
            }
        with open(".advent-of-code-cli","w+") as _advent_of_code_cli:
            _advent_of_code_cli.write(json.dumps(manifest_data))
        click.echo(".advent-of-code-cli created")
##    click.echo(resource_path("content/solution.py"))
    if not os.path.exists("solution.py"):
        with open(resource_path("content/solution.py"),"rb") as original:
            with open("solution.py","wb+") as new:
                new.write(original.read())
        click.echo("solution.py created")
    if not os.path.exists("problem_io.py"):
        with open(resource_path("content/problem_io.py"),"rb") as original:
            with open("problem_io.py","wb+") as new:
                new.write(original.read())
        click.echo("problem_io.py created")
    if not os.path.exists("sample.txt"):
        with open("sample.txt","w+") as new:
            pass
        click.echo("sample.txt created")
    with open(".advent-of-code-cli","rb") as config_file_stream:
        config_file = json.loads(config_file_stream.read().decode())
    if session_cookie:
        resp = requests.get("https://adventofcode.com/"+config_file["year"]+"/day/"+config_file["day"]+"/input", headers={"cookie": "session="+session_cookie})
        if resp.status_code == 200:
            with open("input.txt","wb+") as new:
                new.write(resp.content)
            click.echo("input.txt downloaded")
        else:
            click.echo(resp.status_code)
            click.echo(resp.content.decode())
    else:
        click.echo("Input not collected as session cookie was not provided. Use aoccli refetch to get the input.")

@main.command()
@click.argument('refetch', nargs=-1)
@click.option('--session_cookie', '-s', required=True)
def refetch(refetch,session_cookie):
    """Refetch input."""
    if os.path.exists(".advent-of-code-cli"):
        with open(".advent-of-code-cli","rb") as config_file_stream:
            config_file = json.loads(config_file_stream.read().decode())
##        session_cookie = click.prompt("Session Cookie")
        resp = requests.get("https://adventofcode.com/"+config_file["year"]+"/day/"+config_file["day"]+"/input", headers={"cookie": "session="+session_cookie})
        if resp.status_code == 200:
            with open("input.txt","wb+") as new:
                new.write(resp.content)
            click.echo("input.txt downloaded")
##            click.echo(resp.content.decode())
        else:
            click.echo(resp.status_code)
            click.echo(resp.content.decode())
    else:
        click.echo("Please initilise this folder first!")

@main.command()
@click.argument('run', nargs=-1)
@click.option('--verbose', '-v', is_flag=True)
@click.option('--sample', '-s', is_flag=True)
##@click.option('--language', '-l', default="py {path} {b64filename}", show_default=True, help="Avalible options:\n{path}: path of file\n{b64filename}: base64 encoded name of file")
##@click.option('--language_custom', '-c', default="py {path} {b64filename}", show_default=True, help="Avalible options:\n{path}: path of file\n{b64filename}: base64 encoded name of file")
def run(run, verbose, sample):
    """Run program"""
    if sample:
        input_file = "sample.txt"
    else:
        input_file = "input.txt"
    try:
        r = open(input_file,"rb").read().decode()
        if r == "" and input_file == "sample.txt":
            click.echo("Put the sample text in sample.txt then try again!")
            return
        elif r == "" and input_file == "input.txt":
            click.echo("input.txt is empty! Try refetching.")
            return
    except FileNotFoundError:
        if input_file == "sample.txt":
            click.echo("Couldn't find sample.txt. Try initilising this folder.")
            return
        else:
            click.echo("Couldn't find input.txt. Try initilising this folder.")
            return
    try:
        result = subprocess.run(
            [
                'py',
                os.path.join(
                    "solution.py"
                ),
                base64.b64encode(input_file.encode()).decode()
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            )
    except FileNotFoundError:
        result = subprocess.run(
            [
                'python3',
                os.path.join(
                    "solution.py"
                ),
                base64.b64encode(input_file.encode()).decode()
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            )
##        language_custom.replace(
##            "{path}",
##            os.path.join("solution.py"),
##            ).replace(
##            "{b64filename}",
##            base64.b64encode(input_file.encode()).decode(),
##            ),
##            ),
##        cwd=problem_file_path
    try:
        code_output = result.stdout.decode()
    except:
        code_output = ''
    try:
        code_output += result.stderr.decode()
    except:
        pass

    code_answers = {}
    for line in code_output.split("\n"):
        if line.startswith("__AOC_CLI_SYSTEM_OUTPUT_CALL:"):
            try:
                code_answer = json.loads(base64.b64decode(line[28:].encode()).decode())
                code_answers[code_answer["part"]] = code_answer["output"]
            except Exception as e:
                pass
    if verbose:
        click.echo(code_output)
    at_least_one = False
    for ans in code_answers:
        at_least_one = True
        click.echo("==PART "+str(ans)+" ANSWER==")
        click.echo(code_answers[ans])
    if not at_least_one and not verbose:
        click.echo("Code produced no valid output calls! Try with --verbose")

if __name__ == "__main__":
    main()
