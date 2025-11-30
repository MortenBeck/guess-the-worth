import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Elements } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";
import { Box, Container, Heading, Text, VStack, Spinner, Button } from "@chakra-ui/react";
import { toaster } from "../components/ui/toaster";
import CheckoutForm from "../components/CheckoutForm";
import { paymentService } from "../services/api";
import { checkStripeConfig, getStripeErrorMessage } from "../utils/stripeConfig";

const stripeConfig = checkStripeConfig();
const stripePromise = stripeConfig.configured
  ? loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)
  : null;

/**
 * PaymentPage - Dedicated page for Stripe payment checkout
 * Handles payment processing for winning bids
 */
function PaymentPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const bidId = searchParams.get("bidId");
  const amount = searchParams.get("amount");
  const artworkTitle = searchParams.get("artwork");

  const [clientSecret, setClientSecret] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!bidId || !amount) {
      navigate("/dashboard");
      return;
    }

    const createPaymentIntent = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await paymentService.createPaymentIntent(bidId);
        setClientSecret(data.client_secret);
      } catch (err) {
        console.error("Failed to create payment intent:", err);
        const userMessage = getStripeErrorMessage(err);
        setError(userMessage);

        if (err.response?.status === 503) {
          toaster.create({
            title: "Payment Unavailable",
            description: "Payment processing is not configured. Please contact support.",
            type: "error",
            duration: 10000,
          });
        }
      } finally {
        setLoading(false);
      }
    };

    createPaymentIntent();
  }, [bidId, amount, navigate]);

  const handleSuccess = () => {
    toaster.create({
      title: "Payment Processing",
      description: "Your payment is being confirmed. You will be redirected shortly.",
      type: "info",
      duration: 5000,
    });

    setTimeout(() => {
      navigate("/dashboard");
    }, 2000);
  };

  const handleError = (error) => {
    console.error("Payment error:", error);
    const userMessage = getStripeErrorMessage(error);
    setError(userMessage);
  };

  const handleCancel = () => {
    navigate(-1);
  };

  if (!stripeConfig.configured) {
    return (
      <Container maxW="container.md" py={10}>
        <VStack align="stretch" spacing={6}>
          <Heading size="xl" color="red.600">
            Payment Unavailable
          </Heading>
          <Box bg="red.50" border="1px solid" borderColor="red.200" p={6} borderRadius="md">
            <Text fontWeight="bold" mb={2}>
              Stripe is not configured
            </Text>
            <Text mb={2}>Payment processing is currently unavailable.</Text>
            <VStack align="start" spacing={1}>
              {stripeConfig.errors.map((err, index) => (
                <Text key={index} fontSize="sm">
                  • {err}
                </Text>
              ))}
            </VStack>
          </Box>
          <Button onClick={() => navigate("/dashboard")} colorScheme="blue">
            Return to Dashboard
          </Button>
        </VStack>
      </Container>
    );
  }

  const stripeOptions = clientSecret
    ? {
        clientSecret,
        appearance: {
          theme: "stripe",
          variables: {
            colorPrimary: "#2563eb",
          },
        },
      }
    : undefined;

  return (
    <Container maxW="container.md" py={10}>
      <VStack align="stretch" spacing={6}>
        <Box>
          <Heading size="xl" mb={2}>
            Complete Your Payment
          </Heading>
          <Text color="gray.600">
            You won the auction for <strong>{artworkTitle || "this artwork"}</strong>
          </Text>
        </Box>

        <Box bg="blue.50" border="1px solid" borderColor="blue.200" p={6} borderRadius="md">
          <VStack align="start" spacing={3}>
            <Box>
              <Text fontSize="sm" color="gray.600">
                Winning Bid Amount
              </Text>
              <Text fontSize="3xl" fontWeight="bold" color="blue.600">
                ${parseFloat(amount || 0).toLocaleString()}
              </Text>
            </Box>
            <Text fontSize="sm" color="gray.600">
              Complete your payment below to finalize your purchase
            </Text>
          </VStack>
        </Box>

        {loading && (
          <Box textAlign="center" py={8}>
            <Spinner size="xl" color="blue.500" mb={4} />
            <Text>Initializing payment...</Text>
          </Box>
        )}

        {error && (
          <Box bg="red.50" border="1px solid" borderColor="red.200" p={4} borderRadius="md">
            <Text color="red.800" fontWeight="medium">
              {error}
            </Text>
          </Box>
        )}

        {!loading && !error && clientSecret && stripePromise && (
          <Elements stripe={stripePromise} options={stripeOptions}>
            <CheckoutForm
              amount={parseFloat(amount || 0)}
              artworkTitle={artworkTitle || "Artwork"}
              onSuccess={handleSuccess}
              onError={handleError}
            />
          </Elements>
        )}

        <Button onClick={handleCancel} variant="outline" colorScheme="gray">
          Cancel and Return
        </Button>
      </VStack>
    </Container>
  );
}

export default PaymentPage;
