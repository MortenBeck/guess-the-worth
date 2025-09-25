import { Box, Container, Heading, Text, VStack, SimpleGrid, Button, HStack } from '@chakra-ui/react'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'

const HelpPage = () => {
  const navigate = useNavigate()
  const [expandedFaq, setExpandedFaq] = useState(null)

  const faqs = [
    {
      question: "How does the bidding system work?",
      answer: "Our unique secret threshold bidding system allows artists to set a hidden minimum price. When your bid meets or exceeds this secret threshold, you instantly win the artwork - no waiting, no outbidding!"
    },
    {
      question: "When will I know if I've won?",
      answer: "You'll know immediately! As soon as your bid reaches the artist's secret threshold, you'll receive an instant confirmation that you've won the artwork."
    },
    {
      question: "What happens if I don't hit the threshold?",
      answer: "If your bid is below the threshold, it will be recorded but you won't win the artwork. You can place additional bids until someone hits the threshold or the auction ends."
    },
    {
      question: "How do I know what to bid?",
      answer: "That's the exciting part! Use your intuition and knowledge of art to guess what the piece is worth to the artist. Look at similar works, the artist's reputation, and your personal connection to the piece."
    },
    {
      question: "Are there any fees?",
      answer: "We charge a small transaction fee only when you successfully win an artwork. There are no fees for browsing, bidding, or registering."
    },
    {
      question: "How do I get my artwork after winning?",
      answer: "Once you win, you'll receive instructions for payment and shipping. Most artworks are shipped within 5-7 business days after payment confirmation."
    },
    {
      question: "Can I cancel a bid?",
      answer: "Unfortunately, all bids are final once placed. This ensures fairness for all participants and maintains the integrity of our auction system."
    },
    {
      question: "What if there's an issue with my artwork?",
      answer: "We have a 14-day return policy for damaged or misrepresented items. Contact our support team immediately if you encounter any issues."
    }
  ]

  const supportCategories = [
    {
      title: "Getting Started",
      description: "New to the platform? Learn the basics",
      icon: "🚀"
    },
    {
      title: "Bidding Help",
      description: "Understand our unique bidding system",
      icon: "💰"
    },
    {
      title: "Account Issues",
      description: "Profile, settings, and login help",
      icon: "👤"
    },
    {
      title: "Payment & Shipping",
      description: "Questions about transactions",
      icon: "📦"
    }
  ]

  return (
    <Box bg="#0f172a" minH="100vh" color="white">
      <Container maxW="7xl" py={8}>
        <VStack spacing={12} align="stretch">
          {/* Header */}
          <Box textAlign="center">
            <Heading size="3xl" mb={4} background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)" backgroundClip="text" color="transparent">
              Help & Support
            </Heading>
            <Text color="#94a3b8" fontSize="xl" maxW="600px" mx="auto">
              Get help with bidding, account issues, and everything else you need to know about Guess The Worth
            </Text>
          </Box>

          {/* Quick Help Categories */}
          <Box>
            <Heading size="lg" color="white" mb={6}>Quick Help</Heading>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
              {supportCategories.map((category, index) => (
                <Box
                  key={index}
                  bg="#1e293b"
                  p={6}
                  borderRadius="xl"
                  textAlign="center"
                  cursor="pointer"
                  border="1px solid"
                  borderColor="rgba(255,255,255,0.1)"
                  _hover={{
                    transform: "translateY(-2px)",
                    boxShadow: "0 8px 25px rgba(0,0,0,0.2)",
                    borderColor: "rgba(99, 102, 241, 0.3)"
                  }}
                  transition="all 0.3s ease"
                >
                  <VStack spacing={4}>
                    <Text fontSize="3xl">{category.icon}</Text>
                    <VStack spacing={2}>
                      <Heading size="md" color="white">{category.title}</Heading>
                      <Text fontSize="sm" color="#94a3b8" textAlign="center">
                        {category.description}
                      </Text>
                    </VStack>
                  </VStack>
                </Box>
              ))}
            </SimpleGrid>
          </Box>

          {/* FAQ Section */}
          <Box>
            <Heading size="lg" color="white" mb={6}>Frequently Asked Questions</Heading>
            <VStack spacing={4} align="stretch">
              {faqs.map((faq, index) => (
                <Box
                  key={index}
                  bg="#1e293b"
                  borderRadius="xl"
                  border="1px solid"
                  borderColor="rgba(255,255,255,0.1)"
                  overflow="hidden"
                >
                  <Button
                    w="full"
                    p={6}
                    bg="transparent"
                    color="white"
                    fontWeight="medium"
                    textAlign="left"
                    justifyContent="space-between"
                    _hover={{ bg: "rgba(255,255,255,0.05)" }}
                    onClick={() => setExpandedFaq(expandedFaq === index ? null : index)}
                    rightIcon={<Text>{expandedFaq === index ? '▲' : '▼'}</Text>}
                    borderRadius="none"
                  >
                    {faq.question}
                  </Button>
                  {expandedFaq === index && (
                    <Box p={6} pt={0}>
                      <Text color="#94a3b8" lineHeight="1.6">
                        {faq.answer}
                      </Text>
                    </Box>
                  )}
                </Box>
              ))}
            </VStack>
          </Box>

          {/* Contact Section */}
          <Box
            bg="#1e293b"
            p={8}
            borderRadius="xl"
            border="1px solid"
            borderColor="rgba(255,255,255,0.1)"
            textAlign="center"
          >
            <VStack spacing={6}>
              <VStack spacing={3}>
                <Text fontSize="2xl">💬</Text>
                <Heading size="lg" color="white">Still Need Help?</Heading>
                <Text color="#94a3b8" maxW="500px">
                  Can't find what you're looking for? Our support team is here to help you with any questions or issues.
                </Text>
              </VStack>

              <HStack spacing={4} wrap="wrap" justify="center">
                <Button
                  background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
                  color="white"
                  size="lg"
                  onClick={() => window.location.href = 'mailto:support@guesstheworth.com'}
                  _hover={{
                    transform: "translateY(-1px)",
                    boxShadow: "0 4px 15px rgba(99, 102, 241, 0.3)",
                  }}
                  transition="all 0.2s"
                >
                  Email Support
                </Button>

                <Button
                  variant="outline"
                  borderColor="#334155"
                  color="#94a3b8"
                  bg="transparent"
                  size="lg"
                  onClick={() => navigate('/artworks')}
                  _hover={{
                    bg: "#334155",
                    color: "white"
                  }}
                  transition="all 0.2s"
                >
                  Browse Artworks
                </Button>
              </HStack>

              <Text fontSize="sm" color="#94a3b8">
                Response time: Usually within 24 hours
              </Text>
            </VStack>
          </Box>
        </VStack>
      </Container>
    </Box>
  )
}

export default HelpPage