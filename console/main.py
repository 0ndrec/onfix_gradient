
import os
import sys
import inquirer
from inquirer.themes import GreenPassion
from art import text2art
from colorama import Fore
from loader import config
from rich.console import Console as RichConsole
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text
sys.path.append(os.path.realpath('.'))

class Console:
    MODULES = ('Register', 'Farm', 'Export statistics', 'Exit')
    MODULES_DATA = {'Register': 'register', 'Farm': 'farm', 'Exit': 'exit', 'Export statistics': 'export_statistics'}

    def __init__(self):
        self.rich_console = RichConsole()

    def show_dev_info(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        title = text2art('JamBit', font='small')
        styled_title = Text(title, style='bold cyan')
        version = Text('VERSION: 1.5', style='blue')
        dev_panel = Panel(Text.assemble(styled_title, '\n', version), border_style='yellow', expand=False, title='[bold green]Welcome[/bold green]', subtitle='[italic]Powered by Jammer[/italic]')
        self.rich_console.print(dev_panel)
        print()

    @staticmethod
    def prompt(data: list):
        answers = inquirer.prompt(data, theme=GreenPassion())
        return answers

    def get_module(self):
        questions = [inquirer.List('module', message=Fore.LIGHTBLACK_EX + 'Select the module', choices=self.MODULES)]
        answers = self.prompt(questions)
        return answers.get('module')

    def display_info(self):
        table = Table(title='Gradient Configuration', box=box.ROUNDED)
        table.add_column('Parameter', style='cyan')
        table.add_column('Value', style='magenta')
        table.add_row('Accounts to register', str(len(config.accounts_to_register)))
        table.add_row('Accounts to farm', str(len(config.accounts_to_farm)))
        table.add_row('Threads', str(config.threads))
        table.add_row('Delay before start', f'{config.delay_before_start.min} - {config.delay_before_start.max} sec')
        panel = Panel(table, expand=False, border_style='green', title='[bold yellow]System Information[/bold yellow]', subtitle='[italic]Use arrow keys to navigate[/italic]')
        self.rich_console.print(panel)

    def build(self) -> None:
        self.show_dev_info()
        self.display_info()
        module = self.get_module()
        config.module = self.MODULES_DATA[module]