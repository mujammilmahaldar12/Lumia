import Header from './components/Header'
import Home from './components/Home'
import Footer from './components/Footer'
import { ThemeProvider } from './context/ThemeContext'
import './App.css'

function App() {
  return (
    <ThemeProvider>
      <div className="min-h-screen bg-light dark:bg-dark-900 transition-colors duration-300">
        <Header />
        <main>
          <Home />
        </main>
        <Footer />
      </div>
    </ThemeProvider>
  )
}

export default App
