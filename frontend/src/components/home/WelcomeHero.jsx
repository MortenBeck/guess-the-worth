import { Box, Container, Heading, Text, Button, VStack, HStack } from "@chakra-ui/react";
import { useAuth0 } from "@auth0/auth0-react";
import { useNavigate } from "react-router-dom";
import useAuthStore from "../../store/authStore";

const WelcomeHero = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  const getTimeGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 17) return "Good afternoon";
    return "Good evening";
  };

  return (
    <Box bg="#0f172a" position="relative" overflow="hidden" py={16}>
      <Box
        position="absolute"
        top="0"
        left="0"
        right="0"
        bottom="0"
        background="radial-gradient(circle at 30% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%), radial-gradient(circle at 70% 80%, rgba(236, 72, 153, 0.15) 0%, transparent 50%)"
        zIndex="0"
      />

      <Container maxW="7xl" position="relative" zIndex="1">
        <VStack spacing={8} textAlign="center">
          <VStack spacing={4}>
            <Text fontSize="lg" color="#94a3b8">
              {getTimeGreeting()}, {user?.name || "Welcome back"}!
            </Text>

            <Heading
              size={{ base: "2xl", md: "3xl" }}
              fontWeight="700"
              background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
              backgroundClip="text"
              color="transparent"
              textAlign="center"
            >
              Ready to discover your next masterpiece?
            </Heading>

            <Text fontSize="lg" color="#94a3b8" maxW="600px">
              Explore live auctions, track your bids, and find art that speaks to you.
            </Text>
          </VStack>

          <HStack spacing={6} wrap="wrap" justify="center">
            <Button
              size="lg"
              background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
              color="white"
              px={8}
              py={6}
              fontSize="md"
              fontWeight="600"
              onClick={() => navigate("/artworks")}
              _hover={{
                transform: "translateY(-2px) scale(1.05)",
                boxShadow: "0 10px 25px rgba(99, 102, 241, 0.3)",
              }}
              transition="all 0.3s ease"
            >
              Browse Artworks
            </Button>

            <Button
              size="lg"
              variant="outline"
              borderColor="#334155"
              color="#94a3b8"
              bg="transparent"
              px={8}
              py={6}
              fontSize="md"
              fontWeight="600"
              onClick={() => navigate("/dashboard")}
              _hover={{
                bg: "#1e293b",
                color: "white",
                borderColor: "#1e293b",
              }}
              transition="all 0.3s ease"
            >
              My Dashboard
            </Button>
          </HStack>
        </VStack>
      </Container>
    </Box>
  );
};

export default WelcomeHero;
