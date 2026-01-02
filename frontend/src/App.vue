<template>
  <div class="min-h-screen font-sans bg-dm-bg text-slate-200">
    <div v-if="!isLoggedIn" class="fixed inset-0 bg-dm-bg flex items-center justify-center p-6 z-[9999]">
      <div class="w-full max-w-md bg-dm-card border border-slate-700/50 rounded-3xl p-8 shadow-2xl animate-in">
        <div class="text-center mb-8">
          <div class="w-16 h-16 bg-dm-accent/10 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-dm-accent/20">
            <span class="text-4xl">⚓</span>
          </div>
          <h2 class="text-3xl font-black text-white tracking-tighter">DockMaster</h2>
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

    <div v-else @click="closeAllMenus" class="min-h-screen">
      <header class="sticky top-0 z-[1000] bg-dm-bg/80 backdrop-blur-md border-b border-slate-700/30 px-3 md:px-6 py-4">
        <div class="max-w-[1600px] mx-auto flex items-center justify-between gap-3 md:gap-6">
          
          <h1 class="flex items-center gap-2 shrink-0 tracking-tighter cursor-pointer" @click="fetchStacks">
            <span class="text-2xl md:text-4xl text-dm-accent drop-shadow-[0_0_10px_rgba(59,130,246,0.5)]">⚓</span>
            <span class="hidden sm:block text-xl md:text-3xl font-black text-white">DockMaster</span>
          </h1>

          <div class="flex-1 max-w-xl relative">
            <input v-model="searchQuery" type="text" placeholder="Search..." class="w-full h-10 md:h-11 bg-dm-card/50 border border-slate-700/50 rounded-xl px-10 text-xs text-white outline-none focus:border-dm-accent transition-all placeholder:text-slate-600" />
            <span class="absolute left-3.5 top-2.5 md:top-3 opacity-30 text-xs">🔍</span>
          </div>

          <div class="hidden xl:flex items-center gap-6 px-6 border-x border-slate-700/30">
             <div v-for="(val, key) in sysStats" :key="key" class="flex flex-col items-center">
                <span class="text-[9px] font-black text-slate-500 uppercase tracking-widest">{{ key }}</span>
                <span class="text-xs font-bold text-white">{{ val }}{{ key === 'temp' ? '°' : '%' }}</span>
             </div>
          </div>

          <div class="flex items-center gap-2 md:gap-4 shrink-0">
            <button @click.stop="showHidden = !showHidden" class="w-10 h-10 md:w-11 md:h-11 flex items-center justify-center rounded-xl border border-slate-700/50 transition-all" :class="showHidden ? 'bg-amber-500/10 border-amber-500/50 text-amber-500' : 'bg-slate-800/30 text-slate-500 hover:text-slate-300'">
               <svg v-if="showHidden" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
               <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
            </button>

            <button @click.stop="menuOpen = !menuOpen" class="w-10 h-10 md:w-11 md:h-11 flex flex-col items-center justify-center gap-1.5 bg-slate-800/50 border border-slate-700/50 rounded-xl transition-all" :class="isEditMode ? 'border-dm-accent' : ''">
              <div class="w-5 h-0.5 bg-slate-300 rounded-full"></div>
              <div class="w-5 h-0.5 bg-slate-300 rounded-full"></div>
              <div class="w-5 h-0.5 bg-slate-300 rounded-full"></div>
            </button>
          </div>
        </div>

        <transition name="menu-fade">
          <div v-if="menuOpen" @click.stop class="absolute right-3 md:right-6 top-16 md:top-24 z-[1001]">
            <div class="bg-dm-card border border-slate-700 rounded-2xl shadow-2xl w-60 overflow-hidden">
              <div class="xl:hidden p-4 bg-slate-900/40 border-b border-slate-700/30 flex justify-around">
                <div v-for="(val, key) in sysStats" :key="'mob'+key" class="text-center">
                    <div class="text-[8px] font-black text-slate-500 uppercase">{{ key }}</div>
                    <div class="text-[10px] font-bold text-white">{{ val }}{{ key === 'temp' ? '°' : '%' }}</div>
                </div>
              </div>

              <div @click="isEditMode = !isEditMode" class="flex items-center justify-between p-4 hover:bg-white/[0.02] cursor-pointer transition-colors">
                <span class="text-[10px] font-black uppercase text-slate-400" :class="isEditMode ? 'text-dm-accent' : ''">Edit Mode</span>
                <div class="relative h-5 w-10 rounded-full bg-slate-700" :class="isEditMode ? 'bg-dm-accent' : ''">
                  <span class="absolute h-4 w-4 bg-white rounded-full transition-all mt-0.5 ml-0.5" :class="isEditMode ? 'translate-x-5' : ''"></span>
                </div>
              </div>
              <template v-if="isEditMode">
                <div @click="openGlobalVariables(); menuOpen = false" class="flex items-center justify-between p-4 hover:bg-white/[0.02] cursor-pointer border-t border-slate-700/30">
                  <span class="text-[10px] font-black uppercase text-slate-300">Global Registry</span>
                  <span>⚙️</span>
                </div>
                <div @click="openCreationModal(); menuOpen = false" class="flex items-center justify-between p-4 hover:bg-emerald-500/5 cursor-pointer border-t border-slate-700/30">
                  <span class="text-[10px] font-black uppercase text-emerald-400">New Stack</span>
                  <span class="text-emerald-400">+</span>
                </div>
              </template>
              <div @click="logout" class="flex items-center justify-between p-4 hover:bg-rose-500/5 cursor-pointer border-t border-slate-700/30">
                <span class="text-[10px] font-black uppercase text-rose-500">Logout</span>
              </div>
            </div>
          </div>
        </transition>
      </header>

      <div class="max-w-[1600px] mx-auto p-4 md:p-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6 pb-20">
        <template v-for="stack in filteredStacks" :key="stack.name">
          <div v-if="(stack.status === 'Running' && !stack.hidden) || showHidden" class="bg-dm-card rounded-2xl p-5 border border-slate-700/50 flex flex-col shadow-lg animate-in" :class="stack.status !== 'Running' || stack.hidden ? 'opacity-50 grayscale border-dashed' : ''">
            <div class="flex justify-between items-start mb-5">
              <div class="truncate">
                <h2 class="text-base font-black text-white truncate tracking-tight flex items-center gap-2 capitalize">
                    {{ stack.name }}
                    <span v-if="stack.status !== 'Running'" class="text-[9px] bg-rose-500/20 text-rose-500 px-1.5 rounded uppercase font-bold">Stopped</span>
                    <span v-else-if="stack.hidden" class="text-[9px] bg-amber-500/20 text-amber-500 px-1.5 rounded uppercase font-bold">Hidden</span>
                </h2>
                <div class="flex items-center gap-1.5 mt-1">
                  <span class="w-1.5 h-1.5 rounded-full" :class="stack.status === 'Running' ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-rose-500'"></span>
                  <span class="text-[10px] font-bold uppercase text-slate-500">{{ stack.status }}</span>
                </div>
              </div>
              <div v-if="isEditMode" class="relative">
                <button @click.stop="activeStackMenu = activeStackMenu === stack.name ? null : stack.name" class="w-8 h-8 flex items-center justify-center text-slate-500 rounded-lg bg-slate-800/30 border border-slate-700/30">⋮</button>
                <div v-if="activeStackMenu === stack.name" class="absolute right-0 top-full mt-2 z-[200] bg-dm-card border border-slate-700 rounded-xl shadow-2xl py-1 w-44 overflow-hidden animate-in">
                  <button @click="openEditor(stack.name, 'docker-compose.yml'); activeStackMenu = null" class="w-full text-left px-4 py-2.5 text-[10px] font-bold text-white hover:bg-white/10 uppercase">Edit Stack</button>
                  <button @click="toggleStackVisibility(stack); activeStackMenu = null" class="w-full text-left px-4 py-2.5 text-[10px] font-bold text-amber-400 hover:bg-white/10 uppercase">{{ stack.hidden ? 'Unhide' : 'Hide' }}</button>
                  <button @click="triggerDeploy(stack.name); activeStackMenu = null" class="w-full text-left px-4 py-2.5 text-[10px] font-bold text-emerald-400 hover:bg-emerald-500/10 uppercase border-t border-slate-700/30">Deploy</button>
                  <button @click="triggerDown(stack.name); activeStackMenu = null" class="w-full text-left px-4 py-2.5 text-[10px] font-bold text-rose-500 hover:bg-rose-500/10 uppercase">Down</button>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-3 gap-3">
              <template v-for="cont in stack.containers" :key="cont.id">
                <div v-if="(cont.status === 'running' && !cont.hidden) || showHidden" class="relative group aspect-square bg-slate-900/50 border border-slate-700/30 rounded-2xl flex flex-col items-center justify-center p-2 hover:border-dm-accent transition-all" :class="cont.status !== 'running' || cont.hidden ? 'opacity-40 grayscale border-dashed' : ''">
                  <div class="absolute top-2 left-2 w-1.5 h-1.5 rounded-full" :class="cont.status === 'running' ? 'bg-emerald-500' : 'bg-rose-500'"></div>
                  
                  <div v-if="isEditMode" class="absolute top-1 right-1">
                      <button @click.stop="activeDropdown = activeDropdown === cont.id ? null : cont.id" class="w-6 h-6 flex items-center justify-center text-slate-600">⋮</button>
                      <div v-if="activeDropdown === cont.id" class="absolute right-0 top-full z-[300] mt-1 bg-dm-card border border-slate-700 rounded-xl py-1 w-32 shadow-2xl overflow-hidden animate-in">
                        <button @click="openMetadataEditor(cont)" class="w-full text-left px-3 py-2 text-[9px] font-bold text-amber-400 hover:bg-white/5 uppercase">Config</button>
                        <button @click="toggleContainerVisibility(cont)" class="w-full text-left px-3 py-2 text-[9px] font-bold text-slate-400 hover:bg-white/5 uppercase">{{ cont.hidden ? 'Unhide' : 'Hide' }}</button>
                        <button @click="triggerLogs(cont)" class="w-full text-left px-3 py-2 text-[9px] font-bold text-dm-accent hover:bg-white/5 uppercase">Logs</button>
                        <button @click="runAction(cont.id, cont.status === 'running' ? 'stop' : 'start')" class="w-full text-left px-3 py-2 text-[9px] font-bold uppercase" :class="cont.status === 'running' ? 'text-rose-400' : 'text-emerald-400'">{{ cont.status === 'running' ? 'Stop' : 'Start' }}</button>
                      </div>
                  </div>

                  <div @click="openContainerUI(cont)" class="w-12 h-12 mb-2 cursor-pointer transition-transform hover:scale-110">
                      <img :src="getIconUrl(cont)" @error="handleIconError" class="w-full h-full object-contain" />
                  </div>
                  <span @click="openContainerUI(cont)" class="text-[10px] font-bold text-slate-300 text-center truncate w-full px-1 cursor-pointer capitalize">{{ cont.display_name || cont.name }}</span>
                </div>
              </template>
            </div>
          </div>
        </template>
      </div>

      <div v-if="editor.visible" class="fixed inset-0 bg-slate-950/80 z-[5000] flex items-center justify-center p-0 md:p-8 backdrop-blur-md">
        <div class="w-full h-full max-w-6xl bg-dm-card border-t md:border border-slate-700/50 md:rounded-3xl flex flex-col shadow-2xl overflow-hidden animate-in">
            <div class="h-16 px-6 bg-slate-800/20 border-b border-slate-700/50 flex justify-between items-center shrink-0">
                <div class="flex items-center gap-3">
                  <span class="text-xs font-black text-dm-accent uppercase tracking-tighter capitalize">{{ editor.isGlobal ? 'Global Registry' : editor.stack }}</span>
                  <div v-if="!editor.isGlobal" class="lg:hidden flex bg-slate-950/50 p-1 rounded-lg border border-slate-700/50">
                      <button @click="activeEditorTab = 'code'" class="px-3 py-1 text-[9px] font-black uppercase rounded-md transition-all" :class="activeEditorTab === 'code' ? 'bg-dm-accent text-white' : 'text-slate-500'">YAML</button>
                      <button @click="activeEditorTab = 'env'" class="px-3 py-1 text-[9px] font-black uppercase rounded-md transition-all" :class="activeEditorTab === 'env' ? 'bg-dm-accent text-white' : 'text-slate-500'">ENV</button>
                  </div>
                </div>
                <button @click="editor.visible = false" class="text-slate-400 text-2xl px-2">&times;</button>
            </div>
            <div class="flex-1 overflow-hidden relative">
                <div v-if="editor.isGlobal" class="h-full overflow-y-auto p-6 scroll-custom">
                    <div v-for="(val, id) in globalVarsObj" :key="id" class="flex items-center gap-2 mb-3">
                        <input v-model="globalVarKeys[id]" placeholder="KEY" class="w-1/3 h-11 bg-slate-950 border border-slate-700 rounded-xl px-4 text-xs font-mono text-dm-accent outline-none" />
                        <input v-model="globalVarsObj[id]" placeholder="value" class="flex-1 h-11 bg-slate-950 border border-slate-700 rounded-xl px-4 text-xs text-white outline-none" />
                        <button @click="deleteVariable(id)" class="text-rose-500/40 hover:text-rose-500 px-2">🗑</button>
                    </div>
                    <button @click="addNewVariable" class="mt-4 w-full h-11 border border-dashed border-slate-700 rounded-xl text-[10px] font-black uppercase text-slate-500 hover:border-dm-accent transition-all">+ Add Variable</button>
                </div>
                <div v-else class="h-full flex flex-col lg:flex-row">
                    <div class="flex-1 h-full overflow-hidden" :class="activeEditorTab === 'code' ? 'flex' : 'hidden lg:flex'">
                        <textarea v-model="editor.content" @input="debounceParse" spellcheck="false" class="w-full h-full bg-transparent p-6 font-mono text-[11px] md:text-xs text-slate-300 outline-none resize-none whitespace-pre overflow-auto scroll-custom"></textarea>
                    </div>
                    <div class="w-full lg:w-80 h-full bg-slate-900/30 border-l border-slate-700/30 flex flex-col" :class="activeEditorTab === 'env' ? 'flex' : 'hidden lg:flex'">
                        <div class="p-4 border-b border-slate-700/20 bg-slate-800/10 text-center">
                            <span class="text-[10px] font-black text-slate-500 uppercase">Variable Inspector</span>
                        </div>
                        <div class="flex-1 overflow-y-auto p-6 scroll-custom">
                            <div v-for="(val, key) in parsedVars" :key="key" class="mb-5">
                                <label class="text-[10px] font-mono font-bold text-slate-400">{{ key }}</label>
                                <input v-model="parsedVars[key]" class="w-full h-10 bg-slate-950 border border-slate-700 rounded-lg px-3 text-xs text-white mt-1 outline-none focus:border-dm-accent transition-all" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="p-6 bg-slate-800/20 border-t border-slate-700/50 flex items-center justify-between gap-4 shrink-0">
                <button v-if="!editor.isGlobal" @click="deleteStackConfirm(editor.stack)" class="h-12 px-6 bg-rose-500/10 text-rose-500 rounded-2xl text-[11px] font-black uppercase">Delete</button>
                <button @click="saveSmartFile" class="flex-1 h-12 bg-dm-accent text-white rounded-2xl text-[11px] font-black uppercase shadow-lg shadow-dm-accent/20">Save & Sync</button>
            </div>
        </div>
      </div>

      <div v-if="terminal.visible" class="fixed inset-0 bg-slate-950/90 z-[6000] flex items-center justify-center p-4 backdrop-blur-xl">
          <div class="w-full max-w-4xl h-[70vh] bg-black border border-slate-700/50 rounded-3xl flex flex-col overflow-hidden animate-in">
              <div class="h-14 px-6 bg-slate-900/50 border-b border-white/5 flex justify-between items-center">
                  <span class="text-[10px] font-black uppercase text-slate-400">{{ terminal.title }}</span>
                  <button @click="closeTerminal" class="text-slate-500 hover:text-white transition-colors text-xl">&times;</button>
              </div>
              <div ref="terminalElement" class="flex-1 p-4 bg-black overflow-hidden"></div>
          </div>
      </div>

      <div v-if="metadataModal.visible" class="fixed inset-0 bg-slate-950/80 z-[5000] flex items-center justify-center p-4 backdrop-blur-md">
          <div class="w-full max-w-md bg-dm-card border border-slate-700/50 rounded-3xl p-8 shadow-2xl animate-in">
              <h3 class="text-lg font-black text-white mb-6 uppercase tracking-tight">Container Settings</h3>
              <div class="space-y-4">
                  <div>
                      <label class="text-[10px] font-black text-slate-500 uppercase">Display Name</label>
                      <input v-model="metadataModal.displayName" class="w-full h-12 bg-slate-950 border border-slate-700 rounded-xl px-4 text-white mt-1 outline-none focus:border-dm-accent" />
                  </div>
                  <div>
                      <label class="text-[10px] font-black text-slate-500 uppercase">Icon URL</label>
                      <input v-model="metadataModal.iconUrl" placeholder="https://..." class="w-full h-12 bg-slate-950 border border-slate-700 rounded-xl px-4 text-white mt-1 outline-none focus:border-dm-accent" />
                  </div>
              </div>
              <div class="flex gap-3 mt-8">
                  <button @click="metadataModal.visible = false" class="flex-1 h-12 bg-slate-800 text-slate-300 rounded-xl font-black uppercase text-[11px]">Cancel</button>
                  <button @click="saveMetadata" class="flex-1 h-12 bg-dm-accent text-white rounded-xl font-black uppercase text-[11px]">Save</button>
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
const WS_PROTOCOL = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_HOST = window.location.host;

const isLoggedIn = ref(false), loginPass = ref(""), loginError = ref(""), loading = ref(false);
const isEditMode = ref(false), menuOpen = ref(false), showHidden = ref(false), searchQuery = ref(""), stacks = ref([]), sysStats = ref({});
const activeDropdown = ref(null), activeStackMenu = ref(null), activeEditorTab = ref('code');
const editor = reactive({ visible: false, content: '', secondaryContent: '', stack: '', filename: '', isGlobal: false });
const metadataModal = reactive({ visible: false, containerId: null, displayName: '', iconUrl: '' });
const terminal = reactive({ visible: false, title: '' }), terminalElement = ref(null);
const parsedVars = ref({}), globalVarsObj = ref({}), globalVarKeys = ref({});
let xterm, socket, fitAddon, parseTimer;

axios.interceptors.request.use(c => {
  const t = localStorage.getItem('dm_token');
  if (t) c.headers.Authorization = `Bearer ${t}`;
  return c;
});

const getIconUrl = (cont) => {
    if (cont.icon && cont.icon.startsWith('http')) return cont.icon;
    const cleanName = cont.name.split(/[-_]/)[0].toLowerCase();
    return `https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/${cleanName}.png`;
};
const handleIconError = (e) => { e.target.src = DEFAULT_SVG; };

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

const filteredStacks = computed(() => {
  const query = searchQuery.value.toLowerCase().trim();
  let base = stacks.value;
  if (query) {
    base = base.map(stack => {
      const stackMatch = stack.name.toLowerCase().includes(query);
      const matchingContainers = stack.containers.filter(cont => 
        cont.name.toLowerCase().includes(query) || (cont.display_name && cont.display_name.toLowerCase().includes(query))
      );
      if (stackMatch || matchingContainers.length > 0) {
        return { ...stack, containers: stackMatch ? stack.containers : matchingContainers };
      }
      return null;
    }).filter(s => s !== null);
  }
  return base;
});

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
    editor.stack = sn; editor.filename = fn; editor.isGlobal = false;
    editor.visible = true; activeEditorTab.value = 'code'; debounceParse();
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

const toggleStackVisibility = async (stack) => { await axios.post(`/api/stack/${stack.name}/metadata`, { hidden: !stack.hidden }); fetchStacks(); };
const toggleContainerVisibility = async (cont) => { await axios.post(`/api/container/${cont.id}/metadata`, { hidden: !cont.hidden }); fetchStacks(); };
const deleteStackConfirm = async (sn) => { if(confirm(`Delete stack: ${sn}?`)) { await axios.delete(`/api/stack/${sn}`); editor.visible = false; fetchStacks(); } };

const openMetadataEditor = (c) => {
    metadataModal.containerId = c.id;
    metadataModal.displayName = c.display_name || c.name;
    metadataModal.iconUrl = c.icon || '';
    metadataModal.visible = true; activeDropdown.value = null;
};

const saveMetadata = async () => {
    await axios.post(`/api/container/${metadataModal.containerId}/metadata`, { display_name: metadataModal.displayName, icon: metadataModal.iconUrl });
    metadataModal.visible = false; fetchStacks();
};

const openContainerUI = (c) => {
    if (c.url) window.open(c.url, '_blank');
    else {
        const p = Object.values(c.ports).find(v => v !== null)?.[0]?.HostPort;
        window.open(`${window.location.protocol}//${window.location.hostname}${p ? ':' + p : ''}`, '_blank');
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

const triggerLogs = (c) => { setupTerminal(`Logs: ${c.name}`); socket = new WebSocket(`${WS_PROTOCOL}//${WS_HOST}/ws/logs/${c.id}?token=${localStorage.getItem('dm_token')}`); socket.onmessage = (e) => xterm.write(e.data); };
const triggerDeploy = (n) => { setupTerminal(`Deploying: ${n}`); socket = new WebSocket(`${WS_PROTOCOL}//${WS_HOST}/ws/deploy/${n}?token=${localStorage.getItem('dm_token')}`); socket.onmessage = (e) => xterm.write(e.data); socket.onclose = () => fetchStacks(); };
const triggerDown = (n) => { if(confirm(`Down stack ${n}?`)) { setupTerminal(`Stopping: ${n}`); socket = new WebSocket(`${WS_PROTOCOL}//${WS_HOST}/ws/down/${n}?token=${localStorage.getItem('dm_token')}`); socket.onmessage = (e) => xterm.write(e.data); socket.onclose = () => fetchStacks(); } };
const closeTerminal = () => { if(socket) socket.close(); terminal.visible = false; fetchStacks(); };
const runAction = async (id, a) => { await axios.post(`/api/container/${id}/${a}`); setTimeout(fetchStacks, 1000); };
const openCreationModal = async () => { const n = prompt("New Stack Name:"); if(n) { await axios.post('/api/stack/create', { name: n }); fetchStacks(); } };
const closeAllMenus = () => { menuOpen.value = false; activeDropdown.value = null; activeStackMenu.value = null; };
const addNewVariable = () => { const id = Math.random().toString(36).substr(2, 9); globalVarKeys.value[id] = ""; globalVarsObj.value[id] = ""; };
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
.capitalize { text-transform: capitalize; }
.animate-in { animation: s 0.3s ease-out; }
@keyframes s { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.scroll-custom::-webkit-scrollbar { width: 8px; height: 8px; }
.scroll-custom::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.05); border-radius: 4px; }
.menu-fade-enter-active, .menu-fade-leave-active { transition: opacity 0.2s, transform 0.2s; }
.menu-fade-enter-from, .menu-fade-leave-to { opacity: 0; transform: scale(0.95); }
</style>
