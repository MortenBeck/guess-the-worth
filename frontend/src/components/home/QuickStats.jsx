import { Box, Container, Heading, Text, VStack, SimpleGrid } from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import { statsService } from "../../services/api";
import useAuthStore from "../../store/authStore";

const QuickStats = () => {
  const { isAuthenticated } = useAuthStore();

  // Fetch platform stats
  const {
    data: platformStats,
    isLoading: platformLoading,
    error: platformError,
  } = useQuery({
    queryKey: ["platform-stats"],
    queryFn: () => statsService.getPlatformStats(),
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });

  // Fetch user stats (only if logged in)
  const { data: userStatsData, isLoading: userLoading } = useQuery({
    queryKey: ["user-stats"],
    queryFn: statsService.getUserStats,
    enabled: isAuthenticated,
    staleTime: 60000,
  });

  const userStats = userStatsData?.data;

  // Show error if platform stats fail to load
  if (platformError) {
    return (
      <Box py={12}>
        <Container maxW="7xl">
          <Box textAlign="center" p={8}>
            <Text color="red.400" fontSize="lg">
              Unable to load platform statistics
            </Text>
          </Box>
        </Container>
      </Box>
    );
  }

  // Show loading state
  if (platformLoading) {
    return (
      <Box py={12}>
        <Container maxW="7xl">
          <Box textAlign="center" p={8}>
            <Text color="#94a3b8">Loading statistics...</Text>
          </Box>
        </Container>
      </Box>
    );
  }

  const platformStatsData = [
    {
      label: "Active Artworks",
      value: platformStats?.data?.active_auctions || 0,
      icon: "🎨",
      color: "#6366f1",
    },
    {
      label: "Total Bids",
      value: platformStats?.data?.total_bids || 0,
      icon: "💎",
      color: "#10b981",
    },
    { label: "Total Users", value: platformStats?.data?.total_users || 0, icon: "👨‍🎨", color: "#f59e0b" },
    {
      label: "Total Artworks",
      value: platformStats?.data?.total_artworks || 0,
      icon: "⚡",
      color: "#ec4899",
    },
  ];

  const personalStats =
    isAuthenticated && userStats
      ? [
          { label: "Your Bids", value: userStats.active_bids || 0, icon: "💰", color: "#6366f1" },
          {
            label: "Artworks Won",
            value: userStats.won_auctions || 0,
            icon: "🏆",
            color: "#10b981",
          },
        ]
      : [];

  return (
    <Box py={12}>
      <Container maxW="7xl">
        <VStack spacing={12}>
          {/* Personal Stats (only for logged-in users) */}
          {isAuthenticated && !userLoading && personalStats.length > 0 && (
            <VStack spacing={6} w="full">
              <Heading size="lg" color="white" fontWeight="700" textAlign="center">
                Your Activity
              </Heading>

              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} w="full">
                {personalStats.map((stat, index) => (
                  <Box
                    key={index}
                    bg="#0f172a"
                    p={6}
                    borderRadius="xl"
                    textAlign="center"
                    border="1px solid"
                    borderColor="rgba(255,255,255,0.1)"
                  >
                    <VStack spacing={3}>
                      <Text fontSize="xl">{stat.icon}</Text>
                      <Text fontSize="2xl" fontWeight="700" color={stat.color}>
                        {stat.value}
                      </Text>
                      <Text fontSize="sm" color="#94a3b8" textAlign="center">
                        {stat.label}
                      </Text>
                    </VStack>
                  </Box>
                ))}
              </SimpleGrid>
            </VStack>
          )}

          {/* Platform Stats */}
          <VStack spacing={6} w="full">
            <Heading size="xl" color="white" fontWeight="700" textAlign="center">
              Platform Overview
            </Heading>

            <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6} w="full">
              {platformStatsData.map((stat, index) => (
                <Box
                  key={index}
                  bg="#0f172a"
                  p={6}
                  borderRadius="xl"
                  textAlign="center"
                  border="1px solid"
                  borderColor="rgba(255,255,255,0.1)"
                >
                  <VStack spacing={3}>
                    <Text fontSize="xl">{stat.icon}</Text>
                    <Text fontSize="2xl" fontWeight="700" color={stat.color}>
                      {stat.value}
                    </Text>
                    <Text fontSize="sm" color="#94a3b8" textAlign="center">
                      {stat.label}
                    </Text>
                  </VStack>
                </Box>
              ))}
            </SimpleGrid>
          </VStack>
        </VStack>
      </Container>
    </Box>
  );
};

export default QuickStats;
