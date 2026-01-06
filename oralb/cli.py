# Copyright (C) MatrixEditor 2023
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import shlex
import traceback
import asyncio

from prompt_toolkit import PromptSession

from oralb.command import COMMAND_TYPES
from oralb.exceptions import CLIStop


class OralBCmd:
    prompt = "(oralb)> "

    def __init__(self) -> None:
        super().__init__()
        self.session = PromptSession()
        self.commands = [x() for x in COMMAND_TYPES]
        self.parsers = {}
        self.obclient = None
        self.old_completer = None
        for command in self.commands:
            parser = command.get_parser()
            self.parsers[command.name] = parser

            # set methods
            name = command.name
            setattr(self, f"help_{name}", lambda parser=parser: parser.print_help())

    def get_names(self):
        return list(dir(self))

    def get_prompt(self):
        prompt = [("(oralb)", ""), (">", "")]
        if self.obclient is not None:
            try:
                prompt.insert(1, (f"@ {self.obclient.address}", ""))
            except AttributeError:
                pass

        return self.prompt

    async def cmdloop(self):
        stop = None
        while not stop:
            line = await self.session.prompt_async(self.get_prompt())
            if not line:
                continue

            if line.count(" ") > 0:
                name, args = line.split(" ", 1)
            else:
                name, args = line, ""

            try:
                func = getattr(self, f"do_{name}")
                func(args)
            except AttributeError:
                try:
                    argv = self.parsers[name].parse_args(shlex.split(args))
                    if not hasattr(argv, "fn"):
                        self.parsers[name].parse_args(["-h"])

                    await argv.fn(self, argv)
                except KeyError:
                    self.default(line)

    def default(self, line):
        pass


async def amain():
    shell = OralBCmd()
    while True:
        try:
            await shell.cmdloop()
        except SystemExit:
            pass
        except (KeyboardInterrupt, EOFError):
            print()
        except CLIStop:
            break
        except Exception:
            traceback.print_exc()


def main():
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        pass
