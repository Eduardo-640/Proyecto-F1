import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';

// Pages
import Races from './pages/Races';
import Dashboard from './pages/Dashboard';
import Teams from './pages/Teams';
import Home from './pages/Home';
import News from './pages/News';
import Profile from './pages/Profile';
import Drivers from './pages/Drivers';
import Welcome from './pages/Welcome';

// Auth pages
import ConfirmPassword from './pages/auth/ConfirmPassword';
import ForgotPassword from './pages/auth/ForgotPassword';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import ResetPassword from './pages/auth/ResetPassword';
import VerifyEmail from './pages/auth/VerifyEmail';

import Analytics from './pages/Analytics';

// Fantasy pages
import Buy from './pages/fantasy/Buy';
import CreateTeam from './pages/fantasy/CreateTeam';
import FantasyTeams from './pages/fantasy/Teams';
import FantasyIndex from './pages/fantasy/Index';
import MyTeam from './pages/fantasy/MyTeam';
import Sell from './pages/fantasy/Sell';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/drivers" element={<Drivers />} />
          <Route path="/teams" element={<Teams />} />
          <Route path="/races" element={<Races />} />
          <Route path="/news" element={<News />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/confirm-password" element={<ConfirmPassword />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/fantasy" element={<FantasyIndex />} />
          <Route path="/fantasy/create" element={<CreateTeam />} />
          <Route path="/fantasy/my-team" element={<MyTeam />} />
          <Route path="/fantasy/teams" element={<FantasyTeams />} />
          <Route path="/fantasy/buy" element={<Buy />} />
          <Route path="/fantasy/sell" element={<Sell />} />
          <Route path="*" element={<Welcome />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
