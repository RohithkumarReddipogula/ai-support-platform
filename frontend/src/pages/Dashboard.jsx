import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../hooks/useAuth'
import { documentsAPI, chatAPI } from '../services/api'
import {
  Bot, Upload, FileText, Trash2, Send,
  LogOut, CheckCircle, Clock, XCircle, Loader2, MessageSquare
} from 'lucide-react'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [documents, setDocuments] = useState([])
  const [uploading, setUploading] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [sending, setSending] = useState(false)
  const [activeTab, setActiveTab] = useState('chat')
  const fileRef = useRef()
  const chatRef = useRef()

  useEffect(() => {
    loadDocuments()
  }, [])

  useEffect(() => {
    chatRef.current?.scrollTo(0, chatRef.current.scrollHeight)
  }, [messages])

  const loadDocuments = async () => {
    try {
      const res = await documentsAPI.list()
      setDocuments(res.data.documents)
    } catch (e) {}
  }

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setUploading(true)
    try {
      await documentsAPI.upload(file)
      await loadDocuments()
      setTimeout(loadDocuments, 3000)
    } catch (err) {
      alert(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
      fileRef.current.value = ''
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this document?')) return
    await documentsAPI.delete(id)
    await loadDocuments()
  }

  const handleSend = async () => {
    if (!input.trim() || sending) return
    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setSending(true)
    try {
      const res = await chatAPI.send(userMsg, sessionId)
      setSessionId(res.data.session_id)
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.answer, sources: res.data.sources }])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Something went wrong. Try again.' }])
    } finally {
      setSending(false)
    }
  }

  const statusIcon = (status) => {
    if (status === 'completed') return <CheckCircle size={14} className="text-green-500" />
    if (status === 'failed') return <XCircle size={14} className="text-red-500" />
    return <Clock size={14} className="text-yellow-500 animate-pulse" />
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 p-1.5 rounded-lg">
            <Bot size={20} className="text-white" />
          </div>
          <div>
            <span className="font-semibold text-gray-900">AI Support Platform</span>
            <span className="text-xs text-gray-500 ml-2">{user?.tenant?.name}</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-600">{user?.email}</span>
          <button onClick={logout} className="text-gray-400 hover:text-gray-600 transition">
            <LogOut size={18} />
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-100">
            <button
              onClick={() => setActiveTab('chat')}
              className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition ${activeTab === 'chat' ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-50'}`}
            >
              <MessageSquare size={16} />
              Chat
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition mt-1 ${activeTab === 'documents' ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-50'}`}
            >
              <FileText size={16} />
              Documents
            </button>
          </div>

          {/* Upload */}
          <div className="p-4">
            <input ref={fileRef} type="file" accept=".pdf,.txt,.docx" onChange={handleUpload} className="hidden" />
            <button
              onClick={() => fileRef.current?.click()}
              disabled={uploading}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 rounded-lg transition"
            >
              {uploading ? <Loader2 size={14} className="animate-spin" /> : <Upload size={14} />}
              {uploading ? 'Uploading...' : 'Upload Document'}
            </button>
            <p className="text-xs text-gray-400 mt-2 text-center">PDF, TXT, DOCX up to 10MB</p>
          </div>

          {/* Document list */}
          <div className="flex-1 overflow-y-auto px-4 pb-4">
            {documents.length === 0 ? (
              <p className="text-xs text-gray-400 text-center mt-4">No documents yet</p>
            ) : (
              <div className="space-y-2">
                {documents.map(doc => (
                  <div key={doc.id} className="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-2">
                    <FileText size={14} className="text-gray-400 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-gray-700 truncate">{doc.filename}</p>
                      <div className="flex items-center gap-1 mt-0.5">
                        {statusIcon(doc.status)}
                        <span className="text-xs text-gray-400">{doc.chunk_count} chunks</span>
                      </div>
                    </div>
                    <button onClick={() => handleDelete(doc.id)} className="text-gray-300 hover:text-red-400 transition shrink-0">
                      <Trash2 size={12} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {activeTab === 'chat' ? (
            <>
              {/* Chat messages */}
              <div ref={chatRef} className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 && (
                  <div className="flex flex-col items-center justify-center h-full text-center">
                    <div className="bg-blue-100 p-4 rounded-full mb-4">
                      <Bot size={32} className="text-blue-600" />
                    </div>
                    <h2 className="text-lg font-semibold text-gray-800">AI Support Assistant</h2>
                    <p className="text-sm text-gray-500 mt-2 max-w-sm">
                      Upload documents and ask questions. The AI will answer based on your knowledge base.
                    </p>
                  </div>
                )}

                {messages.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai'}>
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      {msg.sources?.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-gray-100">
                          <p className="text-xs text-gray-400">Sources: {msg.sources.length} chunk(s) retrieved</p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {sending && (
                  <div className="flex justify-start">
                    <div className="chat-bubble-ai flex items-center gap-2">
                      <Loader2 size={14} className="animate-spin text-gray-400" />
                      <span className="text-sm text-gray-500">Thinking...</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Input */}
              <div className="border-t border-gray-200 bg-white p-4">
                <div className="flex gap-3 max-w-3xl mx-auto">
                  <input
                    type="text"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
                    placeholder="Ask a question about your documents..."
                    className="flex-1 border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={handleSend}
                    disabled={!input.trim() || sending}
                    className="bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white px-4 py-2.5 rounded-xl transition"
                  >
                    <Send size={18} />
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 overflow-y-auto p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Knowledge Base Documents</h2>
              {documents.length === 0 ? (
                <div className="text-center py-16 text-gray-400">
                  <FileText size={48} className="mx-auto mb-4 opacity-30" />
                  <p>No documents uploaded yet. Upload a PDF, TXT, or DOCX file to get started.</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {documents.map(doc => (
                    <div key={doc.id} className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-4">
                      <FileText size={24} className="text-blue-500 shrink-0" />
                      <div className="flex-1">
                        <p className="font-medium text-gray-800">{doc.filename}</p>
                        <div className="flex items-center gap-3 mt-1">
                          <div className="flex items-center gap-1">
                            {statusIcon(doc.status)}
                            <span className="text-xs text-gray-500 capitalize">{doc.status}</span>
                          </div>
                          <span className="text-xs text-gray-400">{doc.chunk_count} chunks indexed</span>
                          <span className="text-xs text-gray-400">{new Date(doc.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="text-gray-300 hover:text-red-500 transition p-2 rounded-lg hover:bg-red-50"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
