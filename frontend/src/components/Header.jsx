import { Box, Button, HStack, Text, Container, VStack } from "@chakra-ui/react";
import { useAuth0 } from "@auth0/auth0-react";
import { useNavigate, useLocation } from "react-router-dom";
import { useState } from "react";

const Header = () => {
  const { loginWithRedirect, logout, isAuthenticated, user } = useAuth0();
  const navigate = useNavigate();
  const location = useLocation();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const publicNavItems = [
    { label: "How It Works", path: "#how-it-works" },
    { label: "Artworks", path: "/artworks" },
    { label: "About", path: "#about" },
  ];

  const authenticatedNavItems = [
    { label: "Home", path: "/" },
    { label: "Artworks", path: "/artworks" },
    { label: "Dashboard", path: "/dashboard" },
    { label: "Sell Artwork", path: "/seller-dashboard" },
  ];

  const navItems = isAuthenticated ? authenticatedNavItems : publicNavItems;

  const handleNavClick = (path) => {
    if (path.startsWith("#")) {
      // Handle anchor links
      if (location.pathname === "/") {
        // Already on homepage, just scroll
        const element = document.querySelector(path);
        if (element) {
          element.scrollIntoView({ behavior: "smooth" });
        }
      } else {
        // Navigate to homepage with scroll target
        navigate("/", { state: { scrollTo: path } });
      }
    } else {
      navigate(path);
    }
  };

  return (
    <Box
      bg="#1e293b"
      color="white"
      borderBottom="1px solid"
      borderColor="rgba(255,255,255,0.1)"
      position="sticky"
      top={0}
      zIndex={1000}
    >
      <Container maxW="container.xl" py={4}>
        <HStack w="full">
          {/* Logo - Left */}
          <Box flex="1">
            <Text
              fontSize="xl"
              fontWeight="bold"
              cursor="pointer"
              onClick={() => navigate("/")}
              _hover={{ opacity: 0.8 }}
              transition="opacity 0.2s"
            >
              Guess The Worth
            </Text>
          </Box>

          {/* Navigation - Center */}
          <Box as="nav" flex="1" display="flex" justifyContent="center" data-testid="main-nav">
            <HStack spacing={8}>
              {navItems.map((item) => (
                <Text
                  key={item.path}
                  cursor="pointer"
                  color="#94a3b8"
                  fontSize="md"
                  fontWeight="500"
                  mx={4}
                  _hover={{
                    color: "white",
                    transform: "translateY(-1px)",
                  }}
                  transition="all 0.2s"
                  onClick={() => handleNavClick(item.path)}
                  data-testid={`nav-${item.label.toLowerCase().replace(/ /g, '-')}`}
                >
                  {item.label}
                </Text>
              ))}
            </HStack>
          </Box>

          {/* Auth Section - Right */}
          <Box flex="1" display="flex" justifyContent="flex-end">
            {isAuthenticated ? (
              <Box position="relative">
                <Button
                  variant="ghost"
                  color="#94a3b8"
                  _hover={{ bg: "#334155", color: "white" }}
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                >
                  <HStack spacing={2}>
                    <Text fontSize="sm">Hello {user?.name}</Text>
                    <Text fontSize="xs">{isDropdownOpen ? "▲" : "▼"}</Text>
                  </HStack>
                </Button>

                {isDropdownOpen && (
                  <Box
                    position="absolute"
                    top="100%"
                    right="0"
                    mt={2}
                    bg="#1e293b"
                    border="1px solid"
                    borderColor="rgba(255,255,255,0.1)"
                    borderRadius="md"
                    boxShadow="0 4px 12px rgba(0,0,0,0.3)"
                    zIndex={1000}
                    minW="180px"
                  >
                    <VStack spacing={0} align="stretch">
                      <Text
                        fontSize="sm"
                        color="#94a3b8"
                        cursor="pointer"
                        p={3}
                        _hover={{ bg: "#334155", color: "white" }}
                        onClick={() => {
                          navigate("/profile");
                          setIsDropdownOpen(false);
                        }}
                      >
                        👤 Profile Settings
                      </Text>

                      <Text
                        fontSize="sm"
                        color="#94a3b8"
                        cursor="pointer"
                        p={3}
                        _hover={{ bg: "#334155", color: "white" }}
                        onClick={() => {
                          navigate("/favourites");
                          setIsDropdownOpen(false);
                        }}
                      >
                        ⭐ Favourites
                      </Text>

                      <Text
                        fontSize="sm"
                        color="#94a3b8"
                        cursor="pointer"
                        p={3}
                        _hover={{ bg: "#334155", color: "white" }}
                        onClick={() => {
                          navigate("/dashboard");
                          setIsDropdownOpen(false);
                        }}
                      >
                        ⚙️ Dashboard
                      </Text>

                      <Box h="1px" bg="rgba(255,255,255,0.1)" />

                      <Text
                        fontSize="sm"
                        color="#94a3b8"
                        cursor="pointer"
                        p={3}
                        _hover={{ bg: "#334155", color: "white" }}
                        onClick={() => {
                          navigate("/help");
                          setIsDropdownOpen(false);
                        }}
                      >
                        ❓ Help & Support
                      </Text>

                      <Box h="1px" bg="rgba(255,255,255,0.1)" />

                      <Text
                        fontSize="sm"
                        color="#f87171"
                        cursor="pointer"
                        p={3}
                        _hover={{ bg: "#7f1d1d", color: "white" }}
                        onClick={() => {
                          logout({ logoutParams: { returnTo: window.location.origin } });
                          setIsDropdownOpen(false);
                        }}
                      >
                        Logout
                      </Text>
                    </VStack>
                  </Box>
                )}
              </Box>
            ) : (
              <Button
                background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
                color="white"
                onClick={() => loginWithRedirect()}
                _hover={{
                  transform: "translateY(-1px)",
                  boxShadow: "0 4px 15px rgba(99, 102, 241, 0.3)",
                }}
                transition="all 0.2s"
              >
                Login
              </Button>
            )}
          </Box>
        </HStack>
      </Container>
    </Box>
  );
};

export default Header;
