#!/usr/bin/env python3
"""
생명나무 HTML에 TTS 읽어주기 기능을 추가하는 패치 스크립트.

사용법:
    python apply_tts_patch.py <원본.html> [출력.html]

출력 파일을 지정하지 않으면 <원본>.with_tts.html 로 저장됩니다.
원본 파일은 변경되지 않습니다.
"""
import sys
import os
import shutil

# ============================================================
# 1) CSS 추가 (</style> 바로 앞에 삽입)
# ============================================================
NEW_CSS = """
/* ===== TTS Reader (읽어주기) ===== */
.tts-reader-overlay{display:none;position:fixed;inset:0;background:rgba(26,20,16,0.55);backdrop-filter:blur(3px);-webkit-backdrop-filter:blur(3px);z-index:2000;align-items:center;justify-content:center;padding:20px;animation:tvOverlayIn 0.2s ease-out}
.tts-reader-overlay.active{display:flex}
.tts-reader-modal{background:var(--paper-card);border-radius:6px;max-width:520px;width:100%;max-height:90vh;display:flex;flex-direction:column;box-shadow:0 18px 50px rgba(0,0,0,0.35);border:1px solid var(--line);border-top:4px solid var(--accent);animation:tvPopIn 0.22s cubic-bezier(.2,.9,.3,1.2);font-family:'Noto Sans KR',sans-serif}
.tts-reader-header{padding:18px 22px 14px;border-bottom:1px dashed var(--line);display:flex;align-items:center;gap:10px;flex-shrink:0}
.tts-reader-icon{flex-shrink:0;color:var(--accent)}
.tts-reader-title{font-family:'Noto Serif KR',serif;font-size:1.05rem;font-weight:700;color:var(--ink);flex:1}
.tts-reader-close{width:30px;height:30px;background:transparent;border:1px solid var(--line);border-radius:50%;color:var(--ink-soft);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:13px}
.tts-reader-close:hover{background:var(--accent);color:var(--paper);border-color:var(--accent)}
.tts-reader-body{padding:14px 22px;overflow-y:auto;flex:1}
.tts-form-label{font-size:10.5px;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:var(--accent);margin-bottom:8px;margin-top:14px;display:block}
.tts-form-label:first-child{margin-top:0}
.tts-voice-select{width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:4px;font-family:inherit;font-size:13px;background:var(--paper);color:var(--ink)}
.tts-api-row{display:flex;gap:8px;align-items:center}
.tts-api-row input{flex:1;padding:9px 11px;border:1px solid var(--line);border-radius:4px;font-family:inherit;font-size:12px;background:var(--paper);color:var(--ink)}
.tts-api-row button{padding:9px 14px;border:1px solid var(--accent);background:var(--accent);color:var(--paper);border-radius:4px;font-size:11px;font-weight:700;letter-spacing:0.06em;cursor:pointer}
.tts-api-row button:hover{background:#6e1622}
.tts-section-list{border:1px solid var(--line-soft);border-radius:4px;background:var(--paper);max-height:240px;overflow-y:auto}
.tts-section-item{display:flex;align-items:flex-start;gap:10px;padding:9px 13px;cursor:pointer;border-bottom:1px solid var(--line-soft);font-size:13px;color:var(--ink-soft);transition:background 0.15s}
.tts-section-item:last-child{border-bottom:none}
.tts-section-item:hover{background:var(--paper-card)}
.tts-section-item.all{font-weight:700;color:var(--ink);background:var(--paper-card)}
.tts-section-item.playing{background:var(--paper-verse);color:var(--accent);font-weight:600}
.tts-section-checkbox{flex-shrink:0;width:15px;height:15px;margin-top:2px;accent-color:var(--accent);cursor:pointer}
.tts-section-label{flex:1;line-height:1.45}
.tts-progress{margin-top:14px;padding:12px 14px;background:var(--paper);border:1px solid var(--line-soft);border-radius:4px;display:none}
.tts-progress.active{display:block}
.tts-progress-bar{height:6px;background:var(--line-soft);border-radius:3px;overflow:hidden}
.tts-progress-fill{height:100%;background:var(--accent);width:0%;transition:width 0.3s}
.tts-progress-text{font-size:12px;color:var(--ink-soft);margin-top:8px;line-height:1.5}
.tts-progress-text strong{color:var(--ink)}
.tts-status{font-size:11.5px;color:var(--ink-mute);margin-top:10px;font-style:italic;line-height:1.5}
.tts-status.error{color:var(--accent);font-style:normal;font-weight:600}
.tts-reader-footer{padding:14px 22px 18px;border-top:1px solid var(--line);display:flex;gap:10px;flex-shrink:0}
.tts-btn{flex:1;padding:11px 16px;border:1px solid var(--line);background:var(--paper);color:var(--ink-soft);border-radius:4px;font-family:'Noto Sans KR',sans-serif;font-size:12.5px;font-weight:700;letter-spacing:0.06em;cursor:pointer;transition:all 0.15s}
.tts-btn:hover:not(:disabled){background:var(--line-soft)}
.tts-btn:disabled{opacity:0.45;cursor:not-allowed}
.tts-btn.primary{background:var(--accent);border-color:var(--accent);color:var(--paper)}
.tts-btn.primary:hover:not(:disabled){background:#6e1622}
@media (max-width:480px){.tts-reader-modal{max-height:95vh}.tts-reader-body{padding:14px 16px}}
"""

# ============================================================
# 2) Topbar 버튼 추가 (font-controls 왼쪽에)
# ============================================================
OLD_TOPBAR = '''<div class="topbar-title">생명나무 · 길·강·나무 · 거듭남의 심기심 · 하나님-사람의 재건축</div>
  <div class="font-controls">'''

NEW_TOPBAR = '''<div class="topbar-title">생명나무 · 길·강·나무 · 거듭남의 심기심 · 하나님-사람의 재건축</div>
  <button class="topbar-btn" onclick="ttsOpenReader()" aria-label="읽어주기"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg></button>
  <div class="font-controls">'''

# ============================================================
# 3) 모달 HTML 추가 (<!-- DASHBOARD --> 바로 앞에 삽입)
# ============================================================
NEW_MODAL = '''  <!-- TTS READER MODAL -->
  <div class="tts-reader-overlay" id="tts-reader-overlay" onclick="ttsCloseOnBg(event)">
    <div class="tts-reader-modal" onclick="event.stopPropagation()">
      <div class="tts-reader-header">
        <svg class="tts-reader-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
        <div class="tts-reader-title">본문 듣기</div>
        <button class="tts-reader-close" onclick="ttsCloseReader()" aria-label="닫기">✕</button>
      </div>
      <div class="tts-reader-body">
        <label class="tts-form-label">API 키</label>
        <div class="tts-api-row">
          <input type="password" id="tts-api-key" placeholder="API 키를 입력하세요" />
          <button onclick="ttsSaveApiKey()">저장</button>
        </div>

        <label class="tts-form-label">음성 선택</label>
        <select class="tts-voice-select" id="tts-voice-select">
          <option value="tk_voice">tk_voice</option>
        </select>

        <label class="tts-form-label">읽을 항목 (기본: 전체 선택)</label>
        <div class="tts-section-list" id="tts-section-list"></div>

        <div class="tts-progress" id="tts-progress">
          <div class="tts-progress-bar">
            <div class="tts-progress-fill" id="tts-progress-fill"></div>
          </div>
          <div class="tts-progress-text" id="tts-progress-text">대기 중...</div>
        </div>

        <div class="tts-status" id="tts-status">서버에서 음성 목록을 불러옵니다...</div>
      </div>
      <div class="tts-reader-footer">
        <button class="tts-btn" id="tts-stop-btn" onclick="ttsStop()" disabled>⏹ 중지</button>
        <button class="tts-btn" id="tts-pause-btn" onclick="ttsTogglePause()" disabled>⏸ 일시정지</button>
        <button class="tts-btn primary" id="tts-play-btn" onclick="ttsPlay()">▶ 재생</button>
      </div>
    </div>
  </div>

  <!-- DASHBOARD -->'''

# ============================================================
# 4) JavaScript 추가 (</script> 바로 앞에 삽입)
# ============================================================
NEW_JS = r"""
// ============================================================
// TTS Reader (Qwen3-TTS MLX 스트리밍)
// ============================================================
const TTS_CONFIG = {
  serverUrl: 'https://qwen.tkhome.cloud',          // 서버 URL (필요시 수정)
  apiKey: localStorage.getItem('qwen_tts_api_key') || '',
  defaultVoice: 'tk_voice',
  sampleRate: 24000,
  pauseSec: 0.4,
  chunkMaxLen: 200
};

const TTS_SECTIONS = [
  { id: 'hero', title: '제목 & 주제' },
  { id: 'todays-verse', title: '오늘의 구절 (갈 2:20)' },
  { id: 'dashboard', title: '메시지 전체 맥락 요약' },
  { id: 'flow', title: '다섯 단계의 흐름' },
  { id: 'acc-0', title: 'Ⅰ. 그리스도 = 생명나무' },
  { id: 'acc-1', title: 'Ⅱ. 요한복음의 모든 방면' },
  { id: 'acc-2', title: 'Ⅲ. 길·강·나무' },
  { id: 'acc-3', title: 'Ⅳ. 영원한 몫 — 달마다 새 열매' },
  { id: 'acc-4', title: 'Ⅴ. 거듭남 — 심기심' },
  { id: 'acc-5', title: 'Ⅵ. 실지 생활 — 두 노선 사이' },
  { id: 'acc-6', title: 'Ⅶ. 욥의 윤리 → 하나님의 영역' },
  { id: 'acc-7', title: 'Ⅷ. 허무심과 재건축' },
  { id: 'acc-8', title: 'Ⅸ. 욥기 42:17 각주' },
  { id: 'recap', title: '전체 복습' },
  { id: 'prayer', title: '기도' }
];

function ttsCleanText(text) {
  if (!text) return '';
  return text.replace(/\s+/g, ' ').replace(/\[[^\]]*\]/g, '').trim();
}

const TTS_EXTRACTORS = {
  'hero': () => {
    const h1 = document.querySelector('#hero-section h1');
    const sub = document.querySelector('#hero-section .hero-sub');
    return ttsCleanText((h1 ? h1.textContent : '') + '. ' + (sub ? sub.textContent : ''));
  },
  'todays-verse': () => {
    const kr = document.querySelector('#todays-verse-section .tv-trans-row.kr .tv-trans-text');
    return '오늘의 구절. 갈라디아서 2장 20절. ' + ttsCleanText(kr ? kr.textContent : '');
  },
  'dashboard': () => {
    const msg = document.querySelector('#dashboard-section .core-message');
    return '메시지 전체 맥락 요약. ' + ttsCleanText(msg ? msg.textContent : '');
  },
  'flow': () => {
    let text = '다섯 단계의 흐름. 생명나무에서 하나님 사람까지. ';
    document.querySelectorAll('#flow-section .flow-step').forEach(s => {
      const label = s.querySelector('.flow-step-label');
      const desc = s.querySelector('.flow-step-desc');
      text += (label ? label.textContent : '') + '. ' + (desc ? desc.textContent : '') + ' ';
    });
    return ttsCleanText(text);
  },
  'recap': () => {
    let text = '전체 메시지 복습. ';
    document.querySelectorAll('#recap-section .recap-anchor').forEach(anchor => {
      const sub = anchor.querySelector('.recap-subtitle');
      if (sub) text += ttsCleanText(sub.textContent.replace(/REVIEW/i, '')) + '. ';
      anchor.querySelectorAll('.recap-item-text').forEach(item => {
        text += ttsCleanText(item.textContent) + '. ';
      });
    });
    const note = document.querySelector('#recap-section .recap-note');
    if (note) text += '이 메시지의 부담. ' + ttsCleanText(note.textContent);
    return text;
  },
  'prayer': () => {
    const heading = document.querySelector('#prayer-section .prayer-heading');
    const callbox = document.querySelector('#prayer-section .prayer-callbox');
    const amen = document.querySelector('#prayer-section .prayer-amen-box');
    let text = '';
    if (heading) text += ttsCleanText(heading.textContent) + '. ';
    if (callbox) text += ttsCleanText(callbox.textContent) + '. ';
    if (amen) {
      const clone = amen.cloneNode(true);
      const sig = clone.querySelector('.prayer-amen-sig');
      if (sig) sig.remove();
      text += ttsCleanText(clone.textContent);
    }
    return text;
  }
};

// 아코디언 항목 추출기 (acc-0 ~ acc-8)
for (let i = 0; i <= 8; i++) {
  const accId = 'acc-' + i;
  TTS_EXTRACTORS[accId] = () => {
    const acc = document.getElementById(accId);
    if (!acc) return '';
    const titleEl = acc.querySelector('.acc-title-text');
    const titleText = titleEl ? titleEl.textContent : '';
    const content = acc.querySelector('.accordion-content');
    if (!content) return ttsCleanText(titleText);
    const clone = content.cloneNode(true);
    clone.querySelectorAll('.verse-block').forEach(v => v.remove());
    return ttsCleanText(titleText + '. ' + clone.textContent);
  };
}

// Audio context 상태
let ttsAudioContext = null;
let ttsNextPlayTime = 0;
let ttsScheduledSources = [];
let ttsCurrentReader = null;
let ttsIsCanceled = false;
let ttsIsPlaying = false;
let ttsIsPaused = false;

function ttsPcmToBuffer(int16Bytes, ctx) {
  const evenLen = int16Bytes.byteLength - (int16Bytes.byteLength % 2);
  if (evenLen === 0) return null;
  const aligned = new Uint8Array(evenLen);
  aligned.set(int16Bytes.subarray(0, evenLen));
  const int16 = new Int16Array(aligned.buffer);
  const float32 = new Float32Array(int16.length);
  for (let i = 0; i < int16.length; i++) float32[i] = int16[i] / 32768;
  const buffer = ctx.createBuffer(1, float32.length, TTS_CONFIG.sampleRate);
  buffer.copyToChannel(float32, 0);
  return buffer;
}

function ttsScheduleBuffer(buffer) {
  if (!buffer || !ttsAudioContext) return;
  const source = ttsAudioContext.createBufferSource();
  source.buffer = buffer;
  source.connect(ttsAudioContext.destination);
  const now = ttsAudioContext.currentTime;
  if (ttsNextPlayTime < now) ttsNextPlayTime = now;
  source.start(ttsNextPlayTime);
  ttsScheduledSources.push(source);
  ttsNextPlayTime += buffer.duration;
  source.onended = () => {
    const idx = ttsScheduledSources.indexOf(source);
    if (idx >= 0) ttsScheduledSources.splice(idx, 1);
  };
}

function ttsStopPlayback() {
  ttsScheduledSources.forEach(src => { try { src.stop(); } catch(e) {} });
  ttsScheduledSources = [];
  ttsNextPlayTime = 0;
}

function ttsOpenReader() {
  document.getElementById('tts-reader-overlay').classList.add('active');
  document.body.style.overflow = 'hidden';
  ttsInitSectionList();
  if (TTS_CONFIG.apiKey) {
    document.getElementById('tts-api-key').value = TTS_CONFIG.apiKey;
  }
  ttsLoadVoices();
}

function ttsCloseReader() {
  if (ttsIsPlaying) {
    if (!confirm('재생 중입니다. 정말 닫으시겠습니까?')) return;
    ttsStop();
  }
  document.getElementById('tts-reader-overlay').classList.remove('active');
  document.body.style.overflow = '';
}

function ttsCloseOnBg(e) {
  if (e.target.id === 'tts-reader-overlay') ttsCloseReader();
}

function ttsSaveApiKey() {
  const input = document.getElementById('tts-api-key');
  TTS_CONFIG.apiKey = input.value.trim();
  localStorage.setItem('qwen_tts_api_key', TTS_CONFIG.apiKey);
  ttsSetStatus(TTS_CONFIG.apiKey ? 'API 키가 저장되었습니다.' : 'API 키가 비워졌습니다.');
  ttsLoadVoices();
}

function ttsInitSectionList() {
  const list = document.getElementById('tts-section-list');
  if (list.dataset.initialized === 'true') return;
  list.innerHTML = '';
  const allItem = document.createElement('label');
  allItem.className = 'tts-section-item all';
  allItem.innerHTML = '<input type="checkbox" class="tts-section-checkbox" id="tts-section-all" checked><span class="tts-section-label">전체 선택 / 해제</span>';
  allItem.querySelector('input').addEventListener('change', function() { ttsToggleAll(this); });
  list.appendChild(allItem);
  TTS_SECTIONS.forEach(sec => {
    const item = document.createElement('label');
    item.className = 'tts-section-item';
    item.dataset.sectionId = sec.id;
    item.innerHTML = '<input type="checkbox" class="tts-section-checkbox" data-section="' + sec.id + '" checked><span class="tts-section-label">' + sec.title + '</span>';
    list.appendChild(item);
  });
  list.dataset.initialized = 'true';
}

function ttsToggleAll(cb) {
  document.querySelectorAll('#tts-section-list input[data-section]').forEach(c => c.checked = cb.checked);
}

async function ttsLoadVoices() {
  const select = document.getElementById('tts-voice-select');
  try {
    const res = await fetch(TTS_CONFIG.serverUrl + '/voices');
    if (!res.ok) throw new Error('서버 응답 ' + res.status);
    const data = await res.json();
    select.innerHTML = '';
    if (!data.voices || data.voices.length === 0) {
      const opt = document.createElement('option');
      opt.textContent = '(등록된 음성 없음)';
      select.appendChild(opt);
      ttsSetStatus('등록된 음성이 없습니다.', true);
      return;
    }
    data.voices.forEach(v => {
      const opt = document.createElement('option');
      opt.value = v.name;
      opt.textContent = v.name + (v.name === data.default ? ' (기본)' : '');
      select.appendChild(opt);
    });
    if (data.default) select.value = data.default;
    ttsSetStatus(data.voices.length + '개 음성 로드 완료. 항목을 선택하고 재생을 누르세요.');
  } catch (e) {
    select.innerHTML = '<option>tk_voice</option>';
    ttsSetStatus('음성 목록 로드 실패: ' + e.message, true);
  }
}

function ttsSetStatus(msg, isError) {
  const el = document.getElementById('tts-status');
  el.textContent = msg;
  el.className = 'tts-status' + (isError ? ' error' : '');
}

function ttsUpdateProgress(current, total, sectionTitle) {
  document.getElementById('tts-progress').classList.add('active');
  document.getElementById('tts-progress-fill').style.width = (current / total * 100) + '%';
  document.getElementById('tts-progress-text').innerHTML = '<strong>' + current + ' / ' + total + '</strong> · ' + sectionTitle;
}

function ttsHighlightSection(sectionId) {
  document.querySelectorAll('#tts-section-list .tts-section-item').forEach(el => el.classList.remove('playing'));
  if (sectionId) {
    const item = document.querySelector('#tts-section-list .tts-section-item[data-section-id="' + sectionId + '"]');
    if (item) item.classList.add('playing');
  }
}

async function ttsPlay() {
  if (!TTS_CONFIG.apiKey) {
    ttsSetStatus('먼저 API 키를 입력하고 저장하세요.', true);
    return;
  }
  const checked = document.querySelectorAll('#tts-section-list input[data-section]:checked');
  if (checked.length === 0) {
    ttsSetStatus('읽을 항목을 하나 이상 선택하세요.', true);
    return;
  }
  const voice = document.getElementById('tts-voice-select').value;
  const selectedIds = Array.from(checked).map(cb => cb.dataset.section);
  const sectionsToRead = TTS_SECTIONS.filter(s => selectedIds.includes(s.id));

  ttsIsCanceled = false;
  ttsIsPlaying = true;
  document.getElementById('tts-play-btn').disabled = true;
  document.getElementById('tts-stop-btn').disabled = false;
  document.getElementById('tts-pause-btn').disabled = false;

  if (!ttsAudioContext || ttsAudioContext.state === 'closed') {
    const Ctor = window.AudioContext || window.webkitAudioContext;
    try {
      ttsAudioContext = new Ctor({ sampleRate: TTS_CONFIG.sampleRate });
    } catch (e) {
      ttsAudioContext = new Ctor();
    }
  }
  if (ttsAudioContext.state === 'suspended') await ttsAudioContext.resume();
  ttsIsPaused = false;
  ttsUpdatePauseBtn();

  ttsStopPlayback();

  try {
    for (let i = 0; i < sectionsToRead.length; i++) {
      if (ttsIsCanceled) break;
      const sec = sectionsToRead[i];
      const extractor = TTS_EXTRACTORS[sec.id];
      if (!extractor) continue;
      ttsUpdateProgress(i + 1, sectionsToRead.length, sec.title);
      ttsHighlightSection(sec.id);
      ttsSetStatus('재생 중: ' + sec.title);
      const text = extractor();
      if (!text || text.trim().length < 2) continue;
      await ttsStreamText(text, voice);
      if (ttsIsCanceled) break;
    }
    while (!ttsIsCanceled) {
      if (ttsAudioContext.state === 'suspended') {
        await new Promise(r => setTimeout(r, 200));
        continue;
      }
      const remaining = ttsNextPlayTime - ttsAudioContext.currentTime;
      if (remaining <= 0) break;
      ttsSetStatus('재생 마무리 중... (남은 ' + remaining.toFixed(1) + '초)');
      await new Promise(r => setTimeout(r, Math.min(remaining * 1000 + 200, 1000)));
    }
    if (!ttsIsCanceled) ttsSetStatus('✅ 모든 항목 재생 완료');
    else ttsSetStatus('⏹ 중지됨');
  } catch (e) {
    ttsSetStatus('❌ 오류: ' + e.message, true);
  } finally {
    ttsIsPlaying = false;
    ttsIsPaused = false;
    ttsHighlightSection(null);
    document.getElementById('tts-play-btn').disabled = false;
    document.getElementById('tts-stop-btn').disabled = true;
    document.getElementById('tts-pause-btn').disabled = true;
    ttsUpdatePauseBtn();
    ttsCurrentReader = null;
  }
}

async function ttsStreamText(text, voice) {
  const res = await fetch(TTS_CONFIG.serverUrl + '/tts/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': TTS_CONFIG.apiKey
    },
    body: JSON.stringify({
      text: text,
      voice: voice,
      pause_sec: TTS_CONFIG.pauseSec,
      chunk_max_len: TTS_CONFIG.chunkMaxLen
    })
  });
  if (!res.ok) {
    let errMsg = 'HTTP ' + res.status;
    try { const err = await res.json(); errMsg = err.detail || errMsg; } catch(e) {}
    throw new Error(errMsg);
  }
  const reader = res.body.getReader();
  ttsCurrentReader = reader;
  let buffer = new Uint8Array(0);
  const MIN_DECODE = 24000;
  while (true) {
    let done, value;
    try { ({ done, value } = await reader.read()); }
    catch (e) { if (ttsIsCanceled) break; throw e; }
    if (done || ttsIsCanceled) {
      if (buffer.length >= 2 && !ttsIsCanceled) {
        ttsScheduleBuffer(ttsPcmToBuffer(buffer, ttsAudioContext));
      }
      break;
    }
    const merged = new Uint8Array(buffer.length + value.length);
    merged.set(buffer);
    merged.set(value, buffer.length);
    buffer = merged;
    while (buffer.length >= MIN_DECODE && !ttsIsCanceled) {
      const evenLen = MIN_DECODE - (MIN_DECODE % 2);
      const audioBuffer = ttsPcmToBuffer(buffer.subarray(0, evenLen), ttsAudioContext);
      if (audioBuffer) ttsScheduleBuffer(audioBuffer);
      buffer = buffer.subarray(evenLen);
    }
  }
}

async function ttsStop() {
  ttsIsCanceled = true;
  if (ttsCurrentReader) { try { await ttsCurrentReader.cancel(); } catch(e) {} ttsCurrentReader = null; }
  ttsStopPlayback();
  if (ttsAudioContext && ttsAudioContext.state === 'suspended') {
    try { await ttsAudioContext.resume(); } catch(e) {}
  }
  ttsIsPaused = false;
  ttsSetStatus('⏹ 중지됨');
  document.getElementById('tts-play-btn').disabled = false;
  document.getElementById('tts-stop-btn').disabled = true;
  document.getElementById('tts-pause-btn').disabled = true;
  ttsUpdatePauseBtn();
  ttsIsPlaying = false;
  ttsHighlightSection(null);
}

async function ttsTogglePause() {
  if (!ttsIsPlaying || !ttsAudioContext) return;
  if (ttsIsPaused) {
    try { await ttsAudioContext.resume(); } catch(e) {}
    ttsIsPaused = false;
    ttsSetStatus('▶ 재생 재개됨');
  } else {
    try { await ttsAudioContext.suspend(); } catch(e) {}
    ttsIsPaused = true;
    ttsSetStatus('⏸ 일시정지됨');
  }
  ttsUpdatePauseBtn();
}

function ttsUpdatePauseBtn() {
  const btn = document.getElementById('tts-pause-btn');
  if (!btn) return;
  btn.textContent = ttsIsPaused ? '▶ 계속' : '⏸ 일시정지';
}
"""

# ============================================================
# 패치 적용
# ============================================================
def apply_patch(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        html = f.read()

    original_size = len(html)
    print(f"📂 원본 읽음: {input_path} ({original_size:,} bytes)")

    # 이미 패치되어 있는지 확인
    if 'tts-reader-overlay' in html or 'TTS_CONFIG' in html:
        print("⚠️  이 파일에는 이미 TTS 패치가 적용되어 있습니다.")
        ans = input("덮어쓰기를 진행하시겠습니까? (y/N): ").strip().lower()
        if ans != 'y':
            print("취소됨.")
            return False

    # 1) CSS 삽입 (</style> 앞에)
    if '</style>' not in html:
        raise RuntimeError("'</style>' 태그를 찾을 수 없습니다.")
    html = html.replace('</style>', NEW_CSS + '\n</style>', 1)
    print("✅ CSS 추가됨")

    # 2) Topbar 버튼 추가
    if OLD_TOPBAR not in html:
        raise RuntimeError("Topbar 앵커를 찾을 수 없습니다. HTML 구조가 예상과 다릅니다.")
    html = html.replace(OLD_TOPBAR, NEW_TOPBAR, 1)
    print("✅ 상단바 버튼 추가됨")

    # 3) 모달 HTML 삽입 (<!-- DASHBOARD --> 앞에)
    if '  <!-- DASHBOARD -->' not in html:
        raise RuntimeError("'<!-- DASHBOARD -->' 앵커를 찾을 수 없습니다.")
    html = html.replace('  <!-- DASHBOARD -->', NEW_MODAL, 1)
    print("✅ 모달 HTML 추가됨")

    # 4) JavaScript 추가 (</script> 앞에)
    # 마지막 </script>가 메인 스크립트의 끝
    last_script_end = html.rfind('</script>')
    if last_script_end == -1:
        raise RuntimeError("'</script>' 태그를 찾을 수 없습니다.")
    html = html[:last_script_end] + NEW_JS + '\n' + html[last_script_end:]
    print("✅ JavaScript 추가됨")

    new_size = len(html)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n📦 출력: {output_path} ({new_size:,} bytes, +{new_size - original_size:,})")
    return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f"❌ 파일을 찾을 수 없습니다: {input_path}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        base, ext = os.path.splitext(input_path)
        output_path = base + '.with_tts' + ext

    print("=" * 60)
    print("  TTS 읽어주기 기능 패치")
    print("=" * 60)

    try:
        ok = apply_patch(input_path, output_path)
        if ok:
            print("\n🎉 완료! 브라우저에서 출력 파일을 열어보세요.")
            print(f"   open {output_path}")
            print("\n💡 사용법:")
            print("   1. 우측 상단의 🔊 스피커 아이콘 클릭")
            print("   2. API 키 입력 → 저장 (한 번만, localStorage에 저장됨)")
            print("   3. 음성과 항목 선택 → ▶ 재생")
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
