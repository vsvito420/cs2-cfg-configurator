// =============================================================
// DATA
// =============================================================
const PRIMARY = [
    ['AK-47', 'buy ak47'], ['M4A4', 'buy m4a1'], ['M4A1-S', 'buy m4a1_silencer'],
    ['AWP', 'buy awp'], ['SG 553', 'buy sg556'], ['AUG', 'buy aug'],
    ['FAMAS', 'buy famas'], ['Galil AR', 'buy galilar'], ['SSG 08', 'buy ssg08'],
    ['G3SG1', 'buy g3sg1'], ['SCAR-20', 'buy scar20'], ['M249', 'buy m249'],
    ['Negev', 'buy negev'], ['MAC-10', 'buy mac10'], ['MP9', 'buy mp9'],
    ['MP5-SD', 'buy mp5sd'], ['MP7', 'buy mp7'], ['UMP-45', 'buy ump45'],
    ['P90', 'buy p90'], ['PP-Bizon', 'buy bizon'], ['Nova', 'buy nova'],
    ['XM1014', 'buy xm1014'], ['Sawed-Off', 'buy sawedoff'], ['MAG-7', 'buy mag7'],
];
const SECONDARY = [
    ['Glock-18', 'buy glock'], ['USP-S', 'buy usp_silencer'], ['P2000', 'buy hkp2000'],
    ['P250', 'buy p250'], ['Five-SeveN', 'buy fiveseven'], ['Tec-9', 'buy tec9'],
    ['CZ75-Auto', 'buy cz75a'], ['Desert Eagle', 'buy deagle'],
    ['R8 Revolver', 'buy revolver'], ['Dual Berettas', 'buy elite'],
];
const GRENADES = [
    ['Flashbang', 'buy flashbang'], ['Smoke', 'buy smokegrenade'],
    ['Molotov (T)', 'buy molotov'], ['Incendiary (CT)', 'buy incgrenade'],
    ['HE Grenade', 'buy hegrenade'], ['Decoy', 'buy decoy'],
];
const ARMOR = [
    ['Vest + Helmet', 'buy vesthelm'], ['Vest only', 'buy vest'],
    ['Defuse Kit', 'buy defuser'], ['Zeus (Taser)', 'buy taser'],
];

const CONVARS = [
    { n: 'sensitivity', c: 'Mouse', d: '2.5', r: '0.1–10', t: 'Mouse sensitivity' },
    { n: 'zoom_sensitivity_ratio_mouse', c: 'Mouse', d: '1.0', r: '0.1–5', t: 'Scoped sensitivity ratio' },
    { n: 'm_rawinput', c: 'Mouse', d: '1', r: '0/1', t: 'Raw mouse input' },
    { n: 'm_mouseaccel1', c: 'Mouse', d: '0', r: '0–5', t: 'Mouse accel (lower)' },
    { n: 'm_mouseaccel2', c: 'Mouse', d: '0', r: '0–5', t: 'Mouse accel (upper)' },
    { n: 'fps_max', c: 'Video', d: '400', r: '0–999', t: 'Max FPS (0=unlimited)' },
    { n: 'fps_max_ui', c: 'Video', d: '60', r: '0–999', t: 'Max FPS in menus' },
    { n: 'r_dynamic', c: 'Video', d: '0', r: '0/1', t: 'Dynamic lighting' },
    { n: 'mat_queue_mode', c: 'Video', d: '-1', r: '-1/0/2', t: 'Multicore rendering' },
    { n: 'cl_showfps', c: 'HUD', d: '0', r: '0–5', t: 'Show FPS counter' },
    { n: 'net_graph', c: 'HUD', d: '0', r: '0/1', t: 'Network graph overlay' },
    { n: 'hud_scaling', c: 'HUD', d: '0.85', r: '0.5–0.95', t: 'HUD scale' },
    { n: 'cl_hud_color', c: 'HUD', d: '0', r: '0–10', t: 'HUD color preset' },
    { n: 'cl_radar_scale', c: 'Radar', d: '0.7', r: '0.25–1', t: 'Radar map scale' },
    { n: 'cl_radar_always_centered', c: 'Radar', d: '0', r: '0/1', t: 'Keep centered on radar' },
    { n: 'cl_righthand', c: 'View', d: '1', r: '0/1', t: 'Right hand (1) / Left hand (0)' },
    { n: 'viewmodel_fov', c: 'View', d: '68', r: '54–68', t: 'Viewmodel FOV' },
    { n: 'viewmodel_offset_x', c: 'View', d: '0', r: '-2–2.5', t: 'Viewmodel X offset' },
    { n: 'viewmodel_offset_y', c: 'View', d: '0', r: '-2–2', t: 'Viewmodel Y offset' },
    { n: 'viewmodel_offset_z', c: 'View', d: '-2', r: '-2–2', t: 'Viewmodel Z offset' },
    { n: 'cl_bob_lower_amt', c: 'View', d: '21', r: '5–30', t: 'Weapon bob lower amount' },
    { n: 'cl_bobamt_lat', c: 'View', d: '0.4', r: '0.1–2', t: 'Weapon lateral bob' },
    { n: 'cl_bobamt_vert', c: 'View', d: '0.25', r: '0.1–2', t: 'Weapon vertical bob' },
    { n: 'cl_bobcycle', c: 'View', d: '0.98', r: '0.1–2', t: 'Weapon bob cycle' },
    { n: 'voice_enable', c: 'Audio', d: '1', r: '0/1', t: 'Voice chat enabled' },
    { n: 'voice_scale', c: 'Audio', d: '1.0', r: '0–1', t: 'Voice volume' },
    { n: 'volume', c: 'Audio', d: '0.5', r: '0–1', t: 'Master volume' },
    { n: 'snd_musicvolume', c: 'Audio', d: '0.1', r: '0–1', t: 'Music volume' },
    { n: 'cl_mute_enemy_team', c: 'Audio', d: '0', r: '0/1', t: 'Mute enemy team voice' },
    { n: 'cl_interp_ratio', c: 'Network', d: '2', r: '0–2', t: 'Interpolation ratio' },
    { n: 'cl_interp', c: 'Network', d: '0.015625', r: '0–0.5', t: 'Interpolation time (s)' },
    { n: 'rate', c: 'Network', d: '786432', r: '1–1048576', t: 'Network data rate (bytes/s)' },
    { n: 'cl_updaterate', c: 'Network', d: '128', r: '10–128', t: 'Server update rate' },
    { n: 'cl_cmdrate', c: 'Network', d: '128', r: '10–128', t: 'Client command rate' },
    { n: 'cl_autohelp', c: 'Misc', d: '0', r: '0/1', t: 'Auto help tips' },
    { n: 'gameinstructor_enable', c: 'Misc', d: '0', r: '0/1', t: 'In-game instructor' },
    { n: 'cl_autowepswitch', c: 'Misc', d: '0', r: '0/1', t: 'Auto switch to new weapon' },
    { n: 'cl_teamid_overhead_always', c: 'Misc', d: '1', r: '0–2', t: 'Always show teammate IDs' },
];

const COMMANDS = [
    { n: 'bind', d: 'Bind a key to a command. Usage: bind KEY "command"' },
    { n: 'unbind', d: 'Remove binding from a key' },
    { n: 'unbindall', d: 'Remove all key bindings' },
    { n: 'alias', d: 'Create a command alias. Usage: alias name "commands"' },
    { n: 'exec', d: 'Execute a .cfg file. Usage: exec filename.cfg' },
    { n: 'echo', d: 'Print a message to the console' },
    { n: 'toggle', d: 'Toggle a ConVar between values. Usage: toggle convar val1 val2' },
    { n: 'incrementvar', d: 'Cycle a ConVar through a range. Usage: incrementvar cvar min max step' },
    { n: 'buy', d: 'Buy a weapon/item. Usage: buy ak47' },
    { n: 'noclip', d: 'Toggle noclip mode (practice servers)' },
    { n: 'sv_cheats', d: 'Enable/disable cheat commands (1/0)' },
    { n: 'give', d: 'Give a weapon (sv_cheats). Usage: give weapon_ak47' },
    { n: 'bot_add', d: 'Add a bot to the game' },
    { n: 'bot_kick', d: 'Remove all bots' },
    { n: 'bot_stop', d: 'Freeze all bots (1/0)' },
    { n: 'mp_restartgame', d: 'Restart the game. Usage: mp_restartgame 1' },
    { n: 'mp_warmuptime', d: 'Set warmup duration in seconds' },
    { n: 'mp_freezetime', d: 'Set freeze time at round start' },
    { n: 'mp_roundtime', d: 'Set round duration in minutes' },
    { n: 'mp_buy_anywhere', d: 'Allow buying anywhere (1/0, sv_cheats)' },
    { n: 'mp_unlimited_ammo', d: 'Unlimited ammo (1/0, sv_cheats)' },
    { n: 'cl_grenadepreview', d: 'Show grenade trajectory preview (1/0)' },
    { n: 'r_drawothermodels', d: 'See through walls (2=wireframe, sv_cheats)' },
    { n: 'sv_infinite_ammo', d: 'Infinite ammo (sv_cheats)' },
    { n: 'cl_showpos', d: 'Show position/velocity overlay (1/0)' },
    { n: 'clear', d: 'Clear the developer console' },
    { n: 'quit', d: 'Exit CS2' },
    { n: 'disconnect', d: 'Disconnect from the current server' },
    { n: 'status', d: 'Show server/player status info' },
    { n: 'net_channels', d: 'Show network channel info' },
    { n: 'voice_enable', d: 'Enable/disable voice chat (1/0)' },
    { n: 'voice_scale', d: 'Voice chat volume (0–1)' },
    { n: '+attack', d: 'Primary fire (hold)' },
    { n: '+attack2', d: 'Secondary fire (hold)' },
    { n: '+use', d: 'Use key (hold)' },
    { n: '+jump', d: 'Jump (hold)' },
    { n: '+duck', d: 'Crouch (hold)' },
    { n: '+sprint', d: 'Walk (hold)' },
    { n: '+lookatweapon', d: 'Inspect weapon (hold)' },
];

// =============================================================
// STATE
// =============================================================
let STATE = {
    buyBinds: [],   // {key, cmds[]}
    switchBinds: [], // {type, key, ...}
    settings: {},   // {cvar: val}
    cfgText: '',
    cfgFileName: 'autoexec.cfg',
};
let dirHandle = null;
let bbSelected = new Set(); // indices into weapon arrays combined

// persist
function save() { try { localStorage.setItem('cs2cfg', JSON.stringify(STATE)); } catch (e) { } }
function load() {
    try {
        const s = localStorage.getItem('cs2cfg');
        if (s) { const p = JSON.parse(s); Object.assign(STATE, p); }
    } catch (e) { }
}

// =============================================================
// INIT
// =============================================================
document.addEventListener('DOMContentLoaded', () => {
    load();
    buildWeaponGrid();
    renderBuyBinds();
    buildSettingsTable();
    buildCmdViewer();
    renderSwitchBinds();
    updateCfgEditor();
    updateDash();
    if (!('showDirectoryPicker' in window)) {
        document.getElementById('exp-api-note').className = 'alert alert-warn';
        document.getElementById('exp-api-note').innerHTML = '⚠️ File System Access API not supported in your browser. Use the Download button.';
    }
});

// =============================================================
// SIDEBAR / PANEL
// =============================================================
function sw(name, el) {
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.sb-item').forEach(s => s.classList.remove('active'));
    document.getElementById('panel-' + name).classList.add('active');
    if (el) el.classList.add('active');
    if (name === 'export') refreshExport();
    if (name === 'dashboard') updateDash();
}
function getSbItem(i) { return document.querySelectorAll('.sb-item')[i]; }

// =============================================================
// FOLDER PICKER
// =============================================================
async function pickFolder() {
    if (!('showDirectoryPicker' in window)) { alert('Not supported in this browser. Use Chrome or Edge 86+.'); return; }
    try {
        dirHandle = await window.showDirectoryPicker({ mode: 'readwrite' });
        document.getElementById('folder-name').textContent = '✅ ' + dirHandle.name;
        document.getElementById('sb-folder').textContent = '📁 ' + dirHandle.name;
        document.getElementById('exp-path').textContent = '📁 ' + dirHandle.name + '/autoexec.cfg';
        document.getElementById('exp-api-note').className = 'alert alert-ok';
        document.getElementById('exp-api-note').innerHTML = '✅ Folder selected! Click Save to write autoexec.cfg.';
    } catch (e) { if (e.name !== 'AbortError') console.error(e); }
}

// =============================================================
// BUY BINDS
// =============================================================
const ALL_WEAPONS = [
    ...PRIMARY.map((w, i) => ({ ...{ label: w[0], cmd: w[1] }, group: 'primary', id: 'p' + i })),
    ...SECONDARY.map((w, i) => ({ ...{ label: w[0], cmd: w[1] }, group: 'secondary', id: 's' + i })),
    ...GRENADES.map((w, i) => ({ ...{ label: w[0], cmd: w[1] }, group: 'grenades', id: 'g' + i })),
    ...ARMOR.map((w, i) => ({ ...{ label: w[0], cmd: w[1] }, group: 'armor', id: 'a' + i })),
];

function buildWeaponGrid() {
    const groups = { primary: 'wg-primary', secondary: 'wg-secondary', grenades: 'wg-grenades', armor: 'wg-armor' };
    ALL_WEAPONS.forEach(w => {
        const el = document.getElementById(groups[w.group]);
        const div = document.createElement('div');
        div.className = 'weapon-chip';
        div.id = 'wc-' + w.id;
        div.innerHTML = `<input type="checkbox" id="wch-${w.id}" onchange="toggleWeapon('${w.id}')" /><label for="wch-${w.id}">${esc(w.label)}</label>`;
        div.onclick = e => { if (e.target.tagName !== 'INPUT') { const cb = div.querySelector('input'); cb.checked = !cb.checked; toggleWeapon(w.id); } };
        el.appendChild(div);
    });
}

function toggleWeapon(id) {
    if (bbSelected.has(id)) bbSelected.delete(id);
    else bbSelected.add(id);
    const chip = document.getElementById('wc-' + id);
    if (chip) chip.classList.toggle('selected', bbSelected.has(id));
    updateBbPreview();
}

function clearBBSelection() {
    bbSelected.clear();
    ALL_WEAPONS.forEach(w => {
        const chip = document.getElementById('wc-' + w.id);
        if (chip) { chip.classList.remove('selected'); chip.querySelector('input').checked = false; }
    });
    updateBbPreview();
}

function getBbCmd() {
    const cmds = ALL_WEAPONS.filter(w => bbSelected.has(w.id)).map(w => w.cmd);
    return cmds.join('; ');
}

function updateBbPreview() {
    const key = (document.getElementById('bb-key').value.trim().toUpperCase() || '<KEY>');
    const cmd = getBbCmd();
    document.getElementById('bb-cmd-preview').textContent =
        cmd ? `bind "${key}" "${cmd}"` : '// Select weapons above and assign a key';
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('bb-key').addEventListener('input', updateBbPreview);
});

function addBuyBind() {
    const key = document.getElementById('bb-key').value.trim().toUpperCase();
    const cmd = getBbCmd();
    if (!key) { alert('Enter a key first.'); return; }
    if (!cmd) { alert('Select at least one weapon/item.'); return; }
    STATE.buyBinds.push({ key, cmd });
    save();
    clearBBSelection();
    document.getElementById('bb-key').value = '';
    renderBuyBinds();
    updateDash();
    showToast('Buy bind added!');
}

function renderBuyBinds() {
    const el = document.getElementById('bb-list');
    if (!STATE.buyBinds.length) { el.innerHTML = '<div style="color:var(--muted);font-style:italic;font-size:.82rem;padding:.5rem">No buy binds yet.</div>'; }
    else {
        el.innerHTML = STATE.buyBinds.map((b, i) =>
            `<div class="buy-bind-row">
        <span class="bkey">${esc(b.key)}</span>
        <span class="bcmd">bind "${esc(b.key)}" "${esc(b.cmd)}"</span>
        <button class="btn btn-danger" onclick="removeBuyBind(${i})">✕</button>
      </div>`
        ).join('');
    }
    document.getElementById('sb-bb').textContent = STATE.buyBinds.length + ' buy bind' + (STATE.buyBinds.length !== 1 ? 's' : '');
}

function removeBuyBind(i) { STATE.buyBinds.splice(i, 1); save(); renderBuyBinds(); updateDash(); }

function copyBuyBinds() {
    const t = STATE.buyBinds.map(b => `bind "${b.key}" "${b.cmd}"`).join('\n');
    navigator.clipboard.writeText(t).then(() => showToast('Copied!'));
}

// =============================================================
// BIND SWITCHER
// =============================================================
let bsCurrentType = 'simple';

function bsTab(type, el) {
    bsCurrentType = type;
    document.querySelectorAll('.bs-tab').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
    ['simple', 'toggle', 'hold', 'cfgexec'].forEach(t => {
        document.getElementById('bsf-' + t).style.display = (t === type ? 'block' : 'none');
    });
}

function cfgExecTypeChange() {
    const v = document.getElementById('bs-c-type').value;
    document.getElementById('cfg-simple-row').style.display = (v === 'simple' ? 'flex' : 'none');
    document.getElementById('cfg-toggle-row').style.display = (v === 'toggle' ? 'block' : 'none');
    document.getElementById('cfg-hold-row').style.display = (v === 'hold' ? 'block' : 'none');
}

function addSimpleBind() {
    const key = document.getElementById('bs-s-key').value.trim().toUpperCase();
    const cmd = document.getElementById('bs-s-cmd').value.trim();
    const desc = document.getElementById('bs-s-desc').value.trim();
    if (!key || !cmd) { alert('Key and Command required.'); return; }
    STATE.switchBinds.push({ type: 'simple', key, cmd, desc });
    save(); renderSwitchBinds(); updateDash(); showToast('Simple bind added!');
    document.getElementById('bs-s-key').value = '';
    document.getElementById('bs-s-cmd').value = '';
    document.getElementById('bs-s-desc').value = '';
}

function addToggleBind() {
    const key = document.getElementById('bs-t-key').value.trim().toUpperCase();
    const alias = document.getElementById('bs-t-alias').value.trim().replace(/[^a-zA-Z0-9_]/g, '_');
    const a = document.getElementById('bs-t-a').value.trim();
    const b = document.getElementById('bs-t-b').value.trim();
    const desc = document.getElementById('bs-t-desc').value.trim();
    if (!key || !alias || !a || !b) { alert('Key, Alias, State A and State B required.'); return; }
    STATE.switchBinds.push({ type: 'toggle', key, alias, stateA: a, stateB: b, desc });
    save(); renderSwitchBinds(); updateDash(); showToast('Toggle bind added!');
}

function addHoldBind() {
    const key = document.getElementById('bs-h-key').value.trim().toUpperCase();
    const alias = document.getElementById('bs-h-alias').value.trim().replace(/[^a-zA-Z0-9_]/g, '_');
    const press = document.getElementById('bs-h-press').value.trim();
    const release = document.getElementById('bs-h-release').value.trim();
    const before = document.getElementById('bs-h-before').value.trim();
    const desc = document.getElementById('bs-h-desc').value.trim();
    if (!key || !alias) { alert('Key and Alias required.'); return; }
    STATE.switchBinds.push({ type: 'hold', key, alias, press, release, before, desc });
    save(); renderSwitchBinds(); updateDash(); showToast('Hold bind added!');
}

function addCfgBind() {
    const key = document.getElementById('bs-c-key').value.trim().toUpperCase();
    const execType = document.getElementById('bs-c-type').value;
    const desc = document.getElementById('bs-c-desc').value.trim();
    const file = document.getElementById('bs-c-file').value.trim();
    const fa = document.getElementById('bs-c-fa').value.trim();
    const fb = document.getElementById('bs-c-fb').value.trim();
    const fp = document.getElementById('bs-c-fp').value.trim();
    const fr = document.getElementById('bs-c-fr').value.trim();
    if (!key) { alert('Key required.'); return; }
    STATE.switchBinds.push({ type: 'cfgexec', key, execType, desc, file, fa, fb, fp, fr });
    save(); renderSwitchBinds(); updateDash(); showToast('CFG bind added!');
}

function genSwitchCfg() {
    return STATE.switchBinds.map(b => {
        if (b.type === 'simple') {
            return (b.desc ? `// ${b.desc}\n` : '') + `bind "${b.key}" "${b.cmd}"`;
        }
        if (b.type === 'toggle') {
            const n = b.alias;
            const lines = [];
            if (b.desc) lines.push(`// ${b.desc}`);
            lines.push(`alias "${n}_a" "${b.stateA}; alias ${n} ${n}_b"`);
            lines.push(`alias "${n}_b" "${b.stateB}; alias ${n} ${n}_a"`);
            lines.push(`alias "${n}" "${n}_a"`);
            lines.push(`bind "${b.key}" "${n}"`);
            return lines.join('\n');
        }
        if (b.type === 'hold') {
            const n = b.alias;
            const lines = [];
            if (b.desc) lines.push(`// ${b.desc}`);
            if (b.before) lines.push(b.before);
            if (b.press) lines.push(`alias "+${n}" "${b.press}"`);
            if (b.release) lines.push(`alias "-${n}" "${b.release}"`);
            lines.push(`bind "${b.key}" "+${n}"`);
            return lines.join('\n');
        }
        if (b.type === 'cfgexec') {
            const n = `cfg_${b.execType}_${b.key}`.replace(/[^a-zA-Z0-9_]/g, '_');
            const lines = [];
            if (b.desc) lines.push(`// ${b.desc}`);
            if (b.execType === 'simple') {
                const f = b.file.endsWith('.cfg') ? b.file : b.file + '.cfg';
                lines.push(`bind "${b.key}" "exec ${f}"`);
            } else if (b.execType === 'toggle') {
                const ca = (b.fa || '').endsWith('.cfg') ? b.fa : (b.fa || '') + '.cfg';
                const cb = (b.fb || '').endsWith('.cfg') ? b.fb : (b.fb || '') + '.cfg';
                if (b.fa) lines.push(`alias "${n}_a" "exec ${ca}; alias ${n} ${n}_b"`);
                if (b.fb) lines.push(`alias "${n}_b" "exec ${cb}; alias ${n} ${n}_a"`);
                lines.push(`alias "${n}" "${n}_a"`);
                lines.push(`bind "${b.key}" "${n}"`);
            } else if (b.execType === 'hold') {
                const cp = (b.fp || '').endsWith('.cfg') ? b.fp : (b.fp || '') + '.cfg';
                const cr = (b.fr || '').endsWith('.cfg') ? b.fr : (b.fr || '') + '.cfg';
                if (b.fp) lines.push(`alias "+${n}" "exec ${cp}"`);
                if (b.fr) lines.push(`alias "-${n}" "exec ${cr}"`);
                lines.push(`bind "${b.key}" "+${n}"`);
            }
            return lines.join('\n');
        }
        return '';
    }).filter(Boolean).join('\n\n');
}

function renderSwitchBinds() {
    const list = document.getElementById('bs-list');
    const preview = document.getElementById('bs-preview');
    if (!STATE.switchBinds.length) {
        list.innerHTML = '<div style="color:var(--muted);font-style:italic;font-size:.82rem;padding:.5rem">No binds yet.</div>';
        preview.textContent = '// No binds yet';
    } else {
        const typeMap = { simple: 'bt-simple', toggle: 'bt-toggle', hold: 'bt-hold', cfgexec: 'bt-cfg' };
        const typeLabel = { simple: 'Simple', toggle: 'Toggle', hold: 'Hold', cfgexec: 'CFG Exec' };
        list.innerHTML = STATE.switchBinds.map((b, i) =>
            `<div class="bs-row">
        <span class="bs-type-badge ${typeMap[b.type]}">${typeLabel[b.type]}</span>
        <span style="color:var(--ctp-peach);font-family:Consolas,monospace;font-weight:700;min-width:55px">${esc(b.key)}</span>
        <span style="flex:1;color:var(--muted);font-size:.78rem">${esc(b.desc || b.cmd || b.alias || b.file || '')}</span>
        <button class="btn btn-danger" onclick="removeSwitchBind(${i})">✕</button>
      </div>`
        ).join('');
        preview.textContent = genSwitchCfg();
    }
    document.getElementById('sb-sw').textContent = STATE.switchBinds.length + ' switch bind' + (STATE.switchBinds.length !== 1 ? 's' : '');
}

function removeSwitchBind(i) { STATE.switchBinds.splice(i, 1); save(); renderSwitchBinds(); updateDash(); }

function copySwitchBinds() {
    navigator.clipboard.writeText(genSwitchCfg()).then(() => showToast('Copied!'));
}

// =============================================================
// SETTINGS EDITOR
// =============================================================
function buildSettingsTable(q = '') {
    const ql = q.toLowerCase();
    const rows = CONVARS.filter(c => !ql || c.n.includes(ql) || c.c.toLowerCase().includes(ql) || c.t.toLowerCase().includes(ql));
    document.getElementById('set-tbody').innerHTML = rows.map(c =>
        `<tr>
      <td class="cv">${esc(c.n)}</td>
      <td style="color:var(--muted);font-size:.75rem">${esc(c.c)}</td>
      <td class="cd">${esc(c.d)}</td>
      <td style="color:var(--muted);font-size:.74rem">${esc(c.r)}</td>
      <td><input type="text" placeholder="${esc(c.d)}" value="${esc(STATE.settings[c.n] ?? '')}" oninput="setSetting('${esc(c.n)}',this.value)" style="width:90px" /></td>
      <td style="color:var(--muted);font-size:.75rem">${esc(c.t)}</td>
    </tr>`
    ).join('');
}
function filterSettings() { buildSettingsTable(document.getElementById('set-search').value); }
function setSetting(n, v) {
    if (v.trim() === '') { delete STATE.settings[n]; }
    else { STATE.settings[n] = v.trim(); }
    save();
    const cnt = Object.keys(STATE.settings).length;
    document.getElementById('sb-set').textContent = cnt + ' setting' + (cnt !== 1 ? 's' : '');
    updateDash();
}

// =============================================================
// CFG EDITOR
// =============================================================
function updateCfgEditor() {
    document.getElementById('cfg-editor-area').value = STATE.cfgText;
    updateCfgMeta();
}
function updateCfgMeta() {
    const lines = STATE.cfgText.split('\n').length;
    document.getElementById('cfg-linecount').textContent = lines + ' line' + (lines !== 1 ? 's' : '');
    document.getElementById('cfg-filename-label').textContent = STATE.cfgFileName || 'Unsaved';
    updateDash();
}
function onCfgEdit() {
    STATE.cfgText = document.getElementById('cfg-editor-area').value;
    save();
    updateCfgMeta();
}
function newCfg() {
    STATE.cfgText = ''; STATE.cfgFileName = 'autoexec.cfg';
    save(); updateCfgEditor();
}
async function readCfgFile() {
    if (!dirHandle) { alert('Select your CS2 cfg folder in the sidebar first.'); return; }
    try {
        const [fh] = await window.showOpenFilePicker({ types: [{ description: 'CFG files', accept: { 'text/plain': ['.cfg'] } }], startIn: dirHandle });
        const f = await fh.getFile();
        STATE.cfgText = await f.text();
        STATE.cfgFileName = f.name;
        save(); updateCfgEditor();
        showToast('Loaded: ' + f.name);
    } catch (e) { if (e.name !== 'AbortError') console.error(e); }
}
async function saveCfgFile() {
    if (!dirHandle) { alert('Select your CS2 cfg folder first.'); return; }
    try {
        const fh = await dirHandle.getFileHandle(STATE.cfgFileName || 'autoexec.cfg', { create: true });
        const w = await fh.createWritable();
        await w.write(STATE.cfgText); await w.close();
        showToast('💾 Saved: ' + STATE.cfgFileName);
    } catch (e) { alert('Error: ' + e.message); }
}
function downloadCfgFile() {
    dlBlob(STATE.cfgText, STATE.cfgFileName || 'autoexec.cfg');
}

// =============================================================
// COMMAND VIEWER
// =============================================================
function buildCmdViewer(q = '') {
    const ql = q.toLowerCase();
    const cmds = COMMANDS.filter(c => !ql || c.n.includes(ql) || c.d.toLowerCase().includes(ql));
    document.getElementById('cmd-grid').innerHTML = cmds.map(c =>
        `<div class="cmd-card">
      <div class="cmd-name">${esc(c.n)}</div>
      <div class="cmd-desc">${esc(c.d)}</div>
    </div>`
    ).join('');
}
function filterCmds() { buildCmdViewer(document.getElementById('cmd-search').value); }

// =============================================================
// EXPORT
// =============================================================
function buildAutoexec() {
    const lines = [
        '// ================================================',
        '// autoexec.cfg — CS2 CFG Configurator Web Edition',
        '// https://vsvito420.github.io/cs2-cfg-configurator/demo.html',
        '// Generated: ' + new Date().toLocaleString(),
        '// ================================================',
        '',
    ];
    if (Object.keys(STATE.settings).length) {
        lines.push('// ─── Settings ───');
        for (const [k, v] of Object.entries(STATE.settings)) lines.push(`${k} ${v}`);
        lines.push('');
    }
    if (STATE.buyBinds.length) {
        lines.push('// ─── Buy Binds ───');
        STATE.buyBinds.forEach(b => lines.push(`bind "${b.key}" "${b.cmd}"`))
        lines.push('');
    }
    const sw = genSwitchCfg();
    if (sw) {
        lines.push('// ─── Bind Switcher ───');
        lines.push(sw);
        lines.push('');
    }
    if (STATE.cfgText.trim()) {
        lines.push('// ─── CFG Editor content ───');
        lines.push(STATE.cfgText.trim());
        lines.push('');
    }
    lines.push('echo "[autoexec] Config loaded ✓"');
    return lines.join('\n');
}

function refreshExport() {
    document.getElementById('exp-preview').textContent = buildAutoexec();
}
function copyFull() {
    navigator.clipboard.writeText(buildAutoexec()).then(() => showToast('Copied!'));
}
function downloadAutoexec() {
    dlBlob(buildAutoexec(), 'autoexec.cfg');
}
async function saveAutoexec() {
    const status = document.getElementById('exp-status');
    if (!dirHandle) {
        status.innerHTML = '<div class="alert alert-warn">⚠️ No folder selected. Use the sidebar.</div>';
        return;
    }
    try {
        const fh = await dirHandle.getFileHandle('autoexec.cfg', { create: true });
        const w = await fh.createWritable();
        await w.write(buildAutoexec()); await w.close();
        status.innerHTML = '<div class="alert alert-ok">✅ autoexec.cfg saved to <strong>' + dirHandle.name + '</strong>!</div>';
    } catch (e) {
        status.innerHTML = '<div class="alert alert-red">❌ Error: ' + esc(e.message) + '</div>';
    }
}

// =============================================================
// DASHBOARD
// =============================================================
function updateDash() {
    document.getElementById('d-buybinds').textContent = STATE.buyBinds.length;
    document.getElementById('d-switchbinds').textContent = STATE.switchBinds.length;
    document.getElementById('d-settings').textContent = Object.keys(STATE.settings).length;
    const cfgLines = STATE.cfgText.trim() ? STATE.cfgText.split('\n').length : 0;
    document.getElementById('d-cfglines').textContent = cfgLines;
}

// =============================================================
// UTILS
// =============================================================
function esc(s) {
    return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
function dlBlob(text, name) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([text], { type: 'text/plain' }));
    a.download = name; a.click();
}
function showToast(msg) {
    const t = document.createElement('div');
    t.textContent = msg;
    Object.assign(t.style, {
        position: 'fixed', bottom: '1.5rem', right: '1.5rem',
        background: 'var(--ctp-green)', color: 'var(--ctp-crust)',
        padding: '.45rem 1rem', borderRadius: '5px', fontWeight: '700',
        fontSize: '.84rem', zIndex: '9999', boxShadow: '0 4px 16px rgba(0,0,0,.4)'
    });
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2200);
}