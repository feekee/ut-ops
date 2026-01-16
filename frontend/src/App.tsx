import { useState } from 'react'
import Sidebar from './components/Sidebar'
import ChatArea from './components/ChatArea'
import { useChatStore } from './store/chatStore'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="h-screen flex bg-dark-900 overflow-hidden">
      {/* 背景效果 */}
      <div className="fixed inset-0 grid-bg radial-bg pointer-events-none" />
      
      {/* 侧边栏 */}
      <Sidebar 
        isOpen={sidebarOpen} 
        onToggle={() => setSidebarOpen(!sidebarOpen)} 
      />

      {/* 主聊天区域 */}
      <main className="flex-1 flex flex-col relative min-w-0">
        <ChatArea sidebarOpen={sidebarOpen} onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      </main>
    </div>
  )
}

export default App
