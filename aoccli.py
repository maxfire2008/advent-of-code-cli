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
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

os.environ['REQUESTS_CA_BUNDLE'] = resource_path("content/cacert.pem")

@click.group()
def main():
    """
    Simple CLI for Advent of Code
    """
    pass

@main.command()
@click.argument('init', nargs=-1)
@click.option('--year', '-y', required=True)
@click.option('--day', '-d', required=True)
def init(init, year, day):
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
        with open(resource_path("content\\solution.py"),"rb") as original:
            with open("solution.py","wb+") as new:
                new.write(original.read())
        click.echo("solution.py created")
    if not os.path.exists("problem_io.py"):
        with open(resource_path("content\\problem_io.py"),"rb") as original:
            with open("problem_io.py","wb+") as new:
                new.write(original.read())
        click.echo("problem_io.py created")
    if not os.path.exists("sample.txt"):
        with open("sample.txt","wb+") as new:
            pass
        click.echo("sample.txt created")
    with open(".advent-of-code-cli","rb") as config_file_stream:
        config_file = json.loads(config_file_stream.read().decode())
    session_cookie = click.prompt("Session Cookie")
    resp = requests.get("https://adventofcode.com/"+config_file["year"]+"/day/"+config_file["day"]+"/input", headers={"cookie": "session="+session_cookie})
    if resp.status_code == 200:
        with open("input.txt","wb+") as new:
            new.write(resp.content)
        click.echo("input.txt downloaded")
##            click.echo(resp.content.decode())
    else:
        click.echo(resp.status_code)
        click.echo(resp.content.decode())

@main.command()
@click.argument('refetch', nargs=-1)
def refetch(refetch):
    """Refetch input."""
    if os.path.exists(".advent-of-code-cli"):
        with open(".advent-of-code-cli","rb") as config_file_stream:
            config_file = json.loads(config_file_stream.read().decode())
        session_cookie = click.prompt("Session Cookie")
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
##        cwd=problem_file_path
    )
    try:
        code_output = result.stdout.decode()
    except:
        code_output = ''
    try:
        code_output += result.stderr.decode()
    except:
        pass

    code_answer = None
    for line in code_output.split("\n"):
        if line.startswith("__AOC_CI_SYSTEM_OUTPUT_CALL:"):
            try:
                code_answer = base64.b64decode(line[28:].encode()).decode()
            except Exception as e:
##                print(e)
                code_answer = None
    code_answer_part_2 = None
    for line in code_output.split("\n"):
        if line.startswith("__AOC_CI_SYSTEM_OUTPUT_CALL_2:"):
            try:
                code_answer_part_2 = base64.b64decode(line[30:].encode()).decode()
            except Exception as e:
##                print(e)
                code_answer_part_2 = None
    if verbose:
        click.echo(code_output)
    if code_answer:
        click.echo("==PART 1 ANSWER==")
        click.echo(code_answer)
    if code_answer_part_2:
        click.echo("==PART 2 ANSWER==")
        click.echo(code_answer_part_2)
    if not (code_answer or code_answer_part_2):
        click.echo("Code produced no valid output calls! Try with --verbose")

if __name__ == "__main__":
    main()
