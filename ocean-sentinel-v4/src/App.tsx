import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import { Layout } from './components/layout/Layout'
import { PageLoader } from './components/ui/PageLoader'

// Lazy loading des pages pour optimisation
const Home = lazy(() => import('./pages/Home'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const About = lazy(() => import('./pages/About'))
const API = lazy(() => import('./pages/API'))
const Podcast = lazy(() => import('./pages/Podcast'))
const Contact = lazy(() => import('./pages/Contact'))
const Legal = lazy(() => import('./pages/Legal'))
const Privacy = lazy(() => import('./pages/Privacy'))

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/about" element={<About />} />
            <Route path="/api" element={<API />} />
            <Route path="/podcast" element={<Podcast />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/mentions-legales" element={<Legal />} />
            <Route path="/politique-confidentialite" element={<Privacy />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </Layout>
    </BrowserRouter>
  )
}

export default App
