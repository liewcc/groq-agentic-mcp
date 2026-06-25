"""
Groq Shell Module

This module provides tools for executing local shell commands, reading files, and writing files.

Shell engine: cmd.exe (shell=True) for correct stdout inheritance on Windows.
PowerShell cmdlets can be invoked with: powershell -NoProfile -Command "Get-ChildItem ..."
"""

import os
import subprocess
import locale

# Common Windows tool paths injected into subprocess PATH so bare commands work
_EXTRA_PATHS = [
    r"C:\Program Files\Git\cmd",
    r"C:\Program Files\GitHub CLI",
    r"C:\Windows\System32",
    r"C:\Users\cclie\AppData\Local\Programs\Python\Python314",
]

def _make_env() -> dict:
    env = os.environ.copy()
    existing = env.get("PATH", "")
    additions = ";".join(p for p in _EXTRA_PATHS if os.path.isdir(p))
    if additions:
        env["PATH"] = additions + ";" + existing
    # Prevent git from blocking on credential/SSH prompts in a non-TTY subprocess
    env.setdefault("GIT_TERMINAL_PROMPT", "0")
    env.setdefault("GIT_ASKPASS", "echo")
    return env

def decode_bytes(data: bytes) -> str:
    """Decode raw bytes into a string with fallbacks."""
    if not data:
        return ""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        pass
    preferred = locale.getpreferredencoding()
    try:
        return data.decode(preferred)
    except UnicodeDecodeError:
        pass
    try:
        return data.decode("gbk")
    except UnicodeDecodeError:
        pass
    return data.decode("utf-8", errors="replace")

def run_shell_command(command: str, working_dir: str | None = None, timeout: int = 30) -> str:
    """执行本地 shell 命令，返回 stdout/stderr 合并结果。

    Uses cmd.exe (shell=True) so native executables (git, gh, python, etc.) have
    their stdout properly captured. For PowerShell cmdlets, prefix with:
      powershell -NoProfile -Command \"Get-ChildItem ...\"
    """
    try:
        actual_cwd = None
        if working_dir:
            actual_cwd = os.path.abspath(os.path.expanduser(working_dir))
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            stdin=subprocess.DEVNULL,  # prevent MSYS2/ConPTY handle inheritance hang
            env=_make_env(),
            cwd=actual_cwd,
            timeout=timeout
        )
        stdout = decode_bytes(result.stdout)
        stderr = decode_bytes(result.stderr)
        if result.returncode == 0:
            return stdout if stdout else stderr
        else:
            return f"exit {result.returncode}\n{stderr}"
    except subprocess.TimeoutExpired as e:
        stdout = decode_bytes(e.stdout) if e.stdout else ""
        stderr = decode_bytes(e.stderr) if e.stderr else ""
        return f"exit -1\nCommand timed out after {timeout} seconds.\nStdout: {stdout}\nStderr: {stderr}"
    except Exception as e:
        return f"exit -1\nError running command: {str(e)}"

def read_file(path: str) -> str:
    """读取本地文件内容，返回字符串。"""
    try:
        full_path = os.path.abspath(os.path.expanduser(path))
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {path}: {str(e)}"

def write_file(path: str, content: str) -> str:
    """写入本地文件，返回成功/失败消息。"""
    try:
        full_path = os.path.abspath(os.path.expanduser(path))
        parent_dir = os.path.dirname(full_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing to file {path}: {str(e)}"
