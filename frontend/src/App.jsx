import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import DashboardLayout from './components/layout/DashboardLayout';
import Overview from './pages/donor/Overview';
import MyItems from './pages/donor/MyItems';
import MyMatches from './pages/donor/MyMatches';
import Impact from './pages/donor/Impact';
import NGODashboard from './pages/NGODashboard';
import AdminDashboard from './pages/AdminDashboard';
import DonationForm from './pages/DonationForm';
import RequestForm from './pages/RequestForm';
import MatchView from './pages/MatchView';
import MapView from './pages/MapView';
import PrivateRoute from './components/PrivateRoute';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          <Route
            path="/donor/*"
            element={
              <PrivateRoute allowedRoles={['donor']}>
                <DashboardLayout />
              </PrivateRoute>
            }
          >
            <Route path="dashboard" element={<Overview />} />
            <Route path="dashboard/items" element={<MyItems />} />
            <Route path="dashboard/matches" element={<MyMatches />} />
            <Route path="dashboard/impact" element={<Impact />} />
            <Route path="*" element={<Navigate to="dashboard" replace />} />
          </Route>
          <Route
            path="/ngo/*"
            element={
              <PrivateRoute allowedRoles={['ngo']}>
                <NGODashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/admin/*"
            element={
              <PrivateRoute allowedRoles={['admin']}>
                <AdminDashboard />
              </PrivateRoute>
            }
          />
          
          <Route path="/donation/new" element={
            <PrivateRoute allowedRoles={['donor']}>
              <DonationForm />
            </PrivateRoute>
          } />
          <Route path="/request/new" element={
            <PrivateRoute allowedRoles={['ngo']}>
              <RequestForm />
            </PrivateRoute>
          } />
          <Route path="/matches/:donationId" element={
            <PrivateRoute allowedRoles={['donor']}>
              <MatchView />
            </PrivateRoute>
          } />
          <Route path="/map/:deliveryId" element={
            <PrivateRoute allowedRoles={['donor', 'ngo', 'volunteer']}>
              <MapView />
            </PrivateRoute>
          } />
          
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;