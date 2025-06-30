import re


def get_kernel_version(command):
    stdout = command.run_check("uname -r")
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", stdout.pop().strip())
    return tuple(map(int, match.groups())) if match else None


def check_kernel_bootlog(log_lines):
    splat_patterns = [
        r'unhandled signal \d+',         # Unhandled signals
        r'kernel BUG at',                # Kernel BUG
        r'Oops:',                        # Kernel Oops
        r'panic:',                       # Kernel panic
        r'WARNING:',                     # Warnings
        r'BUG:',                         # Other bugs
        r'general protection fault',     # GPF
        r'Call Trace:',                  # Usually part of stack traces
    ]

    combined_pattern = re.compile('|'.join(splat_patterns), re.IGNORECASE)
    splat_lines = [line for line in log_lines if combined_pattern.search(line)]
    return splat_lines
