import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import RecognitionPage from './pages/RecognitionPage';
import SearchPage from './pages/SearchPage';
import RecommendationPage from './pages/RecommendationPage';
import FoodDetailPage from './pages/FoodDetailPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import AdminDashboard from './pages/admin/Dashboard';
import AdminFoods from './pages/admin/Foods';
import AdminUsers from './pages/admin/Users';
import ProtectedRoute from './components/ProtectedRoute';
import ChatPage from './pages/ChatPage';
import AIChatWidget from './components/AIChatWidget';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-right" />
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="recognition" element={<RecognitionPage />} />
            <Route path="search" element={<SearchPage />} />
            <Route path="recommendations" element={<RecommendationPage />} />
            <Route path="food/:id" element={<FoodDetailPage />} />
            <Route path="login" element={<LoginPage />} />
            <Route path="register" element={<RegisterPage />} />
            
            {/* Protected routes */}
            <Route path="profile" element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            } />
            <Route path="chat" element={<ChatPage />} />
          </Route>
          
          {/* Admin routes */}
          <Route path="/admin" element={
            <ProtectedRoute adminOnly>
              <AdminDashboard />
            </ProtectedRoute>
          } />
          <Route path="/admin/foods" element={
            <ProtectedRoute adminOnly>
              <AdminFoods />
            </ProtectedRoute>
          } />
          <Route path="/admin/users" element={
            <ProtectedRoute adminOnly>
              <AdminUsers />
            </ProtectedRoute>
          } />
        </Routes>
      </BrowserRouter>
      <AIChatWidget />
    </AuthProvider>
  );
}

export default App;
