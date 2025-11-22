import { useState, useRef } from 'react';
import { Box, Button, Image, Text, Progress, useToast, VStack } from '@chakra-ui/react';
import { artworkService } from '../services/api';

export default function ImageUpload({ artworkId, currentImageUrl, onUploadSuccess }) {
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState(currentImageUrl);
  const fileInputRef = useRef(null);
  const toast = useToast();

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      toast({
        title: 'Invalid file type',
        description: 'Please upload a JPEG, PNG, or WebP image',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast({
        title: 'File too large',
        description: 'Maximum file size is 5MB',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(file);

    // Upload to backend
    setUploading(true);
    try {
      const result = await artworkService.uploadImage(artworkId, file);
      toast({
        title: 'Image uploaded successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      if (onUploadSuccess) onUploadSuccess(result.data?.image_url);
    } catch (error) {
      toast({
        title: 'Upload failed',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      // Revert preview on error
      setPreview(currentImageUrl);
    } finally {
      setUploading(false);
    }
  };

  return (
    <VStack spacing={3} w="full">
      <Box
        border="2px dashed"
        borderColor="rgba(255,255,255,0.2)"
        borderRadius="md"
        p={4}
        textAlign="center"
        cursor="pointer"
        onClick={() => fileInputRef.current?.click()}
        w="full"
        bg="#0f172a"
        _hover={{
          borderColor: "rgba(255,255,255,0.4)",
          bg: "#1e293b",
        }}
        transition="all 0.2s"
      >
        {preview ? (
          <Image
            src={preview}
            maxH="300px"
            mx="auto"
            borderRadius="md"
            objectFit="cover"
          />
        ) : (
          <VStack spacing={2} py={8}>
            <Text fontSize="3xl">🖼️</Text>
            <Text color="#94a3b8">Click to upload image</Text>
            <Text fontSize="sm" color="#64748b">
              JPEG, PNG, or WebP (max 5MB)
            </Text>
          </VStack>
        )}
      </Box>

      <input
        type="file"
        ref={fileInputRef}
        accept="image/jpeg,image/png,image/webp"
        style={{ display: 'none' }}
        onChange={handleFileSelect}
      />

      {uploading && (
        <Progress
          isIndeterminate
          size="xs"
          w="full"
          colorScheme="blue"
        />
      )}

      <Button
        size="sm"
        onClick={() => fileInputRef.current?.click()}
        isLoading={uploading}
        bg="white"
        color="#1e293b"
        _hover={{
          bg: "#f1f5f9",
        }}
      >
        {preview ? 'Change Image' : 'Upload Image'}
      </Button>
    </VStack>
  );
}
