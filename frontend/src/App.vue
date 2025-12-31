<template>
  <div class="min-h-screen font-sans bg-dm-bg text-slate-200">
    <div v-if="!isLoggedIn" class="fixed inset-0 bg-dm-bg flex items-center justify-center p-6 z-[9999]">
      <div class="w-full max-w-md bg-dm-card border border-slate-700/50 rounded-3xl p-8 shadow-2xl animate-in">
        <div class="text-center mb-8">
          <div class="w-16 h-16 bg-dm-accent/10 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-dm-accent/20">
            <span class="text-3xl">⚓</span>
          </div>
          <h2 class="text-2xl font-black text-white tracking-tighter">DockMaster</h2>
          <p class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mt-2">Authorization Required</p>
        </div>
        <form @submit.prevent="handleLogin" class="space-y-4">
          <input v-model="loginPass" type="password" placeholder="Master Password" class="w-full h-12 bg-slate-950 border border-slate-700 rounded-xl px-4 text-white outline-none focus:border-dm-accent" />
          <button type="submit" :disabled="loading" class="w-full h-12 bg-dm-accent text-white rounded-xl font-black uppercase tracking-widest text-[11px]">
            {{ loading ? 'Unlocking...' : 'Open Dashboard' }}
          </button>
          <p v-if="loginError" class="text-rose-500 text-[10px] font-bold text-center uppercase">{{ loginError }}</p>
        </form>
      </div>
    </div>

    <div v-else @click="closeAllMenus" class="min-h-screen p-4 md:p-6">
      <header class="max-w-[1600px] mx-auto mb-8 relative">
        <div class="flex flex-wrap lg:flex-nowrap items-center gap-4 lg:gap-6">
          <h1 class="flex items-center gap-2 shrink-0 tracking-tighter order-1">
            <span class="text-2xl text-dm-accent drop-shadow-[0_0_8px_rgba(59,130,246,0.5)]">⚓</span>
            <span class="text-xl font-black text-white block">DockMaster</span>
          </h1>
          <div class="relative flex-grow order-3 lg:order-2 min-w-[200px]">
            <input v-model="searchQuery" type="text" placeholder="Search stacks..." class="w-full h-11 bg-dm-card/50 border border-slate-700/50 rounded-xl px-10 text-xs text-white outline-none focus:border-dm-accent" />
          </div>
          <div class="order-4 lg:order-3 w-full lg:w-auto">
            <div class="bg-dm-card/40 border border-slate-700/30 rounded-xl px-4 h-11 flex items-center gap-5 overflow-x-auto no-scrollbar">
                <div v-for="(val, key) in sysStats" :key="key" class="flex items-center gap-2 shrink-0">
                    <span class="text-[9px] font-black uppercase text-slate-500">{{ key }}</span>
                    <span class="text-xs font-bold text-white tabular-nums">{{ val }}{{ key === 'temp' ? '°C' : '%' }}</span>
                </div>
            </div>
          </div>
          <div class="order-2 lg:order-4 shrink-0 ml-auto lg:ml-0">
            <button @click.stop="menuOpen = !menuOpen" class="w-11 h-11 flex flex-col items-center justify-center gap-1.5 bg-slate-800/50 border border-slate-700/50 rounded-xl" :class="isEditMode ? 'border-dm-accent' : ''">
              <div class="w-5 h-0.5 bg-slate-300 rounded-full"></div>
              <div class="w-5 h-0.5 bg-slate-300 rounded-full"></div>
              <div class="w-5 h-0.5 bg-slate-300 rounded-full"></div>
            </button>
          </div>
        </div>

        <transition name="menu-fade">
          <div v-if="menuOpen" @click.stop class="absolute right-0 top-14 z-[1000]">
            <div class="bg-dm-card border border-slate-700 rounded-2xl shadow-2xl w-56 overflow-hidden">
              <div @click="isEditMode = !isEditMode" class="flex items-center justify-between p-4 hover:bg-white/5 cursor-pointer">
                <span class="text-xs font-bold uppercase" :class="isEditMode ? 'text-dm-accent' : 'text-slate-400'">Edit Mode</span>
                <div class="relative h-5 w-10 rounded-full transition-colors" :class="isEditMode ? 'bg-dm-accent' : 'bg-slate-700'">
                  <span class="absolute h-4 w-4 bg-white rounded-full transition-all mt-0.5 ml-0.5" :class="isEditMode ? 'translate-x-5' : 'translate-x-0'"></span>
                </div>
              </div>
              <template v-if="isEditMode">
                <div @click="openGlobalVariables(); menuOpen = false" class="p-4 hover:bg-white/5 cursor-pointer border-t border-slate-700/30 text-xs font-bold text-slate-300 uppercase">Global Registry</div>
                <button @click="openCreationModal(); menuOpen = false" class="w-full text-left p-4 text-xs font-bold text-emerald-400 hover:bg-emerald-500/10 uppercase border-t border-slate-700/30">＋ New Stack</button>
              </template>
              <button @click="logout" class="w-full text-left p-4 text-xs font-bold text-rose-500 hover:bg-rose-500/10 uppercase border-t border-slate-700/30">Logout</button>
            </div>
          </div>
        </transition>
      </header>

      <div class="max-w-[1600px] mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-20">
        <div v-for="stack in filteredStacks" :key="stack.name" class="bg-dm-card rounded-2xl p-5 border border-slate-700/50 flex flex-col shadow-lg animate-in group relative">
          <div class="flex justify-between items-start mb-5">
            <div class="truncate">
              <h2 class="text-base font-black text-white truncate tracking-tight">{{ stack.name }}</h2>
              <div class="flex items-center gap-1.5 mt-1">
                <span class="w-1.5 h-1.5 rounded-full" :class="stack.status === 'Running' ? 'bg-emerald-500' : 'bg-rose-500'"></span>
                <span class="text-[10px] font-bold uppercase text-slate-500">{{ stack.status }}</span>
              </div>
            </div>
            <div v-if="isEditMode" class="relative">
              <button @click.stop="activeStackMenu = activeStackMenu === stack.name ? null : stack.name" class="w-8 h-8 flex items-center justify-center text-slate-500 rounded-lg bg-slate-800/30 border border-slate-700/30">⋮</button>
              <div v-if="activeStackMenu === stack.name" class="absolute right-0 top-full mt-2 z-[200] bg-dm-card border border-slate-700 rounded-xl shadow-2xl py-1 w-44">
                <button @click="openEditor(stack.name, 'docker-compose.yml'); activeStackMenu = null" class="w-full text-left px-4 py-2.5 text-[10px] font-bold text-white hover:bg-white/10 uppercase">Edit Stack</button>
                <button @click="triggerDeploy(stack.name); activeStackMenu = null" class="w-full text-left px-4 py-2.5 text-[10px] font-bold text-emerald-400 hover:bg-emerald-500/10 uppercase">Deploy</button>
                <button @click="triggerDown(stack.name); activeStackMenu = null" class="w-full text-left px-4 py-2.5 text-[10px] font-bold text-rose-500 hover:bg-rose-500/10 uppercase">Down</button>
              </div>
            </div>
          </div>

          <div class="space-y-3">
            <div v-for="cont in stack.containers" :key="cont.id" class="bg-slate-900/50 p-3 rounded-xl border border-slate-700/30 flex items-center justify-between">
              <div class="flex items-center gap-3 overflow-hidden">
                <div @click="openContainerUI(cont)" class="w-9 h-9 shrink-0 flex items-center justify-center bg-slate-800 rounded-lg p-1.5 border border-slate-700/50 cursor-pointer hover:border-dm-accent">
                    <img :src="cont.icon || DEFAULT_SVG" class="w-full h-full object-contain" />
                </div>
                <div class="flex flex-col truncate">
                  <span @click="openContainerUI(cont)" class="text-sm font-bold text-slate-200 cursor-pointer hover:text-dm-accent truncate">{{ cont.display_name || cont.name }}</span>
                  <span class="text-[9px] uppercase font-mono text-slate-500">{{ cont.status }}</span>
                </div>
              </div>
              <div v-if="isEditMode" class="relative">
                  <button @click.stop="activeDropdown = activeDropdown === cont.id ? null : cont.id" class="w-8 h-8 text-slate-500 hover:text-white">⋮</button>
                  <div v-if="activeDropdown === cont.id" class="absolute right-0 top-full z-[100] mt-2 bg-dm-card border border-slate-700 rounded-xl py-1 w-40 shadow-2xl">
                    <button @click="openMetadataEditor(cont)" class="w-full text-left px-4 py-2 text-[10px] font-bold text-amber-400 hover:bg-white/5 uppercase">Config</button>
                    <button @click="triggerLogs(cont)" class="w-full text-left px-4 py-2 text-[10px] font-bold text-dm-accent hover:bg-white/5 uppercase">Logs</button>
                    <button @click="runAction(cont.id, cont.status === 'running' ? 'stop' : 'start')" class="w-full text-left px-4 py-2 text-[10px] font-bold uppercase" :class="cont.status === 'running' ? 'text-rose-400' : 'text-emerald-400'">{{ cont.status === 'running' ? 'Stop' : 'Start' }}</button>
                  </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="editor.visible" class="fixed inset-0 bg-slate-950/80 z-[5000] flex items-center justify-center p-4 md:p-8 backdrop-blur-md">
        <div class="w-full h-full max-w-5xl bg-dm-card border border-slate-700/50 rounded-3xl flex flex-col shadow-2xl overflow-hidden animate-in">
            <div class="h-16 px-6 bg-slate-800/20 border-b border-slate-700/50 flex justify-between items-center">
                <span class="text-xs font-black text-dm-accent uppercase">{{ editor.isGlobal ? 'Global Registry' : editor.stack }}</span>
                <div class="flex items-center gap-4">
                    <button v-if="editor.isGlobal" @click="addNewVariable" class="text-[10px] font-bold text-emerald-400 uppercase">+ Add Row</button>
                    <button @click="editor.visible = false" class="text-slate-400 text-2xl">&times;</button>
                </div>
            </div>
            <div class="flex-1 overflow-hidden">
                <div v-if="editor.isGlobal" class="h-full overflow-y-auto p-6">
                    <div class="grid grid-cols-1 gap-3">
                        <div v-for="(val, id) in globalVarsObj" :key="id" class="flex items-center gap-3">
                            <input v-model="globalVarKeys[id]" placeholder="NAME" class="w-1/3 h-11 bg-slate-950 border border-slate-700/50 rounded-xl px-4 text-xs font-mono text-dm-accent" />
                            <input v-model="globalVarsObj[id]" placeholder="Value" class="flex-1 h-11 bg-slate-950 border border-slate-700/50 rounded-xl px-4 text-xs text-white" />
                            <button @click="deleteVariable(id)" class="text-rose-500/40 hover:text-rose-500">🗑</button>
                        </div>
                    </div>
                </div>
                <div v-else class="h-full flex flex-col lg:flex-row">
                    <textarea v-model="editor.content" @input="debounceParse" class="flex-1 bg-transparent p-6 font-mono text-xs text-slate-300 outline-none resize-none"></textarea>
                    <div class="w-80 bg-slate-900/20 p-6 overflow-y-auto border-l border-slate-700/30">
                        <span class="text-[10px] font-bold text-slate-500 uppercase block mb-4">Inspector</span>
                        <div v-for="(val, key) in parsedVars" :key="key" class="mb-4">
                            <label class="text-[9px] font-bold text-slate-600 uppercase">{{ key }}</label>
                            <input v-model="parsedVars[key]" class="w-full h-9 bg-slate-950 border border-slate-700/50 rounded-lg px-3 text-xs text-white mt-1" />
                        </div>
                    </div>
                </div>
            </div>
            <div class="p-6 bg-slate-800/20 border-t border-slate-700/50 flex items-center justify-between gap-4">
                <button v-if="!editor.isGlobal" @click="deleteStackConfirm(editor.stack)" class="h-12 px-6 bg-rose-500/10 text-rose-500 rounded-2xl text-[11px] font-black uppercase hover:bg-rose-500 hover:text-white transition-all">Delete Stack</button>
                <button @click="saveSmartFile" class="flex-1 h-12 bg-dm-accent text-white rounded-2xl text-[11px] font-black uppercase">Save & Sync</button>
            </div>
        </div>
    </div>

    <div v-if="terminal.visible" class="fixed inset-0 bg-slate-950/90 z-[6000] flex items-center justify-center p-0 md:p-6 backdrop-blur-md">
        <div class="w-full h-full md:max-w-4xl md:h-[65vh] bg-slate-950 border border-slate-800 md:rounded-2xl flex flex-col overflow-hidden">
            <div class="p-3 bg-slate-900 border-b border-slate-800 flex justify-between items-center">
                <span class="text-[10px] font-mono text-dm-accent uppercase">{{ terminal.title }}</span>
                <button @click="closeTerminal" class="px-4 py-1.5 bg-rose-600 text-white text-[10px] font-black uppercase rounded-lg">Close</button>
            </div>
            <div ref="terminalElement" class="flex-1 p-3 bg-black overflow-hidden font-mono text-xs"></div>
        </div>
    </div>

    <div v-if="metadataModal.visible" class="fixed inset-0 bg-slate-950/80 z-[7000] flex items-center justify-center p-4 backdrop-blur-sm">
        <div class="w-full max-w-sm bg-dm-card border border-slate-700 rounded-2xl p-6 shadow-2xl">
            <h3 class="text-xs font-black uppercase text-dm-accent mb-4">Update Container Config</h3>
            <div class="space-y-4">
                <div>
                    <label class="text-[9px] font-bold text-slate-500 uppercase">Display Name</label>
                    <input v-model="metadataModal.displayName" class="w-full h-10 bg-slate-950 border border-slate-700 rounded-lg px-3 text-sm text-white mt-1" />
                </div>
                <div>
                    <label class="text-[9px] font-bold text-slate-500 uppercase">Icon URL</label>
                    <input v-model="metadataModal.iconUrl" class="w-full h-10 bg-slate-950 border border-slate-700 rounded-lg px-3 text-sm text-white mt-1" />
                </div>
                <div>
                    <label class="text-[9px] font-bold text-slate-500 uppercase block mb-1">Launch URL Mode</label>
                    <div class="flex gap-1 mb-2">
                        <button @click="metadataModal.urlMode = 'auto'" :class="metadataModal.urlMode === 'auto' ? 'bg-dm-accent text-white' : 'bg-slate-800 text-slate-500'" class="flex-1 py-1.5 rounded text-[9px] font-bold uppercase">Auto</button>
                        <button @click="metadataModal.urlMode = 'manual'" :class="metadataModal.urlMode === 'manual' ? 'bg-dm-accent text-white' : 'bg-slate-800 text-slate-500'" class="flex-1 py-1.5 rounded text-[9px] font-bold uppercase">Manual</button>
                    </div>
                    <input v-if="metadataModal.urlMode === 'manual'" v-model="metadataModal.manualUrl" placeholder="https://..." class="w-full h-10 bg-slate-950 border border-slate-700 rounded-lg px-3 text-xs text-white mt-2" />
                </div>
                <div class="flex gap-2 pt-2">
                    <button @click="metadataModal.visible = false" class="flex-1 h-10 bg-slate-800 text-slate-400 rounded-lg text-[10px] font-bold uppercase">Cancel</button>
                    <button @click="saveMetadata" class="flex-1 h-10 bg-dm-accent text-white rounded-lg text-[10px] font-bold uppercase">Save</button>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, computed } from 'vue';
import axios from 'axios';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import 'xterm/css/xterm.css';

const DEFAULT_SVG = `data:image/svg+xml;base64,${btoa('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="3"></circle><line x1="12" y1="22" x2="12" y2="8"></line><path d="M5 12H2a10 10 0 0 0 20 0h-3"></path></svg>')}`;

const isLoggedIn = ref(false), loginPass = ref(""), loginError = ref(""), loading = ref(false);
const isEditMode = ref(false), menuOpen = ref(false), searchQuery = ref(""), stacks = ref([]), sysStats = ref({});
const activeDropdown = ref(null), activeStackMenu = ref(null);
const editor = reactive({ visible: false, content: '', secondaryContent: '', stack: '', filename: '', isGlobal: false });
const metadataModal = reactive({ visible: false, containerId: null, displayName: '', iconUrl: '', manualUrl: '', urlMode: 'auto' });
const terminal = reactive({ visible: false, title: '' }), terminalElement = ref(null);
const parsedVars = ref({}), globalVarsObj = ref({}), globalVarKeys = ref({});
let xterm, socket, fitAddon, parseTimer;

axios.interceptors.request.use(c => {
  const t = localStorage.getItem('dm_token');
  if (t) c.headers.Authorization = `Bearer ${t}`;
  return c;
});

const handleLogin = async () => {
  loading.value = true;
  try {
    const p = new URLSearchParams(); p.append('username', 'admin'); p.append('password', loginPass.value);
    const r = await axios.post('/api/login', p);
    localStorage.setItem('dm_token', r.data.access_token);
    isLoggedIn.value = true; startApp();
  } catch { loginError.value = "Invalid Password"; } finally { loading.value = false; }
};

const logout = () => { localStorage.removeItem('dm_token'); isLoggedIn.value = false; };
const startApp = () => { fetchStacks(); fetchSysStats(); setInterval(fetchSysStats, 5000); };
const fetchStacks = async () => { try { stacks.value = (await axios.get('/api/stacks')).data; } catch(e) { if(e.response?.status === 401) logout(); } };
const fetchSysStats = async () => { try { sysStats.value = (await axios.get('/api/system/stats')).data; } catch {} };
const closeAllMenus = () => { menuOpen.value = false; activeDropdown.value = null; activeStackMenu.value = null; };
const filteredStacks = computed(() => !searchQuery.value ? stacks.value : stacks.value.filter(s => s.name.toLowerCase().includes(searchQuery.value.toLowerCase())));

const parseEnv = (raw) => {
    const env = {}; if (!raw) return env;
    raw.split('\n').forEach(l => {
        const t = l.trim(); if (!t || t.startsWith('#')) return;
        const [k, ...v] = t.split('='); if (k) env[k.trim()] = v.join('=').trim();
    });
    return env;
};

const extractVars = (text) => {
    const regex = /(?:\$([A-Za-z0-9_]+))|(?:\${([A-Za-z0-9_]+)(?::?[-?][^}]*)?})/g;
    const matches = new Set(); let m;
    while ((m = regex.exec(text)) !== null) { matches.add(m[1] || m[2]); }
    return Array.from(matches);
};

const debounceParse = () => {
    clearTimeout(parseTimer);
    parseTimer = setTimeout(() => {
        const keys = extractVars(editor.content);
        const existing = parseEnv(editor.secondaryContent);
        const n = {}; keys.forEach(k => { n[k] = existing[k] || ""; });
        parsedVars.value = n;
    }, 400);
};

const openEditor = async (sn, fn) => {
    const [r1, r2] = await Promise.all([axios.get(`/api/stack/${sn}/file/${fn}`), axios.get(`/api/stack/GLOBAL/file/global.env`)]);
    editor.content = r1.data.content; editor.secondaryContent = r2.data.content;
    editor.stack = sn; editor.filename = fn; editor.isGlobal = false; editor.visible = true;
    debounceParse();
};

const openGlobalVariables = async () => {
    const r = await axios.get('/api/stack/GLOBAL/file/global.env');
    const obj = parseEnv(r.data.content);
    globalVarsObj.value = {}; globalVarKeys.value = {};
    Object.entries(obj).forEach(([k, v]) => {
        const id = Math.random().toString(36).substr(2, 9);
        globalVarKeys.value[id] = k; globalVarsObj.value[id] = v;
    });
    editor.isGlobal = true; editor.visible = true;
};

const saveSmartFile = async () => {
    let envStr = "";
    if (editor.isGlobal) {
        envStr = Object.keys(globalVarsObj.value).filter(id => globalVarKeys.value[id].trim()).map(id => `${globalVarKeys.value[id].trim()}=${globalVarsObj.value[id]}`).join('\n');
    } else {
        await axios.post(`/api/stack/${editor.stack}/file`, { filename: editor.filename, content: editor.content });
        const merged = { ...parseEnv(editor.secondaryContent), ...parsedVars.value };
        envStr = Object.entries(merged).map(([k, v]) => `${k}=${v}`).join('\n');
    }
    await axios.post(`/api/stack/GLOBAL/file`, { filename: 'global.env', content: envStr });
    editor.visible = false; fetchStacks();
};

const deleteStackConfirm = async (sn) => {
    if(confirm(`WARNING: This will permanently delete the folder for stack: ${sn}. This cannot be undone. Proceed?`)) {
        await axios.delete(`/api/stack/${sn}`);
        editor.visible = false;
        fetchStacks();
    }
}

const openMetadataEditor = (c) => {
    metadataModal.containerId = c.id;
    metadataModal.displayName = c.display_name || c.name;
    metadataModal.iconUrl = c.icon || '';
    metadataModal.manualUrl = c.url || '';
    metadataModal.urlMode = (c.url && !c.url.includes(window.location.hostname)) ? 'manual' : 'auto';
    metadataModal.visible = true; activeDropdown.value = null;
};

const saveMetadata = async () => {
    await axios.post(`/api/container/${metadataModal.containerId}/metadata`, {
        display_name: metadataModal.displayName,
        icon: metadataModal.iconUrl,
        url: metadataModal.urlMode === 'manual' ? metadataModal.manualUrl : null
    });
    metadataModal.visible = false; fetchStacks();
};

const openContainerUI = (c) => {
    if (c.url) window.open(c.url, '_blank');
    else {
        const p = Object.values(c.ports).find(v => v !== null)?.[0]?.HostPort;
        window.open(`http://${window.location.hostname}${p ? ':' + p : ''}`, '_blank');
    }
};

const setupTerminal = (t) => {
    terminal.visible = true; terminal.title = t;
    nextTick(() => {
        if (xterm) xterm.dispose();
        xterm = new Terminal({ fontSize: 12, convertEol: true, theme: { background: '#000' } });
        fitAddon = new FitAddon(); xterm.loadAddon(fitAddon);
        xterm.open(terminalElement.value); fitAddon.fit();
    });
};

const triggerLogs = (c) => {
    setupTerminal(`Logs: ${c.name}`);
    socket = new WebSocket(`ws://${window.location.host}/ws/logs/${c.id}?token=${localStorage.getItem('dm_token')}`);
    socket.onmessage = (e) => xterm.write(e.data);
};

const triggerDeploy = (n) => {
    setupTerminal(`Deploy: ${n}`);
    socket = new WebSocket(`ws://${window.location.host}/ws/deploy/${n}?token=${localStorage.getItem('dm_token')}`);
    socket.onmessage = (e) => xterm.write(e.data);
    socket.onclose = () => fetchStacks();
};

const triggerDown = (n) => {
    if(confirm(`Down stack ${n}?`)) {
        setupTerminal(`Down: ${n}`);
        socket = new WebSocket(`ws://${window.location.host}/ws/down/${n}?token=${localStorage.getItem('dm_token')}`);
        socket.onmessage = (e) => xterm.write(e.data);
        socket.onclose = () => fetchStacks();
    }
};

const closeTerminal = () => { 
    if(socket && socket.readyState === WebSocket.OPEN) socket.send("QUIT");
    if(socket) socket.close(); 
    terminal.visible = false; 
    fetchStacks(); 
};

const runAction = async (id, a) => { await axios.post(`/api/container/${id}/${a}`); setTimeout(fetchStacks, 1000); };
const openCreationModal = async () => { 
    const n = prompt("New Stack Name:"); 
    if(n) {
        try {
            await axios.post('/api/stack/create', { name: n }); 
            fetchStacks(); 
        } catch(e) {
            alert("Error: " + (e.response?.data?.detail || "Method Not Allowed"));
        }
    }
};

const addNewVariable = () => { 
    const id = Math.random().toString(36).substr(2, 9); 
    globalVarKeys.value[id] = ""; globalVarsObj.value[id] = ""; 
};
const deleteVariable = (id) => { delete globalVarsObj.value[id]; delete globalVarKeys.value[id]; };

onMounted(() => { if (localStorage.getItem('dm_token')) { isLoggedIn.value = true; startApp(); } });
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
:root { --dm-bg: #0b0f1a; --dm-card: #161c2d; --dm-accent: #3b82f6; }
body { font-family: 'Inter', sans-serif; background: var(--dm-bg); margin: 0; }
.bg-dm-bg { background: var(--dm-bg); }
.bg-dm-card { background: var(--dm-card); }
.text-dm-accent { color: var(--dm-accent); }
.bg-dm-accent { background: var(--dm-accent); }
.animate-in { animation: s 0.3s ease-out; }
@keyframes s { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.no-scrollbar::-webkit-scrollbar { display: none; }
.menu-fade-enter-active, .menu-fade-leave-active { transition: opacity 0.2s, transform 0.2s; }
.menu-fade-enter-from, .menu-fade-leave-to { opacity: 0; transform: scale(0.95); }
</style>
