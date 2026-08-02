/**
 * AI Support Platform — Embeddable Chat Widget
 * Usage: <script src="https://your-domain.com/widget.js" data-api-key="sk_xxx"></script>
 */
(function () {
  const API_KEY = document.currentScript?.getAttribute('data-api-key') || '';
  const API_BASE = document.currentScript?.getAttribute('data-api-url') || 'http://localhost:8000';

  let sessionId = null;
  let isOpen = false;

  const styles = `
    #ai-support-widget * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    #ai-support-bubble {
      position: fixed; bottom: 24px; right: 24px; z-index: 99999;
      width: 56px; height: 56px; border-radius: 50%;
      background: #2563eb; border: none; cursor: pointer;
      box-shadow: 0 4px 20px rgba(37,99,235,0.4);
      display: flex; align-items: center; justify-content: center;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    #ai-support-bubble:hover { transform: scale(1.08); box-shadow: 0 6px 24px rgba(37,99,235,0.5); }
    #ai-support-bubble svg { width: 26px; height: 26px; fill: white; }
    #ai-support-window {
      position: fixed; bottom: 90px; right: 24px; z-index: 99998;
      width: 360px; height: 520px; background: white;
      border-radius: 16px; box-shadow: 0 8px 40px rgba(0,0,0,0.18);
      display: flex; flex-direction: column; overflow: hidden;
      transform: scale(0.95) translateY(10px); opacity: 0;
      transition: transform 0.2s, opacity 0.2s;
      pointer-events: none;
    }
    #ai-support-window.open { transform: scale(1) translateY(0); opacity: 1; pointer-events: all; }
    #ai-support-header {
      background: #2563eb; padding: 16px 20px;
      display: flex; align-items: center; gap: 10px;
    }
    #ai-support-header-icon {
      width: 36px; height: 36px; background: rgba(255,255,255,0.2);
      border-radius: 50%; display: flex; align-items: center; justify-content: center;
    }
    #ai-support-header-icon svg { width: 18px; height: 18px; fill: white; }
    #ai-support-header-text h3 { color: white; font-size: 14px; font-weight: 600; margin: 0; }
    #ai-support-header-text p { color: rgba(255,255,255,0.75); font-size: 11px; margin: 2px 0 0; }
    #ai-support-messages {
      flex: 1; overflow-y: auto; padding: 16px; display: flex;
      flex-direction: column; gap: 10px; background: #f8fafc;
    }
    .ai-msg { display: flex; flex-direction: column; max-width: 85%; }
    .ai-msg.user { align-self: flex-end; align-items: flex-end; }
    .ai-msg.bot { align-self: flex-start; align-items: flex-start; }
    .ai-msg-bubble {
      padding: 10px 14px; border-radius: 16px; font-size: 13px; line-height: 1.5;
    }
    .ai-msg.user .ai-msg-bubble { background: #2563eb; color: white; border-radius: 16px 16px 4px 16px; }
    .ai-msg.bot .ai-msg-bubble { background: white; color: #1e293b; border: 1px solid #e2e8f0; border-radius: 16px 16px 16px 4px; }
    .ai-typing { display: flex; gap: 4px; padding: 12px 14px; background: white; border: 1px solid #e2e8f0; border-radius: 16px 16px 16px 4px; width: fit-content; }
    .ai-typing span { width: 6px; height: 6px; background: #94a3b8; border-radius: 50%; animation: ai-bounce 1.2s infinite; }
    .ai-typing span:nth-child(2) { animation-delay: 0.2s; }
    .ai-typing span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes ai-bounce { 0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-6px)} }
    #ai-support-input-row {
      padding: 12px 16px; background: white; border-top: 1px solid #e2e8f0;
      display: flex; gap: 8px;
    }
    #ai-support-input {
      flex: 1; border: 1px solid #e2e8f0; border-radius: 24px;
      padding: 9px 16px; font-size: 13px; outline: none;
      transition: border-color 0.2s;
    }
    #ai-support-input:focus { border-color: #2563eb; }
    #ai-support-send {
      width: 38px; height: 38px; background: #2563eb; border: none;
      border-radius: 50%; cursor: pointer; display: flex; align-items: center;
      justify-content: center; transition: background 0.2s; flex-shrink: 0;
    }
    #ai-support-send:hover { background: #1d4ed8; }
    #ai-support-send svg { width: 16px; height: 16px; fill: white; }
    #ai-support-powered { text-align: center; font-size: 10px; color: #94a3b8; padding: 6px; background: white; }
  `;

  function injectStyles() {
    const el = document.createElement('style');
    el.textContent = styles;
    document.head.appendChild(el);
  }

  function createWidget() {
    const container = document.createElement('div');
    container.id = 'ai-support-widget';
    container.innerHTML = `
      <div id="ai-support-window">
        <div id="ai-support-header">
          <div id="ai-support-header-icon">
            <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/></svg>
          </div>
          <div id="ai-support-header-text">
            <h3>AI Support</h3>
            <p>Ask me anything</p>
          </div>
        </div>
        <div id="ai-support-messages">
          <div class="ai-msg bot">
            <div class="ai-msg-bubble">Hi! I am your AI support assistant. How can I help you today?</div>
          </div>
        </div>
        <div id="ai-support-input-row">
          <input id="ai-support-input" type="text" placeholder="Type your message..." />
          <button id="ai-support-send">
            <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
          </button>
        </div>
        <div id="ai-support-powered">Powered by AI Support Platform</div>
      </div>
      <button id="ai-support-bubble">
        <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg>
      </button>
    `;
    document.body.appendChild(container);
  }

  function toggleWidget() {
    isOpen = !isOpen;
    const win = document.getElementById('ai-support-window');
    const bubble = document.getElementById('ai-support-bubble');
    if (isOpen) {
      win.classList.add('open');
      bubble.innerHTML = '<svg viewBox="0 0 24 24" style="fill:white;width:22px;height:22px"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>';
      document.getElementById('ai-support-input').focus();
    } else {
      win.classList.remove('open');
      bubble.innerHTML = '<svg viewBox="0 0 24 24" style="fill:white;width:26px;height:26px"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg>';
    }
  }

  function addMessage(role, text) {
    const msgs = document.getElementById('ai-support-messages');
    const div = document.createElement('div');
    div.className = `ai-msg ${role === 'user' ? 'user' : 'bot'}`;
    div.innerHTML = `<div class="ai-msg-bubble">${text.replace(/\n/g, '<br>')}</div>`;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
    return div;
  }

  function showTyping() {
    const msgs = document.getElementById('ai-support-messages');
    const div = document.createElement('div');
    div.className = 'ai-msg bot';
    div.id = 'ai-typing-indicator';
    div.innerHTML = '<div class="ai-typing"><span></span><span></span><span></span></div>';
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function removeTyping() {
    const el = document.getElementById('ai-typing-indicator');
    if (el) el.remove();
  }

  async function sendMessage() {
    const input = document.getElementById('ai-support-input');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    addMessage('user', text);
    showTyping();

    try {
      const res = await fetch(`${API_BASE}/api/v1/chat/widget`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: sessionId, api_key: API_KEY })
      });
      const data = await res.json();
      removeTyping();
      if (data.answer) {
        sessionId = data.session_id;
        addMessage('bot', data.answer);
      } else {
        addMessage('bot', 'Sorry, something went wrong. Please try again.');
      }
    } catch (e) {
      removeTyping();
      addMessage('bot', 'Unable to connect. Please try again later.');
    }
  }

  function init() {
    injectStyles();
    createWidget();
    document.getElementById('ai-support-bubble').addEventListener('click', toggleWidget);
    document.getElementById('ai-support-send').addEventListener('click', sendMessage);
    document.getElementById('ai-support-input').addEventListener('keydown', function (e) {
      if (e.key === 'Enter') sendMessage();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
