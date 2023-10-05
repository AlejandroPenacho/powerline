
import subprocess
import re


def get_remote_status(line):

    if "." not in line:
        return None

    if "[" in line:
        branch_status = line.split("[")[1].split(" ")[0]
        branch_status_n = int(line.split("]")[0].split(" ")[-1])
        if branch_status == "ahead":
            remote_status = f"+{branch_status_n}"
        else:
            remote_status = f"-{branch_status_n}"
    else:
        remote_status = 0

    return remote_status





def get_git_status():
    req = subprocess.run(
        ["git", "status", "--porcelain", "--branch"],
        capture_output=True
    )

    return_code = req.returncode
    std_out = req.stdout.splitlines()

    using_git = return_code == 0

    if not using_git:
        return None
    else:
        # What if no remote?
        current_branch = std_out[0][3:].decode().split(".")[0]

        remote_status = get_remote_status(std_out[0].decode())

        return {
            "branch": current_branch,
            "remote_delta": remote_status 
        }
