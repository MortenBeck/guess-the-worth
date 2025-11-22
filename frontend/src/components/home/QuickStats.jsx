import { Box, Container, Heading, Text, VStack, SimpleGrid } from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import { statsService } from "../../services/api";

const QuickStats = () => {
  const { data: platformStats, isLoading, error } = useQuery({
    queryKey: ["platform-stats"],
    queryFn: () => statsService.getPlatformStats(),
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });

  // Show error if platform stats fail to load
  if (error) {
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
  if (isLoading || !platformStats) {
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
    { label: "Active Artworks", value: platformStats.totalArtworks, icon: "🎨", color: "#6366f1" },
    { label: "Total Bids", value: `$${platformStats.totalBids}`, icon: "💎", color: "#10b981" },
    { label: "Artists", value: platformStats.totalArtists, icon: "👨‍🎨", color: "#f59e0b" },
    { label: "Live Bidding", value: platformStats.liveStatus, icon: "⚡", color: "#ec4899" },
  ];

  return (
    <Box py={12}>
      <Container maxW="7xl">
        <VStack spacing={12}>
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
