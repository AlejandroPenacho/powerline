import os
import datetime
from git_status import get_git_status

SEP_1 = "\uE0B0"
SEP_2 = "\uE0B2"
SEP_3 = "\u25B6"
SEP_4 = "\u25B8"

class Formatter:
    def __init__(self, fg_color=None, bg_color=None):
        default_format = "\[\033[0m\]"

        self.fg_color = fg_color
        self.bg_color = bg_color
        if fg_color == None:
            fg_format = ""
        else:
            fg_format = f"\[\033[38;2;{fg_color[0]};{fg_color[1]};{fg_color[2]}m\]"

        if bg_color == None:
            bg_format = ""
        else:
            bg_format = f"\[\033[48;2;{bg_color[0]};{bg_color[1]};{bg_color[2]}m\]"

        self.str = f"{default_format}{fg_format}{bg_format}"
    
    def as_str(self):
        return self.str

    @classmethod
    def transition(cls, format_1, format_2):
        return cls(fg_color=format_1.bg_color, bg_color=format_2.bg_color)

    @classmethod
    def default(cls):
        return cls()

class Block:
    def __init__(self, text, formatter):
        self.text = text
        self.formatter = formatter

    def as_str(self):
        return f"{self.formatter.as_str()}{self.text}{Formatter.default().as_str()}"

    def __len__(self):
        return len(self.text)

    @classmethod
    def default(cls):
        output = cls("", Formatter.default())

    @classmethod
    def transition(cls, block_1, block_2, separator):
        if block_2 is None:
            formatter_2 = Formatter.default()
        else:
            formatter_2 = block_2.formatter

        return cls(
            separator,
            Formatter.transition(
                block_1.formatter,
                formatter_2
            )
        )

class Powerline:
    def __init__(self, blocks, separator=SEP_1, left_to_right=True):
        self.blocks = blocks 
        self.separator = separator
        self.left_to_right = left_to_right

    def __len__(self):
        # Separators
        output = len(self.blocks) - 1
        for block in self.blocks:
            output += len(block)

        return output

    def as_str(self):
        output = ""
        for i in range(len(self.blocks)):
            output += self.blocks[i].as_str()
            if i != (len(self.blocks)-1):
                if self.left_to_right:
                    sep = Block.transition(self.blocks[i], self.blocks[i+1], separator=self.separator)
                else:
                    sep = Block.transition(self.blocks[i+1], self.blocks[i], separator=self.separator)

                output += sep.as_str()

        return output


cwd = os.getenv("PWD")
conda_env = os.getenv("CONDA_DEFAULT_ENV")
user = os.getenv("USER")
now = datetime.datetime.now()
time = now.strftime("%H:%M")

git_branch = "git branch --no-color"

sty_1 = Formatter(bg_color=[129, 161, 193])
sty_2 = Formatter(bg_color=[94, 129, 172])
sty_3 = Formatter(bg_color=[180, 142, 173])

all_left_blocks = []

time_block = Block(
    f" {time} ",
    sty_1
)
all_left_blocks.append(time_block)


if conda_env is not None:
    conda_block = Block(
        f" {conda_env} ",
        sty_2
    )
    all_left_blocks.append(conda_block)


user_block = Block(
    f" {user} ",
    sty_3
)
all_left_blocks.append(user_block)


cwd_block = Block(
    f" {cwd} ",
    sty_1
)
all_left_blocks.append(cwd_block)


clean_block = Block(
    f" ",
    Formatter.default()
)
all_left_blocks.append(clean_block)


all_right_blocks = [clean_block]

git_status = get_git_status()

if git_status is not None:
    remote_status = git_status["remote_delta"]
    if remote_status is None:
        remote_text = ""
    else:
        remote_text = f"({git_status['remote_delta']}) "

    git_block = Block(
        f" {git_status['branch']} {remote_text}",
        sty_2
    )
    all_right_blocks.append(git_block)



columns = int(os.getenv("COLUMNS"))

powerline = Powerline(
    all_left_blocks,
    separator=SEP_1
)

powerline_2 = Powerline(
    all_right_blocks,
    separator=SEP_2,
    left_to_right=False
)

delta_x = columns - len(powerline_2)


ps1 = powerline.as_str()
print(f"\[\033[{delta_x}C\]{powerline_2.as_str()}\[\033[{columns}D\]{powerline.as_str()}", end="")

