import { useState } from "react";
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
  Spinner,
} from "@chakra-ui/react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { userService, statsService } from "../services/api";
import useAuthStore from "../store/authStore";
import placeholderImg from "../assets/placeholder.jpg";
import { toaster } from "../components/ui/toaster";

const EditIcon = () => <span>✏️</span>;
const CheckIcon = () => <span>✓</span>;
const CloseIcon = () => <span>✕</span>;

const ProfilePage = () => {
  const { user, updateUser } = useAuthStore();
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);

  // Fetch current user data
  const { data: currentUserData, isLoading: userLoading } = useQuery({
    queryKey: ["current-user"],
    queryFn: userService.getCurrentUser,
    staleTime: 60000,
  });

  // Fetch user stats
  const { data: userStatsData, isLoading: statsLoading } = useQuery({
    queryKey: ["user-stats"],
    queryFn: statsService.getUserStats,
    staleTime: 60000,
  });

  const currentUser = currentUserData?.data || user;
  const userStats = userStatsData?.data || {
    active_bids: 0,
    won_auctions: 0,
  };

  const [formData, setFormData] = useState({
    name: "",
    email: "",
  });

  // Update formData when currentUser loads
  useState(() => {
    if (currentUser) {
      setFormData({
        name: currentUser.name || "",
        email: currentUser.email || "",
      });
    }
  }, [currentUser]);

  // Update user mutation
  const updateUserMutation = useMutation({
    mutationFn: (userData) => userService.updateProfile(userData),
    onSuccess: (response) => {
      toaster.create({
        title: "Profile updated successfully",
        type: "success",
        duration: 3000,
      });
      queryClient.invalidateQueries(["current-user"]);
      // Update auth store with new user data
      if (response?.data) {
        updateUser(response.data);
      }
      setIsEditing(false);
    },
    onError: (error) => {
      toaster.create({
        title: "Update failed",
        description: error.message || "Failed to update profile",
        type: "error",
        duration: 5000,
      });
    },
  });

  if (userLoading || statsLoading) {
    return (
      <Box
        bg="#0f172a"
        minH="100vh"
        color="white"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Spinner size="xl" color="#6366f1" />
      </Box>
    );
  }

  const handleSave = () => {
    updateUserMutation.mutate(formData);
  };

  const handleCancel = () => {
    setFormData({
      name: currentUser?.name || "",
      email: currentUser?.email || "",
    });
    setIsEditing(false);
  };

  return (
    <Box bg="#0f172a" minH="100vh" color="white">
      <Container maxW="container.xl" py={8}>
        <Box display="grid" gridTemplateColumns={{ base: "1fr", lg: "1fr 2fr" }} gap={8}>
          {/* Left Column - Profile Info */}
          <VStack spacing={6} align="stretch">
            <Box
              bg="#1e293b"
              p={6}
              borderRadius="lg"
              boxShadow="sm"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
              textAlign="center"
            >
              <VStack spacing={4}>
                <Image
                  w="120px"
                  h="120px"
                  borderRadius="full"
                  src={currentUser?.picture || placeholderImg}
                  alt={currentUser?.name}
                  objectFit="cover"
                />
                <VStack spacing={1}>
                  <Heading size="lg" color="text">
                    {currentUser?.name}
                  </Heading>
                  <HStack>
                    <Badge colorScheme="primary" textTransform="capitalize">
                      {currentUser?.role}
                    </Badge>
                  </HStack>
                </VStack>

                <Button
                  leftIcon={isEditing ? <CloseIcon /> : <EditIcon />}
                  colorScheme={isEditing ? "gray" : "primary"}
                  variant={isEditing ? "outline" : "solid"}
                  size="sm"
                  onClick={isEditing ? handleCancel : () => setIsEditing(true)}
                  isDisabled={updateUserMutation.isLoading}
                >
                  {isEditing ? "Cancel" : "Edit Profile"}
                </Button>
              </VStack>
            </Box>

            {/* Stats */}
            <Box
              bg="#1e293b"
              p={6}
              borderRadius="lg"
              boxShadow="sm"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
            >
              <Heading size="md" color="text" mb={4}>
                Profile Statistics
              </Heading>
              <VStack spacing={3}>
                <HStack justify="space-between" w="full">
                  <Text fontSize="sm" color="#94a3b8">
                    Member since
                  </Text>
                  <Text fontSize="sm" fontWeight="bold" color="white">
                    {new Date(currentUser?.created_at || Date.now()).toLocaleDateString()}
                  </Text>
                </HStack>
                <HStack justify="space-between" w="full">
                  <Text fontSize="sm" color="#94a3b8">
                    Total bids
                  </Text>
                  <Text fontSize="sm" fontWeight="bold" color="white">
                    {userStats.active_bids}
                  </Text>
                </HStack>
                <HStack justify="space-between" w="full">
                  <Text fontSize="sm" color="#94a3b8">
                    Won auctions
                  </Text>
                  <Text fontSize="sm" fontWeight="bold" color="white">
                    {userStats.won_auctions}
                  </Text>
                </HStack>
              </VStack>
            </Box>
          </VStack>

          {/* Right Column - Profile Details */}
          <VStack spacing={6} align="stretch">
            <Box
              bg="#1e293b"
              p={6}
              borderRadius="lg"
              boxShadow="sm"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
            >
              <HStack justify="space-between" mb={4}>
                <Heading size="md" color="text">
                  Profile Information
                </Heading>
                {isEditing && (
                  <Button
                    leftIcon={<CheckIcon />}
                    colorScheme="green"
                    size="sm"
                    onClick={handleSave}
                    isLoading={updateUserMutation.isLoading}
                  >
                    Save Changes
                  </Button>
                )}
              </HStack>
              <VStack spacing={4} align="stretch">
                <Box
                  display="grid"
                  gridTemplateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }}
                  gap={4}
                >
                  <Box>
                    <Text fontWeight="bold" mb={2} color="white">
                      Full Name
                    </Text>
                    <input
                      style={{
                        width: "100%",
                        padding: "8px 12px",
                        border: "1px solid rgba(255,255,255,0.2)",
                        borderRadius: "6px",
                        fontSize: "14px",
                        outline: "none",
                        backgroundColor: isEditing ? "#0f172a" : "#1e293b",
                        color: "white",
                      }}
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      readOnly={!isEditing}
                    />
                  </Box>
                  <Box>
                    <Text fontWeight="bold" mb={2} color="white">
                      Email
                    </Text>
                    <input
                      style={{
                        width: "100%",
                        padding: "8px 12px",
                        border: "1px solid rgba(255,255,255,0.2)",
                        borderRadius: "6px",
                        fontSize: "14px",
                        outline: "none",
                        backgroundColor: isEditing ? "#0f172a" : "#1e293b",
                        color: "white",
                      }}
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      readOnly={!isEditing}
                    />
                  </Box>
                </Box>

                <Box>
                  <Text fontWeight="bold" mb={2} color="white">
                    Auth0 ID
                  </Text>
                  <Text fontSize="sm" color="#94a3b8" fontFamily="monospace">
                    {currentUser?.auth0_sub || "N/A"}
                  </Text>
                </Box>

                <Box>
                  <Text fontWeight="bold" mb={2} color="white">
                    Account Type
                  </Text>
                  <Text fontSize="sm" color="#94a3b8" textTransform="capitalize">
                    {currentUser?.role || "N/A"}
                  </Text>
                </Box>
              </VStack>
            </Box>

            {/* Account Settings */}
            <Box
              bg="#1e293b"
              p={6}
              borderRadius="lg"
              boxShadow="sm"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
            >
              <Heading size="md" color="text" mb={4}>
                Account Settings
              </Heading>
              <VStack spacing={3} align="stretch">
                <Text fontSize="sm" color="#94a3b8">
                  Additional account management features will be available soon.
                </Text>
              </VStack>
            </Box>
          </VStack>
        </Box>
      </Container>
    </Box>
  );
};

export default ProfilePage;
