# generator.py – Generiert CS2-kompatiblen CFG-Output
import re
from .model import BindProfile, SimpleBind, ToggleBind, HoldBind, CfgBind


def _alias(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)


def _q(s: str) -> str:
    """Fuegt Anführungszeichen hinzu wenn nötig."""
    return s if ' ' not in s else f'"{s}"'


# ── Simple ────────────────────────────────────────────────────────────────────

def generate_simple(b: SimpleBind) -> str:
    if not b.key or not b.command:
        return ""
    lines = []
    if b.description:
        lines.append(f"// {b.description}")
    lines.append(f'bind "{b.key}" "{b.command}"')
    return "\n".join(lines)


# ── Toggle ────────────────────────────────────────────────────────────────────

def generate_toggle(b: ToggleBind) -> str:
    if not b.key or not b.alias_name:
        return ""
    n = _alias(b.alias_name)
    a = b.state_a_cmds.strip()
    bv = b.state_b_cmds.strip()
    lines = []
    if b.description:
        lines.append(f"// {b.description}")
    lines.append(f'alias "{n}_a" "{a}; alias {n} {n}_b"')
    lines.append(f'alias "{n}_b" "{bv}; alias {n} {n}_a"')
    lines.append(f'alias "{n}" "{n}_a"')
    lines.append(f'bind "{b.key}" "{n}"')
    return "\n".join(lines)


# ── Hold ──────────────────────────────────────────────────────────────────────

def generate_hold(b: HoldBind) -> str:
    if not b.key or not b.alias_name:
        return ""
    n = _alias(b.alias_name)
    press   = b.press_cmds.strip()
    release = b.release_cmds.strip()
    before  = b.before_cmds.strip()
    lines = []
    if b.description:
        lines.append(f"// {b.description}")
    if before:
        # Default-State beim Start ausfuehren
        lines.append(f"// Default State (before):")
        for cmd in before.splitlines():
            cmd = cmd.strip()
            if cmd:
                lines.append(cmd)
    lines.append(f'alias "+{n}" "{press}"')
    lines.append(f'alias "-{n}" "{release}"')
    lines.append(f'bind "{b.key}" "+{n}"')
    return "\n".join(lines)


# ── CFG Exec ──────────────────────────────────────────────────────────────────

def generate_cfg(b: CfgBind) -> str:
    if not b.key:
        return ""
    lines = []
    if b.description:
        lines.append(f"// {b.description}")

    t = b.exec_type
    if t == "simple":
        if not b.cfg_file:
            return ""
        cfg = b.cfg_file if b.cfg_file.endswith('.cfg') else b.cfg_file + '.cfg'
        lines.append(f'bind "{b.key}" "exec {cfg}"')

    elif t == "hold":
        cp = (b.cfg_press   if b.cfg_press.endswith('.cfg')   else b.cfg_press   + '.cfg') if b.cfg_press   else ''
        cr = (b.cfg_release if b.cfg_release.endswith('.cfg') else b.cfg_release + '.cfg') if b.cfg_release else ''
        if not cp and not cr:
            return ""
        n = _alias(f"cfg_hold_{b.key}")
        if cp:
            lines.append(f'alias "+{n}" "exec {cp}"')
        if cr:
            lines.append(f'alias "-{n}" "exec {cr}"')
        lines.append(f'bind "{b.key}" "+{n}"')

    elif t == "toggle":
        ca = (b.cfg_file_a if b.cfg_file_a.endswith('.cfg') else b.cfg_file_a + '.cfg') if b.cfg_file_a else ''
        cb = (b.cfg_file_b if b.cfg_file_b.endswith('.cfg') else b.cfg_file_b + '.cfg') if b.cfg_file_b else ''
        if not ca and not cb:
            return ""
        n = _alias(f"cfg_tog_{b.key}")
        if ca:
            lines.append(f'alias "{n}_a" "exec {ca}; alias {n} {n}_b"')
        if cb:
            lines.append(f'alias "{n}_b" "exec {cb}; alias {n} {n}_a"')
        lines.append(f'alias "{n}" "{n}_a"')
        lines.append(f'bind "{b.key}" "{n}"')

    return "\n".join(lines)


# ── Profil ────────────────────────────────────────────────────────────────────

def generate_profile(profile: BindProfile) -> str:
    sections = []

    if profile.simple_binds:
        blocks = [b for b in (generate_simple(x) for x in profile.simple_binds) if b]
        if blocks:
            sections.append("// ─── Simple Binds ───\n" + "\n".join(blocks))

    if profile.toggle_binds:
        blocks = [b for b in (generate_toggle(x) for x in profile.toggle_binds) if b]
        if blocks:
            sections.append("// ─── Toggle Binds ───\n" + "\n\n".join(blocks))

    if profile.hold_binds:
        blocks = [b for b in (generate_hold(x) for x in profile.hold_binds) if b]
        if blocks:
            sections.append("// ─── Hold Binds ───\n" + "\n\n".join(blocks))

    if profile.cfg_binds:
        blocks = [b for b in (generate_cfg(x) for x in profile.cfg_binds) if b]
        if blocks:
            sections.append("// ─── CFG Exec Binds ───\n" + "\n\n".join(blocks))

    header = f"// Bind Manager – {profile.name}\n// Generiert vom vsvito's CounterStrike2 CFG Configurator\n\n"
    return header + "\n\n".join(sections)
