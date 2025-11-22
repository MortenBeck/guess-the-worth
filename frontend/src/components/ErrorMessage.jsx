import { Box, Button, HStack, VStack } from "@chakra-ui/react";
import PropTypes from "prop-types";

/**
 * ErrorMessage component for displaying error states with optional retry.
 *
 * Provides user-friendly error messages with contextual styling and
 * optional retry functionality.
 *
 * @param {Object} props
 * @param {Error} props.error - Error object (should have .message, .status, .isNetworkError)
 * @param {Function} props.onRetry - Optional retry callback
 */
export default function ErrorMessage({ error, onRetry }) {
  if (!error) return null;

  const getErrorMessage = () => {
    if (error.isNetworkError) {
      return "Unable to connect to server. Please check your internet connection.";
    }

    if (error.status === 401) {
      return "Your session has expired. Please log in again.";
    }

    if (error.status === 403) {
      return "You do not have permission to access this resource.";
    }

    if (error.status === 404) {
      return "The requested resource was not found.";
    }

    if (error.status === 400) {
      return error.message || "Invalid request. Please check your input.";
    }

    if (error.status >= 500) {
      return "A server error occurred. Please try again later.";
    }

    return error.message || "An unexpected error occurred.";
  };

  const getErrorIcon = () => {
    if (error.isNetworkError) return "⚠️";
    if (error.status === 401 || error.status === 403) return "🔒";
    if (error.status === 404) return "🔍";
    if (error.status >= 500) return "⚙️";
    return "❌";
  };

  return (
    <Box
      bg="rgba(239, 68, 68, 0.1)"
      border="1px"
      borderColor="rgba(239, 68, 68, 0.3)"
      borderRadius="lg"
      p={4}
    >
      <VStack align="stretch" spacing={3}>
        <HStack>
          <Box fontSize="xl">{getErrorIcon()}</Box>
          <Box flex="1">
            <Box fontWeight="bold" color="rgb(252, 165, 165)" mb={1}>
              Error
            </Box>
            <Box color="rgb(252, 165, 165)" fontSize="sm">
              {getErrorMessage()}
            </Box>
          </Box>
        </HStack>
        {onRetry && (
          <Button
            size="sm"
            bg="rgba(239, 68, 68, 0.2)"
            color="rgb(252, 165, 165)"
            _hover={{ bg: "rgba(239, 68, 68, 0.3)" }}
            onClick={onRetry}
          >
            Try Again
          </Button>
        )}
      </VStack>
    </Box>
  );
}

ErrorMessage.propTypes = {
  error: PropTypes.shape({
    message: PropTypes.string,
    status: PropTypes.number,
    isNetworkError: PropTypes.bool,
  }),
  onRetry: PropTypes.func,
};
