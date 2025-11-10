import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  Image,
  Badge,
} from "@chakra-ui/react";
// Simple custom icons
const SettingsIcon = () => <span>⚙️</span>;
const ViewIcon = () => <span>👁️</span>;
const EditIcon = () => <span>✏️</span>;
const DeleteIcon = () => <span>🗑️</span>;
import useAuthStore from "../store/authStore";
import placeholderImg from "../assets/placeholder.jpg";

const AdminDashboard = () => {
  const { user } = useAuthStore();

  // Mock data - replace with actual API calls
  const stats = {
    totalUsers: 1245,
    activeAuctions: 89,
    totalRevenue: 45620,
    platformFees: 2281,
    usersGrowth: 12.5,
    auctionsGrowth: 8.3,
    revenueGrowth: 15.2,
  };

  const recentUsers = [
    {
      id: 1,
      name: "John Doe",
      email: "john@example.com",
      role: "buyer",
      joinDate: "2024-01-15",
      status: "active",
      avatar: placeholderImg,
    },
    {
      id: 2,
      name: "Jane Smith",
      email: "jane@example.com",
      role: "seller",
      joinDate: "2024-01-14",
      status: "pending",
      avatar: placeholderImg,
    },
  ];

  const flaggedAuctions = [
    {
      id: 1,
      title: "Suspicious Artwork",
      seller: "Unknown Artist",
      currentBid: 5000,
      flagReason: "Unusually high bid activity",
      severity: "high",
    },
    {
      id: 2,
      title: "Vintage Painting",
      seller: "Art Gallery",
      currentBid: 1200,
      flagReason: "Copyright dispute",
      severity: "medium",
    },
  ];

  const systemHealth = {
    serverStatus: "healthy",
    databaseStatus: "healthy",
    paymentSystem: "warning",
    uptime: 99.8,
  };

  const recentTransactions = [
    {
      id: 1,
      buyer: "Alice Brown",
      seller: "Bob Wilson",
      artwork: "Mountain Peak",
      amount: 450,
      fee: 22.5,
      date: "2024-01-15",
      status: "completed",
    },
    {
      id: 2,
      buyer: "Charlie Davis",
      seller: "Diana Miller",
      artwork: "Ocean Waves",
      amount: 320,
      fee: 16.0,
      date: "2024-01-14",
      status: "pending",
    },
  ];

  const getUserStatusColor = (status) => {
    switch (status) {
      case "active":
        return "green";
      case "pending":
        return "yellow";
      case "suspended":
        return "red";
      default:
        return "gray";
    }
  };

  const getSystemStatusColor = (status) => {
    switch (status) {
      case "healthy":
        return "green";
      case "warning":
        return "yellow";
      case "error":
        return "red";
      default:
        return "gray";
    }
  };

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="xl" color="text" mb={2}>
            Admin Dashboard
          </Heading>
          <Text color="gray.600">
            Monitor platform activity, manage users, and oversee system health.
          </Text>
        </Box>

        {/* Key Metrics */}
        <Box
          display="grid"
          gridTemplateColumns={{ base: "repeat(2, 1fr)", md: "repeat(4, 1fr)" }}
          gap={6}
        >
          <Box
            bg="white"
            p={4}
            borderRadius="lg"
            boxShadow="sm"
            border="1px"
            borderColor="gray.200"
            textAlign="center"
          >
            <Text fontSize="sm" color="gray.600">
              Total Users
            </Text>
            <Text fontSize="2xl" fontWeight="bold" color="primary">
              {stats.totalUsers.toLocaleString()}
            </Text>
            <Text fontSize="xs" color="green.500">
              +{stats.usersGrowth}% this month
            </Text>
          </Box>
          <Box
            bg="white"
            p={4}
            borderRadius="lg"
            boxShadow="sm"
            border="1px"
            borderColor="gray.200"
            textAlign="center"
          >
            <Text fontSize="sm" color="gray.600">
              Active Auctions
            </Text>
            <Text fontSize="2xl" fontWeight="bold" color="accent">
              {stats.activeAuctions}
            </Text>
            <Text fontSize="xs" color="green.500">
              +{stats.auctionsGrowth}% this week
            </Text>
          </Box>
          <Box
            bg="white"
            p={4}
            borderRadius="lg"
            boxShadow="sm"
            border="1px"
            borderColor="gray.200"
            textAlign="center"
          >
            <Text fontSize="sm" color="gray.600">
              Total Revenue
            </Text>
            <Text fontSize="2xl" fontWeight="bold" color="primary">
              ${stats.totalRevenue.toLocaleString()}
            </Text>
            <Text fontSize="xs" color="green.500">
              +{stats.revenueGrowth}% this month
            </Text>
          </Box>
          <Box
            bg="white"
            p={4}
            borderRadius="lg"
            boxShadow="sm"
            border="1px"
            borderColor="gray.200"
            textAlign="center"
          >
            <Text fontSize="sm" color="gray.600">
              Platform Fees
            </Text>
            <Text fontSize="2xl" fontWeight="bold" color="accent">
              ${stats.platformFees.toLocaleString()}
            </Text>
            <Text fontSize="xs" color="gray.500">
              5% commission
            </Text>
          </Box>
        </Box>

        {/* System Health */}
        <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
          <Heading size="md" color="text" mb={4}>
            System Health
          </Heading>
          <Box
            display="grid"
            gridTemplateColumns={{ base: "repeat(2, 1fr)", md: "repeat(4, 1fr)" }}
            gap={4}
          >
            <VStack>
              <Text fontSize="sm" color="gray.600">
                Server Status
              </Text>
              <Badge colorScheme={getSystemStatusColor(systemHealth.serverStatus)}>
                {systemHealth.serverStatus}
              </Badge>
            </VStack>
            <VStack>
              <Text fontSize="sm" color="gray.600">
                Database
              </Text>
              <Badge colorScheme={getSystemStatusColor(systemHealth.databaseStatus)}>
                {systemHealth.databaseStatus}
              </Badge>
            </VStack>
            <VStack>
              <Text fontSize="sm" color="gray.600">
                Payment System
              </Text>
              <Badge colorScheme={getSystemStatusColor(systemHealth.paymentSystem)}>
                {systemHealth.paymentSystem}
              </Badge>
            </VStack>
            <VStack>
              <Text fontSize="sm" color="gray.600">
                Uptime
              </Text>
              <Text fontWeight="bold">{systemHealth.uptime}%</Text>
              <Box w="60px" h="2px" bg="gray.200" borderRadius="full">
                <Box w={`${systemHealth.uptime}%`} h="100%" bg="green.500" borderRadius="full" />
              </Box>
            </VStack>
          </Box>
        </Box>

        {/* Recent Users */}
        <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
          <HStack justify="space-between" mb={4}>
            <Heading size="md" color="text">
              Recent Users
            </Heading>
            <Button size="sm" variant="outline">
              View All Users
            </Button>
          </HStack>

          <VStack spacing={4} align="stretch">
            {recentUsers.map((user) => (
              <Box
                key={user.id}
                bg="white"
                p={4}
                borderRadius="lg"
                boxShadow="sm"
                border="1px"
                borderColor="gray.200"
              >
                <HStack spacing={4}>
                  <Image src={user.avatar} alt={user.name} w="40px" h="40px" borderRadius="full" />
                  <VStack align="start" flex={1} spacing={1}>
                    <Heading size="sm">{user.name}</Heading>
                    <Text fontSize="sm" color="gray.600">
                      {user.email}
                    </Text>
                    <HStack>
                      <Badge colorScheme="blue">{user.role}</Badge>
                      <Badge colorScheme={getUserStatusColor(user.status)}>{user.status}</Badge>
                    </HStack>
                    <Text fontSize="xs" color="gray.500">
                      Joined {new Date(user.joinDate).toLocaleDateString()}
                    </Text>
                  </VStack>
                  <VStack spacing={2}>
                    <Button size="xs" variant="outline">
                      <ViewIcon /> View
                    </Button>
                    <Button size="xs" variant="outline">
                      <EditIcon /> Edit
                    </Button>
                  </VStack>
                </HStack>
              </Box>
            ))}
          </VStack>
        </Box>

        {/* Flagged Content */}
        <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
          <Heading size="md" color="text" mb={4}>
            Flagged Auctions
          </Heading>

          <VStack spacing={4} align="stretch">
            {flaggedAuctions.map((auction) => (
              <Box
                key={auction.id}
                bg={auction.severity === "high" ? "red.50" : "orange.50"}
                border="1px"
                borderColor={auction.severity === "high" ? "red.200" : "orange.200"}
                borderRadius="md"
                p={4}
              >
                <HStack justify="space-between">
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="bold">{auction.title}</Text>
                    <Text fontSize="sm">by {auction.seller}</Text>
                    <Text fontSize="sm">Current bid: ${auction.currentBid}</Text>
                  </VStack>
                  <VStack align="end" spacing={1}>
                    <Badge colorScheme={auction.severity === "high" ? "red" : "orange"}>
                      {auction.severity} priority
                    </Badge>
                    <Text fontSize="sm" color="gray.600">
                      {auction.flagReason}
                    </Text>
                    <HStack>
                      <Button size="xs" colorScheme="green">
                        Approve
                      </Button>
                      <Button size="xs" colorScheme="red">
                        Remove
                      </Button>
                    </HStack>
                  </VStack>
                </HStack>
              </Box>
            ))}
          </VStack>
        </Box>

        {/* Transactions */}
        <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
          <Heading size="md" color="text" mb={4}>
            Recent Transactions
          </Heading>

          <VStack spacing={3} align="stretch">
            <HStack
              justify="space-between"
              fontWeight="bold"
              fontSize="sm"
              color="gray.600"
              pb={2}
              borderBottom="1px"
              borderColor="gray.200"
            >
              <Text flex="1">Date</Text>
              <Text flex="2">Buyer</Text>
              <Text flex="2">Seller</Text>
              <Text flex="2">Artwork</Text>
              <Text flex="1" textAlign="right">
                Amount
              </Text>
              <Text flex="1" textAlign="right">
                Fee
              </Text>
              <Text flex="1" textAlign="center">
                Status
              </Text>
            </HStack>
            {recentTransactions.map((transaction) => (
              <HStack key={transaction.id} justify="space-between" fontSize="sm">
                <Text flex="1">{new Date(transaction.date).toLocaleDateString()}</Text>
                <Text flex="2">{transaction.buyer}</Text>
                <Text flex="2">{transaction.seller}</Text>
                <Text flex="2">{transaction.artwork}</Text>
                <Text flex="1" textAlign="right">
                  ${transaction.amount}
                </Text>
                <Text flex="1" textAlign="right">
                  ${transaction.fee}
                </Text>
                <Box flex="1" textAlign="center">
                  <Badge colorScheme={transaction.status === "completed" ? "green" : "yellow"}>
                    {transaction.status}
                  </Badge>
                </Box>
              </HStack>
            ))}
          </VStack>
        </Box>

        {/* Analytics & Reports */}
        <Box display="grid" gridTemplateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={6}>
          <Box
            bg="white"
            p={6}
            borderRadius="lg"
            boxShadow="sm"
            border="1px"
            borderColor="gray.200"
          >
            <Heading size="md" color="text" mb={4}>
              Platform Analytics
            </Heading>
            <VStack spacing={4}>
              <HStack justify="space-between" w="full">
                <Text>Daily active users</Text>
                <Text fontWeight="bold">342</Text>
              </HStack>
              <HStack justify="space-between" w="full">
                <Text>Conversion rate</Text>
                <Text fontWeight="bold">12.5%</Text>
              </HStack>
              <HStack justify="space-between" w="full">
                <Text>Average auction value</Text>
                <Text fontWeight="bold">$285</Text>
              </HStack>
              <HStack justify="space-between" w="full">
                <Text>Success rate (threshold met)</Text>
                <Text fontWeight="bold">68%</Text>
              </HStack>
            </VStack>
          </Box>

          <Box
            bg="white"
            p={6}
            borderRadius="lg"
            boxShadow="sm"
            border="1px"
            borderColor="gray.200"
          >
            <Heading size="md" color="text" mb={4}>
              Export Reports
            </Heading>
            <VStack spacing={3}>
              <Button w="full" variant="outline">
                Download User Report
              </Button>
              <Button w="full" variant="outline">
                Download Sales Report
              </Button>
              <Button w="full" variant="outline">
                Download Financial Report
              </Button>
              <Button w="full" variant="outline">
                Download System Logs
              </Button>
            </VStack>
          </Box>
        </Box>

        {/* Platform Settings */}
        <Box display="grid" gridTemplateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={6}>
          <Box
            bg="white"
            p={6}
            borderRadius="lg"
            boxShadow="sm"
            border="1px"
            borderColor="gray.200"
          >
            <Heading size="md" color="text" mb={4}>
              Platform Settings
            </Heading>
            <VStack spacing={4} align="stretch">
              <HStack justify="space-between">
                <Text>Commission Rate</Text>
                <Text fontWeight="bold">5%</Text>
              </HStack>
              <HStack justify="space-between">
                <Text>Auto-approve artworks</Text>
                <Badge colorScheme="red">Disabled</Badge>
              </HStack>
              <HStack justify="space-between">
                <Text>Maintenance Mode</Text>
                <Badge colorScheme="green">Off</Badge>
              </HStack>
              <Button colorScheme="primary" size="sm">
                Update Settings
              </Button>
            </VStack>
          </Box>

          <Box
            bg="white"
            p={6}
            borderRadius="lg"
            boxShadow="sm"
            border="1px"
            borderColor="gray.200"
          >
            <Heading size="md" color="text" mb={4}>
              System Actions
            </Heading>
            <VStack spacing={3}>
              <Button w="full" colorScheme="yellow">
                Send Platform Notification
              </Button>
              <Button w="full" colorScheme="orange">
                Enable Maintenance Mode
              </Button>
              <Button w="full" colorScheme="red">
                Emergency Shutdown
              </Button>
            </VStack>
          </Box>
        </Box>
      </VStack>
    </Container>
  );
};

export default AdminDashboard;
