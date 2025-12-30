<template>
  <div class="min-h-screen p-4 md:p-8 font-sans bg-dm-bg text-slate-200 selection:bg-dm-accent/30">
    <header class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center mb-10 gap-4">
      <div class="flex items-center gap-8 w-full md:w-auto">
        <h1 class="text-2xl font-black text-white flex items-center gap-2 shrink-0 tracking-tighter">
          <span class="text-dm-accent drop-shadow-[0_0_8px_rgba(59,130,246,0.5)]">⚓</span> DockMaster
        </h1>
        <div class="relative w-full max-w-md group">
          <input v-model="searchQuery" type="text" placeholder="Search stacks..." class="w-full bg-dm-card/50 border border-slate-700/50 rounded-xl py-2.5 px-11 text-sm text-white outline-none focus:border-dm-accent focus:ring-4 focus:ring-dm-accent/10 transition-all placeholder:text-slate-500" />
          <span class="absolute left-4 top-3 opacity-30 group-focus-within:opacity-100 transition-opacity">🔍</span>
        </div>
      </div>

      <div class="relative">
        <button 
          @click="menuOpen = !menuOpen" 
          :class="anyModalOpen ? 'z-0' : 'z-[100]'"
          class="px-5 py-2.5 bg-dm-card hover:bg-slate-700 border border-slate-700/50 rounded-xl text-xs font-bold uppercase tracking-widest transition-all relative shadow-lg shadow-black/20"
        >
          {{ menuOpen ? 'Close' : 'Menu' }}
        </button>
        
        <div v-if="menuOpen" @click="menuOpen = false" class="fixed inset-0 z-[1000]"></div>
        
        <div v-if="menuOpen" class="absolute right-0 top-full mt-3 w-64 bg-dm-card border border-slate-700/50 rounded-2xl shadow-2xl py-2 z-[1002] overflow-hidden backdrop-blur-xl">
          <div class="px-4 py-3 border-b border-slate-700/50 mb-2 flex justify-between items-center bg-white/5">
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Edit Mode</span>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="isEditMode" class="sr-only peer">
              <div class="w-9 h-5 bg-slate-700 rounded-full peer peer-checked:after:translate-x-full peer-checked:bg-dm-accent after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all shadow-inner"></div>
            </label>
          </div>
          <template v-if="isEditMode">
            <button @click="openCreationModal(); menuOpen = false" class="w-full text-left px-4 py-3 text-sm hover:bg-white/5 text-emerald-400 transition-colors">＋ New Stack</button>
            <button @click="openGlobalVariables(); menuOpen = false" class="w-full text-left px-4 py-3 text-sm hover:bg-white/5 text-dm-accent transition-colors">⚙ Global Variables</button>
          </template>
        </div>
      </div>
    </header>

    <div v-if="filteredStacks.length" class="max-w-7xl mx-auto grid grid-cols-[repeat(auto-fill,minmax(320px,1fr))] gap-8">
      <div v-for="stack in filteredStacks" :key="stack.name" class="bg-dm-card rounded-2xl p-6 border border-slate-700/50 relative shadow-xl shadow-black/10 hover:border-slate-600 transition-all group/stack-card">
        <div class="flex justify-between items-start mb-6">
          <div class="truncate">
            <h2 class="text-xl font-bold text-white tracking-tight truncate mb-1">{{ stack.name }}</h2>
            <div class="flex items-center gap-2">
               <span class="w-2 h-2 rounded-full" :class="stack.status === 'Running' ? 'bg-emerald-500' : 'bg-rose-500'"></span>
               <span :class="stack.status === 'Running' ? 'text-emerald-500' : 'text-rose-500'" class="text-[11px] font-black uppercase tracking-widest">{{ stack.status }}</span>
            </div>
          </div>
          
          <div v-if="isEditMode" class="relative group/opt">
            <button class="text-[10px] font-bold text-slate-500 hover:text-white uppercase tracking-tighter bg-slate-900/50 border border-slate-700/50 px-3 py-1.5 rounded-lg transition-all">Options</button>
            <div class="absolute right-0 top-full hidden group-hover/opt:block z-[50] pt-2">
              <div class="bg-dm-card border border-slate-700 rounded-xl shadow-2xl py-1.5 w-36 overflow-hidden backdrop-blur-lg">
                <button @click="openEditor(stack.name, 'docker-compose.yml')" class="block w-full text-left px-4 py-2 text-xs text-white hover:bg-dm-accent">Edit Stack</button>
                <button @click="triggerDeploy(stack.name)" class="block w-full text-left px-4 py-2 text-xs text-emerald-400 hover:bg-emerald-500 hover:text-white font-bold">Deploy</button>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div v-for="cont in filterContainers(stack.containers)" :key="cont.id" @click="openContainerUI(cont)" class="group/cont relative bg-slate-900/50 p-4 rounded-xl border border-slate-700/30 flex flex-col items-center cursor-pointer hover:bg-dm-accent/5 transition-all">
            <div class="absolute top-2 left-2 w-1.5 h-1.5 rounded-full" :class="cont.status === 'running' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-rose-500'"></div>
            
            <div v-if="isEditMode" class="absolute inset-x-1 top-1 opacity-0 group-hover/cont:opacity-100 transition-all flex justify-center gap-2 bg-slate-800 border border-slate-600 rounded-lg py-1 shadow-2xl z-20 scale-95 group-hover/cont:scale-100">
                <button @click.stop="runAction(cont.id, 'restart')" class="text-[8px] font-black text-slate-400 hover:text-blue-400 uppercase">Restart</button>
                <button @click.stop="runAction(cont.id, cont.status === 'running' ? 'stop' : 'start')" class="text-[8px] font-black text-slate-400 hover:text-white uppercase">
                    {{ cont.status === 'running' ? 'Stop' : 'Start' }}
                </button>
                <button @click.stop="showLogs(cont)" class="text-[8px] font-black text-slate-400 hover:text-dm-accent uppercase">Logs</button>
            </div>

            <img :src="getIcon(cont)" class="w-10 h-10 mb-2 object-contain drop-shadow-md group-hover/cont:scale-110 transition-transform duration-300" />
            <span class="text-[10px] font-bold text-slate-400 truncate w-full text-center mb-4">{{ cont.name }}</span>

            <div v-if="cont.status === 'running'" class="w-full space-y-2.5 mt-auto">
              <div>
                <div class="flex justify-between text-[7px] font-black uppercase tracking-widest text-slate-500 mb-1">
                  <span>CPU</span>
                  <span>{{ getUsage(cont.id, 'cpu') }}%</span>
                </div>
                <div class="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                  <div class="h-full bg-dm-accent transition-all duration-1000" :style="{ width: getUsage(cont.id, 'cpu') + '%' }"></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between text-[7px] font-black uppercase tracking-widest text-slate-500 mb-1">
                  <span>RAM</span>
                  <span>{{ getUsage(cont.id, 'mem') }}%</span>
                </div>
                <div class="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                  <div class="h-full bg-emerald-500 transition-all duration-1000" :style="{ width: getUsage(cont.id, 'mem') + '%' }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="editor.visible" class="fixed inset-0 bg-slate-950/80 z-[500] flex items-center justify-center p-4 backdrop-blur-md">
        <div class="w-full max-w-[95vw] h-[90vh] bg-dm-card border border-slate-700 rounded-3xl flex flex-col shadow-2xl overflow-hidden">
            <div class="p-5 bg-slate-800/50 border-b border-slate-700 flex justify-between items-center">
                <h3 class="text-xs font-mono text-slate-400 uppercase tracking-widest">{{ editor.title }}</h3>
                <button @click="editor.visible = false" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/10 text-slate-400 hover:text-white transition-all text-xl">×</button>
            </div>
            <div v-if="!editor.isGlobal" class="flex flex-1 overflow-hidden">
                <textarea v-model="editor.content" @input="parseVarsFromYaml" class="flex-1 bg-slate-950/30 p-8 font-mono text-sm text-slate-300 outline-none resize-none border-r border-slate-700/50 leading-relaxed"></textarea>
                <div class="w-96 bg-slate-900/30 p-8 overflow-y-auto">
                    <h4 class="text-[10px] font-black text-slate-500 mb-8 border-b border-slate-700/50 pb-3 uppercase tracking-[0.2em]">Stack Variables</h4>
                    <div v-for="key in editor.detectedKeys" :key="key" class="mb-6">
                        <label class="block text-[10px] font-black text-dm-accent mb-2 uppercase tracking-tighter">{{ key }}</label>
                        <input v-model="editor.localVars[key]" class="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white outline-none focus:border-dm-accent focus:ring-4 focus:ring-dm-accent/10 transition-all" />
                    </div>
                </div>
            </div>
            <div v-else class="flex-1 p-10 overflow-y-auto bg-slate-950/20">
                <div class="max-w-3xl mx-auto">
                    <div v-for="(row, idx) in editor.varList" :key="idx" class="flex gap-4 mb-3 bg-slate-800/40 p-3 rounded-xl border border-slate-700/50">
                       <input v-model="row.key" class="flex-1 bg-transparent text-dm-accent font-mono text-sm outline-none font-bold" placeholder="VARIABLE_NAME"/>
                       <input v-model="row.value" class="flex-1 bg-transparent text-white text-sm outline-none" placeholder="Value"/>
                       <button @click="editor.varList.splice(idx, 1)" class="text-rose-500 px-3 hover:bg-rose-500/10 rounded-lg transition-colors">×</button>
                    </div>
                    <button @click="editor.varList.push({key:'', value:''})" class="mt-6 w-full py-4 border-2 border-dashed border-slate-700 text-slate-500 text-xs font-bold hover:text-white hover:border-slate-500 rounded-xl transition-all uppercase tracking-widest">+ Add New Variable</button>
                </div>
            </div>
            <div class="p-6 bg-slate-800/50 border-t border-slate-700 flex justify-between items-center">
                <button v-if="!editor.isGlobal" @click="handleDeleteStack" class="text-xs font-black text-rose-500 hover:bg-rose-500/10 px-6 py-3 rounded-xl transition-all uppercase tracking-widest">Delete Stack</button>
                <div v-else></div>
                <button @click="saveAll" class="px-10 py-3 bg-dm-accent hover:bg-blue-600 text-white rounded-xl text-xs font-black uppercase tracking-[0.2em] shadow-lg shadow-blue-500/20 transition-all active:scale-95">Save Changes</button>
            </div>
        </div>
    </div>

    <div v-if="logViewer.visible" class="fixed inset-0 bg-slate-950/90 z-[500] flex items-center justify-center p-8 backdrop-blur-xl">
        <div class="w-full max-w-5xl h-full flex flex-col bg-dm-card border border-slate-700 rounded-3xl overflow-hidden shadow-2xl">
            <div class="p-5 bg-slate-800/80 border-b border-slate-700 flex justify-between items-center">
                <span class="text-xs font-black text-dm-accent uppercase tracking-[0.2em]">{{ logViewer.name }} System Logs</span>
                <button @click="logViewer.visible = false" class="text-slate-400 hover:text-white text-2xl">×</button>
            </div>
            <pre class="flex-1 p-8 text-[11px] font-mono text-slate-300 overflow-auto bg-black/20 leading-relaxed">{{ logViewer.content }}</pre>
            <div class="p-5 bg-slate-800/80 border-t border-slate-700 text-right">
                <button @click="showLogs({id: logViewer.currentId, name: logViewer.name})" class="text-xs font-black text-dm-accent px-6 py-3 hover:bg-dm-accent/10 rounded-xl transition-all uppercase tracking-widest">Refresh Logs</button>
            </div>
        </div>
    </div>

    <div v-if="terminal.visible" class="fixed inset-0 bg-slate-950/90 z-[500] flex items-center justify-center p-6 backdrop-blur-md">
        <div class="w-full max-w-4xl h-[65vh] bg-slate-950 border border-slate-800 rounded-3xl flex flex-col overflow-hidden shadow-2xl">
            <div class="p-4 bg-slate-900 border-b border-slate-800 flex justify-between items-center">
                <span class="text-xs font-mono text-dm-accent">{{ terminal.title }}</span>
                <button @click="closeTerminal" class="text-slate-500 hover:text-white text-xl">×</button>
            </div>
            <div ref="terminalElement" class="flex-1 p-6"></div>
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

const isEditMode = ref(false);
const menuOpen = ref(false);
const searchQuery = ref("");
const stacks = ref([]);
const stats = ref({});
const config = ref({ proxy_provider: 'traefik', docker_host_ip: '' });
const editor = reactive({ visible: false, title: '', content: '', stack: '', filename: '', varList: [], isGlobal: false, detectedKeys: [], localVars: {}, globalRaw: '' });
const terminal = reactive({ visible: false, title: '' });
const terminalElement = ref(null);
const logViewer = reactive({ visible: false, name: '', content: '', currentId: '' });
let xterm = null, socket = null;

const anyModalOpen = computed(() => editor.visible || logViewer.visible || terminal.visible);

const getUsage = (id, type) => {
    if (!stats.value[id]) return 0;
    return stats.value[id][type] || 0;
};

const fetchLiveStats = async () => {
    try {
        const res = await axios.get('/api/stacks/stats');
        stats.value = res.data;
    } catch (e) { console.error("Stats error", e); }
};

const filteredStacks = computed(() => {
    if (!searchQuery.value) return stacks.value;
    const q = searchQuery.value.toLowerCase();
    return stacks.value.filter(s => s.name.toLowerCase().includes(q) || s.containers.some(c => c.name.toLowerCase().includes(q)));
});
const filterContainers = (conts) => {
    if (!searchQuery.value) return conts;
    return conts.filter(c => c.name.toLowerCase().includes(searchQuery.value.toLowerCase()));
};

const getIcon = (c) => c.icon || DEFAULT_SVG;
const fetchStacks = async () => { try { const res = await axios.get('/api/stacks'); stacks.value = res.data; } catch (e) { console.error("API error", e); } };

const openContainerUI = (cont) => {
    if (isEditMode.value) return;
    let url = "";
    if (config.value.proxy_provider === 'caddy') {
        const k = Object.keys(cont.labels).find(l => l.startsWith('caddy'));
        if (k) url = `http://${cont.labels[k].split(' ')[0]}`;
    } else {
        const k = Object.keys(cont.labels).find(l => l.includes("rule"));
        if (k && cont.labels[k].includes("Host(")) {
            const m = cont.labels[k].match(/Host\(`([^`]+)`\)/);
            if (m) url = `http://${m[1]}`;
        }
    }
    if (!url) {
        const host = config.value.docker_host_ip || window.location.hostname;
        const portObj = Object.values(cont.ports).find(v => v !== null);
        const port = portObj ? portObj[0].HostPort : 80;
        url = `http://${host}:${port}`;
    }
    window.open(url, '_blank');
};

const parseVarsFromYaml = () => {
    if (editor.isGlobal) return;
    const regex = /\$\{?([a-zA-Z0-9_]+)\}?/g;
    const matches = [...editor.content.matchAll(regex)];
    editor.detectedKeys = [...new Set(matches.map(m => m[1]))];
};

const openEditor = async (s, f) => {
    const [fileRes, envRes] = await Promise.all([axios.get(`/api/stack/${s}/file/${f}`), axios.get('/api/stack/GLOBAL/file/global.env')]);
    editor.isGlobal = false; editor.stack = s; editor.filename = f; editor.content = fileRes.data.content; editor.globalRaw = envRes.data.content;
    const gMap = {};
    envRes.data.content.split('\n').filter(l => l.includes('=')).forEach(l => { const [k, ...v] = l.split('='); gMap[k.trim()] = v.join('=').trim(); });
    parseVarsFromYaml();
    editor.localVars = {}; editor.detectedKeys.forEach(k => { editor.localVars[k] = gMap[k] || "" });
    editor.title = `Project: ${s}`; editor.visible = true;
};

const openGlobalVariables = async () => {
    const res = await axios.get('/api/stack/GLOBAL/file/global.env');
    editor.isGlobal = true; editor.title = "Core Infrastructure Env";
    editor.varList = res.data.content.split('\n').filter(l => l.includes('=')).map(l => {
        const [k, ...v] = l.split('='); return { key: k.trim(), value: v.join('=').trim() };
    });
    editor.visible = true;
};

const saveAll = async () => {
    let gContent = "";
    if (editor.isGlobal) { gContent = editor.varList.map(r => `${r.key}=${r.value}`).join('\n'); }
    else {
        await axios.post(`/api/stack/${editor.stack}/file`, { filename: editor.filename, content: editor.content });
        const currentG = {};
        editor.globalRaw.split('\n').filter(l => l.includes('=')).forEach(l => { const [k, ...v] = l.split('='); currentG[k.trim()] = v.join('=').trim(); });
        gContent = Object.entries({...currentG, ...editor.localVars}).map(([k,v]) => `${k}=${v}`).join('\n');
    }
    await axios.post('/api/stack/GLOBAL/file', { filename: 'global.env', content: gContent });
    editor.visible = false; fetchStacks();
};

const triggerDeploy = (n) => {
    terminal.visible = true; terminal.title = `Initializing Deployment: ${n}`;
    nextTick(() => {
        if (xterm) xterm.dispose();
        xterm = new Terminal({ fontSize: 13, convertEol: true, theme: { background: '#020617', foreground: '#cbd5e1' }, fontFamily: 'monospace' });
        const fit = new FitAddon(); xterm.loadAddon(fit); xterm.open(terminalElement.value); fit.fit();
        socket = new WebSocket(`ws://${window.location.host}/ws/deploy/${n}`);
        socket.onmessage = (e) => xterm.write(e.data);
    });
};

const closeTerminal = () => { if(socket) socket.close(); terminal.visible = false; fetchStacks(); };
const runAction = async (id, action) => { await axios.post(`/api/container/${id}/${action}`); setTimeout(fetchStacks, 1000); };
const showLogs = async (c) => { logViewer.visible = true; logViewer.name = c.name; logViewer.currentId = c.id; logViewer.content = "Streaming logs..."; try { const res = await axios.get(`/api/container/${c.id}/logs`); logViewer.content = res.data.logs; } catch { logViewer.content = "Connection to container lost."; } };
const openCreationModal = async () => { const name = prompt("New Stack Identifier:"); if(name) { await axios.post('/api/stack/create', {name}); fetchStacks(); } };
const handleDeleteStack = async () => { if(confirm('Warning: This action is permanent.')) { await axios.delete(`/api/stack/${editor.stack}`); editor.visible = false; fetchStacks(); } };

onMounted(async () => {
    try { config.value = (await axios.get('/api/config')).data; } catch {}
    fetchStacks(); 
    fetchLiveStats();
    setInterval(fetchLiveStats, 3000); // Live stats every 3s
    setInterval(fetchStacks, 10000); // List refresh every 10s
});
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
body { font-family: 'Inter', sans-serif; margin: 0; background: #111827; -webkit-font-smoothing: antialiased; }
.bg-dm-bg { background: #111827; }
.bg-dm-card { background: #1f2937; }
.text-dm-accent { color: #3b82f6; }
.bg-dm-accent { background: #3b82f6; }

::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #111827; }
::-webkit-scrollbar-thumb { background: #374151; border-radius: 20px; border: 2px solid #111827; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.grid > div { animation: fadeIn 0.4s ease forwards; }
</style>
