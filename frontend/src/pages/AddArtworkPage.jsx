import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Box, Container, Heading, Text, Button, VStack, HStack, useToast } from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import { artworkService } from "../services/api";
import useAuthStore from "../store/authStore";

const AddArtworkPage = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const queryClient = useQueryClient();
  const { isSeller, isAdmin } = useAuthStore();

  const [newArtwork, setNewArtwork] = useState({
    title: "",
    description: "",
    artist_name: "",
    secretThreshold: "",
    category: "",
    end_date: "",
  });

  // Check if user is allowed to create artwork
  if (!isSeller() && !isAdmin()) {
    return (
      <Box bg="#0f172a" minH="100vh" color="white">
        <Container maxW="container.md" py={8}>
          <Box textAlign="center" p={8}>
            <Heading size="lg" color="white" mb={4}>
              Access Denied
            </Heading>
            <Text color="#94a3b8" mb={6}>
              You must be a seller to create artworks.
            </Text>
            <Button onClick={() => navigate("/")}>Go Home</Button>
          </Box>
        </Container>
      </Box>
    );
  }

  // Create artwork mutation
  const createArtworkMutation = useMutation({
    mutationFn: (artworkData) => artworkService.create(artworkData),
    onSuccess: (response) => {
      const { data: artwork } = response;
      toast({
        title: "Artwork created successfully",
        description: `Your artwork "${artwork.title}" has been listed.`,
        status: "success",
        duration: 5000,
        isClosable: true,
      });
      queryClient.invalidateQueries(["artworks"]);
      navigate(`/artwork/${artwork.id}`);
    },
    onError: (error) => {
      toast({
        title: "Failed to create artwork",
        description: error.response?.data?.detail || error.message,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    },
  });

  const handleSubmitArtwork = () => {
    if (!newArtwork.title || !newArtwork.secretThreshold) {
      toast({
        title: "Missing required fields",
        description: "Please fill in title and secret threshold",
        status: "warning",
        duration: 3000,
      });
      return;
    }

    createArtworkMutation.mutate({
      title: newArtwork.title,
      description: newArtwork.description,
      artist_name: newArtwork.artist_name,
      category: newArtwork.category,
      secret_threshold: parseFloat(newArtwork.secretThreshold),
      end_date: newArtwork.end_date ? new Date(newArtwork.end_date).toISOString() : null,
    });
  };

  return (
    <Box bg="#0f172a" minH="100vh" color="white">
      <Container maxW="container.md" py={8}>
        <VStack spacing={8} align="stretch">
          <Box>
            <Heading size="xl" color="white" mb={2}>
              List New Artwork
            </Heading>
            <Text color="#94a3b8">Set your secret threshold and list your artwork for auction</Text>
          </Box>

          <Box
            bg="#1e293b"
            p={6}
            borderRadius="lg"
            boxShadow="sm"
            border="1px"
            borderColor="rgba(255,255,255,0.1)"
          >
            <VStack spacing={6}>
              <Box w="full">
                <Text fontWeight="bold" mb={2} color="white">
                  Title *
                </Text>
                <input
                  style={{
                    width: "100%",
                    padding: "12px",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "6px",
                    fontSize: "16px",
                    outline: "none",
                    backgroundColor: "#0f172a",
                    color: "white",
                  }}
                  value={newArtwork.title}
                  onChange={(e) => setNewArtwork({ ...newArtwork, title: e.target.value })}
                  placeholder="Enter artwork title"
                />
              </Box>

              <Box w="full">
                <Text fontWeight="bold" mb={2} color="white">
                  Description
                </Text>
                <textarea
                  style={{
                    width: "100%",
                    padding: "12px",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "6px",
                    fontSize: "16px",
                    outline: "none",
                    minHeight: "120px",
                    fontFamily: "inherit",
                    backgroundColor: "#0f172a",
                    color: "white",
                  }}
                  value={newArtwork.description}
                  onChange={(e) => setNewArtwork({ ...newArtwork, description: e.target.value })}
                  placeholder="Describe your artwork"
                />
              </Box>

              <Box w="full">
                <Text fontWeight="bold" mb={2} color="white">
                  Artist Name
                </Text>
                <input
                  style={{
                    width: "100%",
                    padding: "12px",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "6px",
                    fontSize: "16px",
                    outline: "none",
                    backgroundColor: "#0f172a",
                    color: "white",
                  }}
                  value={newArtwork.artist_name}
                  onChange={(e) =>
                    setNewArtwork({ ...newArtwork, artist_name: e.target.value })
                  }
                  placeholder="Enter artist name"
                />
              </Box>

              <Box w="full">
                <Text fontWeight="bold" mb={2} color="white">
                  Category
                </Text>
                <input
                  style={{
                    width: "100%",
                    padding: "12px",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "6px",
                    fontSize: "16px",
                    outline: "none",
                    backgroundColor: "#0f172a",
                    color: "white",
                  }}
                  value={newArtwork.category}
                  onChange={(e) => setNewArtwork({ ...newArtwork, category: e.target.value })}
                  placeholder="e.g., Painting, Photography, Sculpture"
                />
              </Box>

              <Box w="full">
                <Text fontWeight="bold" mb={2} color="white">
                  Secret Threshold ($) *
                </Text>
                <Text fontSize="sm" color="#94a3b8" mb={2}>
                  This is your hidden buyout price. When a bid reaches this amount, the artwork
                  sells instantly.
                </Text>
                <input
                  style={{
                    width: "100%",
                    padding: "12px",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "6px",
                    fontSize: "16px",
                    outline: "none",
                    backgroundColor: "#0f172a",
                    color: "white",
                  }}
                  type="number"
                  step="0.01"
                  value={newArtwork.secretThreshold}
                  onChange={(e) =>
                    setNewArtwork({ ...newArtwork, secretThreshold: e.target.value })
                  }
                  placeholder="e.g., 500"
                />
              </Box>

              <Box w="full">
                <Text fontWeight="bold" mb={2} color="white">
                  End Date (Optional)
                </Text>
                <Text fontSize="sm" color="#94a3b8" mb={2}>
                  Set when the auction should end
                </Text>
                <input
                  style={{
                    width: "100%",
                    padding: "12px",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "6px",
                    fontSize: "16px",
                    outline: "none",
                    backgroundColor: "#0f172a",
                    color: "white",
                  }}
                  type="datetime-local"
                  value={newArtwork.end_date}
                  onChange={(e) => setNewArtwork({ ...newArtwork, end_date: e.target.value })}
                />
              </Box>

              <HStack spacing={3} w="full" justify="end" pt={4}>
                <Button
                  variant="outline"
                  borderColor="rgba(255,255,255,0.1)"
                  color="#94a3b8"
                  size="lg"
                  _hover={{ bg: "#0f172a", borderColor: "rgba(255,255,255,0.2)" }}
                  onClick={() => navigate("/seller-dashboard")}
                >
                  Cancel
                </Button>
                <Button
                  bg="white"
                  color="#1e293b"
                  size="lg"
                  _hover={{
                    bg: "#f1f5f9",
                    transform: "translateY(-1px)",
                  }}
                  transition="all 0.2s"
                  onClick={handleSubmitArtwork}
                  isLoading={createArtworkMutation.isLoading}
                  isDisabled={!newArtwork.title || !newArtwork.secretThreshold}
                >
                  List Artwork
                </Button>
              </HStack>
            </VStack>
          </Box>
        </VStack>
      </Container>
    </Box>
  );
};

export default AddArtworkPage;
