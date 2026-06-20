# generator.py – Generiert CS2-kompatiblen CFG-Output
from .model import BindProfile, SimpleBind, ToggleBind, HoldBind, CfgBind


def _sanitize_alias(name: str) -> str:
    """Alias-Namen: nur alphanumerisch + Unterstrich."""
    import re
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)


def generate_simple(b: SimpleBind) -> str:
    if not b.key or not b.command:
        return ""
    line = f'bind "{b.key}" "{b.command}"'
    if b.description:
        line = f"// {b.description}\n" + line
    return line


def generate_toggle(b: ToggleBind) -> str:
    if not b.key or not b.alias_name:
        return ""
    name = _sanitize_alias(b.alias_name)
    state_a = b.state_a_cmds.strip().replace('"', '\\"')
    state_b = b.state_b_cmds.strip().replace('"', '\\"')
    lines = []
    if b.description:
        lines.append(f"// {b.description}")
    lines.append(f'alias "{name}_a" "{state_a}; alias {name} {name}_b"')
    lines.append(f'alias "{name}_b" "{state_b}; alias {name} {name}_a"')
    lines.append(f'alias "{name}" "{name}_a"')
    lines.append(f'bind "{b.key}" "{name}"')
    return "\n".join(lines)


def generate_hold(b: HoldBind) -> str:
    if not b.key or not b.alias_name:
        return ""
    name = _sanitize_alias(b.alias_name)
    press   = b.press_cmds.strip().replace('"', '\\"')
    release = b.release_cmds.strip().replace('"', '\\"')
    lines = []
    if b.description:
        lines.append(f"// {b.description}")
    lines.append(f'alias "+{name}" "{press}"')
    lines.append(f'alias "-{name}" "{release}"')
    lines.append(f'bind "{b.key}" "+{name}"')
    return "\n".join(lines)


def generate_cfg(b: CfgBind) -> str:
    if not b.key or not b.cfg_file:
        return ""
    cfg = b.cfg_file.strip()
    if not cfg.endswith(".cfg"):
        cfg += ".cfg"
    line = f'bind "{b.key}" "exec {cfg}"'
    if b.description:
        line = f"// {b.description}\n" + line
    return line


def generate_profile(profile: BindProfile) -> str:
    sections = []

    if profile.simple_binds:
        blocks = [generate_simple(b) for b in profile.simple_binds]
        blocks = [b for b in blocks if b]
        if blocks:
            sections.append("// ── Simple Binds ──\n" + "\n".join(blocks))

    if profile.toggle_binds:
        blocks = [generate_toggle(b) for b in profile.toggle_binds]
        blocks = [b for b in blocks if b]
        if blocks:
            sections.append("// ── Toggle Binds ──\n" + "\n\n".join(blocks))

    if profile.hold_binds:
        blocks = [generate_hold(b) for b in profile.hold_binds]
        blocks = [b for b in blocks if b]
        if blocks:
            sections.append("// ── Hold Binds ──\n" + "\n\n".join(blocks))

    if profile.cfg_binds:
        blocks = [generate_cfg(b) for b in profile.cfg_binds]
        blocks = [b for b in blocks if b]
        if blocks:
            sections.append("// ── CFG Exec Binds ──\n" + "\n".join(blocks))

    header = f"// Bind Manager – {profile.name}\n// Generiert vom CS2 CFG Configurator\n"
    return header + "\n\n".join(sections)
