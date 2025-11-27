import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Box, Container, Heading, Text, Button, VStack, HStack } from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import { artworkService } from "../services/api";
import useAuthStore from "../store/authStore";
import { toaster } from "../components/ui/toaster";

const AddArtworkPage = () => {
  const navigate = useNavigate();
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

  const [selectedImage, setSelectedImage] = useState(null);

  // Create artwork mutation
  const createArtworkMutation = useMutation({
    mutationFn: (artworkData) => artworkService.create(artworkData),
    onSuccess: async (response) => {
      const { data: artwork } = response;

      // If user selected image, upload it
      if (selectedImage) {
        try {
          await artworkService.uploadImage(artwork.id, selectedImage);
          toaster.create({
            title: "Artwork created successfully",
            description: `Your artwork "${artwork.title}" has been listed with image.`,
            type: "success",
            duration: 5000,
          });
        } catch (error) {
          const errorMessage = error?.message || "Image upload failed";
          toaster.create({
            title: "Artwork created but image upload failed",
            description: String(errorMessage),
            type: "warning",
            duration: 5000,
          });
        }
      } else {
        toaster.create({
          title: "Artwork created successfully",
          description: `Your artwork "${artwork.title}" has been listed.`,
          type: "success",
          duration: 5000,
        });
      }

      queryClient.invalidateQueries(["artworks"]);
      queryClient.invalidateQueries(["my-artworks"]);
      navigate(`/artwork/${artwork.id}`);
    },
    onError: (error) => {
      const errorMessage = error?.data?.detail || error?.message || "Failed to create artwork";
      toaster.create({
        title: "Failed to create artwork",
        description: String(errorMessage),
        type: "error",
        duration: 5000,
      });
    },
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

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
    }
  };

  const handleSubmitArtwork = () => {
    // Validate required fields
    if (!newArtwork.title || !newArtwork.secretThreshold) {
      toaster.create({
        title: "Missing required fields",
        description: "Please fill in title and secret threshold",
        type: "warning",
        duration: 3000,
      });
      return;
    }

    // Validate title length
    if (newArtwork.title.length < 3) {
      toaster.create({
        title: "Invalid title",
        description: "Title must be at least 3 characters long",
        type: "warning",
        duration: 3000,
      });
      return;
    }

    if (newArtwork.title.length > 200) {
      toaster.create({
        title: "Invalid title",
        description: "Title cannot exceed 200 characters",
        type: "warning",
        duration: 3000,
      });
      return;
    }

    // Validate description length
    if (newArtwork.description && newArtwork.description.length > 2000) {
      toaster.create({
        title: "Invalid description",
        description: "Description cannot exceed 2000 characters",
        type: "warning",
        duration: 3000,
      });
      return;
    }

    // Validate secret threshold
    const threshold = parseFloat(newArtwork.secretThreshold);
    if (isNaN(threshold) || threshold < 0) {
      toaster.create({
        title: "Invalid secret threshold",
        description: "Secret threshold must be a non-negative number",
        type: "warning",
        duration: 3000,
      });
      return;
    }

    // Validate end date (if provided)
    if (newArtwork.end_date) {
      const endDate = new Date(newArtwork.end_date);
      const now = new Date();
      if (endDate <= now) {
        toaster.create({
          title: "Invalid end date",
          description: "End date must be in the future",
          type: "warning",
          duration: 3000,
        });
        return;
      }
    }

    createArtworkMutation.mutate({
      title: newArtwork.title,
      description: newArtwork.description,
      artist_name: newArtwork.artist_name,
      category: newArtwork.category,
      secret_threshold: threshold,
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
              {/* Image Upload Section */}
              <Box w="full">
                <Text fontWeight="bold" mb={2} color="white">
                  Artwork Image
                </Text>
                <Text fontSize="sm" color="#94a3b8" mb={3}>
                  Upload an image of your artwork (JPEG, PNG, or WebP, max 5MB)
                </Text>
                <Box
                  border="2px dashed"
                  borderColor="rgba(255,255,255,0.2)"
                  borderRadius="md"
                  p={4}
                  textAlign="center"
                  bg="#0f172a"
                >
                  {selectedImage ? (
                    <VStack spacing={3}>
                      <Text fontSize="3xl">✅</Text>
                      <Text color="#94a3b8">{selectedImage.name}</Text>
                      <Text fontSize="sm" color="#64748b">
                        {(selectedImage.size / 1024).toFixed(2)} KB
                      </Text>
                    </VStack>
                  ) : (
                    <VStack spacing={2} py={8}>
                      <Text fontSize="3xl">🖼️</Text>
                      <Text color="#94a3b8">Click to select image</Text>
                      <Text fontSize="sm" color="#64748b">
                        JPEG, PNG, or WebP (max 5MB)
                      </Text>
                    </VStack>
                  )}
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    style={{ display: "none" }}
                    id="artwork-image-input"
                    onChange={handleImageSelect}
                  />
                  <Button
                    as="label"
                    htmlFor="artwork-image-input"
                    size="sm"
                    mt={3}
                    bg="white"
                    color="#1e293b"
                    cursor="pointer"
                    _hover={{
                      bg: "#f1f5f9",
                    }}
                  >
                    {selectedImage ? "Change Image" : "Select Image"}
                  </Button>
                </Box>
              </Box>

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
                  onChange={(e) => setNewArtwork({ ...newArtwork, artist_name: e.target.value })}
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
