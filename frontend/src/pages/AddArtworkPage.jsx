import { useState } from "react";
import { Box, Container, Heading, Text, Button, VStack, HStack } from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";

const AddArtworkPage = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [newArtwork, setNewArtwork] = useState({
    title: "",
    description: "",
    secretThreshold: "",
    category: "",
    medium: "",
    dimensions: "",
    yearCreated: "",
  });

  const handleSubmitArtwork = () => {
    // Handle artwork submission
    console.log("Submitting artwork:", newArtwork);
    // TODO: API call to create artwork
    // After success, navigate back to seller dashboard
    navigate("/seller-dashboard");
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
                  value={newArtwork.secretThreshold}
                  onChange={(e) =>
                    setNewArtwork({ ...newArtwork, secretThreshold: e.target.value })
                  }
                  placeholder="e.g., 500"
                />
              </Box>

              <Box display="grid" gridTemplateColumns="repeat(2, 1fr)" gap={4} w="full">
                <Box>
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
                    placeholder="e.g., Painting"
                  />
                </Box>
                <Box>
                  <Text fontWeight="bold" mb={2} color="white">
                    Medium
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
                    value={newArtwork.medium}
                    onChange={(e) => setNewArtwork({ ...newArtwork, medium: e.target.value })}
                    placeholder="e.g., Oil on Canvas"
                  />
                </Box>
              </Box>

              <Box display="grid" gridTemplateColumns="repeat(2, 1fr)" gap={4} w="full">
                <Box>
                  <Text fontWeight="bold" mb={2} color="white">
                    Dimensions
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
                    value={newArtwork.dimensions}
                    onChange={(e) => setNewArtwork({ ...newArtwork, dimensions: e.target.value })}
                    placeholder="e.g., 24 x 36 inches"
                  />
                </Box>
                <Box>
                  <Text fontWeight="bold" mb={2} color="white">
                    Year Created
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
                    value={newArtwork.yearCreated}
                    onChange={(e) => setNewArtwork({ ...newArtwork, yearCreated: e.target.value })}
                    placeholder="2024"
                  />
                </Box>
              </Box>

              <Box w="full">
                <Text fontWeight="bold" mb={2} color="white">
                  Upload Image
                </Text>
                <input
                  type="file"
                  accept="image/*"
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
