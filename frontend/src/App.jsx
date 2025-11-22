import { useEffect, lazy, Suspense } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Box, Spinner, Center } from "@chakra-ui/react";
import useAuthStore from "./store/authStore";
import socketService from "./services/socket";
import { userService } from "./services/api";
import Header from "./components/Header";
import NotificationSystem from "./components/NotificationSystem";
import SocketStatus from "./components/SocketStatus";

// Eager load critical pages for better initial performance
import HomePage from "./pages/HomePage";
import Home from "./pages/Home";
import ArtworksPage from "./pages/ArtworksPage";

// Lazy load other pages to reduce initial bundle size
const ArtworkPage = lazy(() => import("./pages/ArtworkPage"));
const UserDashboard = lazy(() => import("./pages/UserDashboard"));
const SellerDashboard = lazy(() => import("./pages/SellerDashboard"));
const AddArtworkPage = lazy(() => import("./pages/AddArtworkPage"));
const AdminDashboard = lazy(() => import("./pages/AdminDashboard"));
const ProfilePage = lazy(() => import("./pages/ProfilePage"));
const FavouritesPage = lazy(() => import("./pages/FavouritesPage"));
const HelpPage = lazy(() => import("./pages/HelpPage"));

function App() {
  const { isLoading: auth0Loading, isAuthenticated, user, getAccessTokenSilently } = useAuth0();
  const { setAuth, clearAuth, setLoading, isLoading } = useAuthStore();

  useEffect(() => {
    const handleAuth = async () => {
      setLoading(true);

      if (isAuthenticated && user) {
        try {
          const token = await getAccessTokenSilently();
          localStorage.setItem("access_token", token);

          // Get user from backend database
          const { data: backendUser } = await userService.getCurrentUser();

          setAuth(backendUser, token);
          socketService.connect();
        } catch (error) {
          console.error("Error getting token or user:", error);
          clearAuth();
        }
      } else if (!isAuthenticated) {
        clearAuth();
        localStorage.removeItem("access_token");
        socketService.disconnect();
      }

      setLoading(false);
    };

    if (!auth0Loading) {
      handleAuth();
    }
  }, [isAuthenticated, user, auth0Loading, getAccessTokenSilently, setAuth, clearAuth, setLoading]);

  if (auth0Loading || isLoading) {
    return (
      <Center h="100vh">
        <Spinner size="xl" color="primary" />
      </Center>
    );
  }

  return (
    <BrowserRouter>
      <Box minH="100vh">
        <Header />
        <NotificationSystem />
        <Suspense
          fallback={
            <Center h="100vh">
              <Spinner size="xl" color="primary" />
            </Center>
          }
        >
          <Routes>
            <Route path="/" element={isAuthenticated ? <Home /> : <HomePage />} />
            <Route path="/home" element={<Home />} />
            <Route path="/artworks" element={<ArtworksPage />} />
            <Route path="/artwork/:id" element={<ArtworkPage />} />
            <Route path="/dashboard" element={<UserDashboard />} />
            <Route path="/seller-dashboard" element={<SellerDashboard />} />
            <Route path="/add-artwork" element={<AddArtworkPage />} />
            <Route path="/admin-dashboard" element={<AdminDashboard />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/favourites" element={<FavouritesPage />} />
            <Route path="/help" element={<HelpPage />} />
          </Routes>
        </Suspense>
        <SocketStatus />
      </Box>
    </BrowserRouter>
  );
}

export default App;
