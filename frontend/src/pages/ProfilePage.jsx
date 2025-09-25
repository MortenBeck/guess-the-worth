import { useState } from 'react'
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
} from '@chakra-ui/react'
// Simple custom icons
const EditIcon = () => <span>✏️</span>
const CheckIcon = () => <span>✓</span>
const CloseIcon = () => <span>✕</span>
import useAuthStore from '../store/authStore'
import placeholderImg from '../assets/placeholder.jpg'

const ProfilePage = () => {
  const { user } = useAuthStore()
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    bio: 'Art enthusiast and collector with a passion for contemporary works.',
    location: 'New York, NY',
    website: 'https://myartblog.com',
    phone: '+1 (555) 123-4567'
  })
  const [notifications, setNotifications] = useState({
    bidUpdates: true,
    auctionReminders: true,
    newArtworks: false,
    priceAlerts: true,
    marketingEmails: false
  })

  // Mock user statistics
  const userStats = {
    joinDate: '2023-06-15',
    totalBids: 45,
    wonAuctions: 8,
    savedArtworks: 23,
    rating: 4.8,
    verificationStatus: 'verified'
  }

  const recentActivity = [
    {
      id: 1,
      type: 'bid',
      description: 'Placed bid on "Sunset Dreams"',
      amount: 175,
      date: '2024-01-15'
    },
    {
      id: 2,
      type: 'win',
      description: 'Won auction for "Mountain Peak"',
      amount: 450,
      date: '2024-01-10'
    },
    {
      id: 3,
      type: 'save',
      description: 'Added "Ocean Waves" to watchlist',
      date: '2024-01-08'
    }
  ]

  const handleSave = () => {
    // Handle profile update
    // Show success message (replaced toast with console.log for now)
    console.log("Profile updated successfully")
    setIsEditing(false)
  }

  const handleCancel = () => {
    // Reset form data
    setFormData({
      name: user?.name || '',
      email: user?.email || '',
      bio: 'Art enthusiast and collector with a passion for contemporary works.',
      location: 'New York, NY',
      website: 'https://myartblog.com',
      phone: '+1 (555) 123-4567'
    })
    setIsEditing(false)
  }

  const getActivityIcon = (type) => {
    switch (type) {
      case 'bid': return '🔨'
      case 'win': return '🏆'
      case 'save': return '❤️'
      default: return '📝'
    }
  }

  const handleNotificationChange = (key, value) => {
    setNotifications(prev => ({
      ...prev,
      [key]: value
    }))
  }

  return (
    <Box bg="#0f172a" minH="100vh" color="white">
      <Container maxW="container.xl" py={8}>
        <Box display="grid" gridTemplateColumns={{ base: "1fr", lg: "1fr 2fr" }} gap={8}>
        {/* Left Column - Profile Info */}
        <VStack spacing={6} align="stretch">
          <Box bg="#1e293b" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="rgba(255,255,255,0.1)" textAlign="center">
            <VStack spacing={4}>
              <Image
                w="120px"
                h="120px"
                borderRadius="full"
                src={user?.picture || placeholderImg}
                alt={user?.name}
                objectFit="cover"
              />
              <VStack spacing={1}>
                <Heading size="lg" color="text">{user?.name}</Heading>
                <HStack>
                  <Badge colorScheme="primary" textTransform="capitalize">
                    {user?.role}
                  </Badge>
                  <Badge colorScheme="green">
                    {userStats.verificationStatus}
                  </Badge>
                </HStack>
                <Text color="#94a3b8">{formData.location}</Text>
              </VStack>
              
              <Button
                leftIcon={isEditing ? <CloseIcon /> : <EditIcon />}
                colorScheme={isEditing ? "gray" : "primary"}
                variant={isEditing ? "outline" : "solid"}
                size="sm"
                onClick={isEditing ? handleCancel : () => setIsEditing(true)}
              >
                {isEditing ? 'Cancel' : 'Edit Profile'}
              </Button>
            </VStack>
          </Box>

          {/* Stats */}
          <Box bg="#1e293b" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="rgba(255,255,255,0.1)">
            <Heading size="md" color="text" mb={4}>Profile Statistics</Heading>
            <VStack spacing={3}>
              <HStack justify="space-between" w="full">
                <Text fontSize="sm">Member since</Text>
                <Text fontSize="sm" fontWeight="bold">
                  {new Date(userStats.joinDate).toLocaleDateString()}
                </Text>
              </HStack>
              <HStack justify="space-between" w="full">
                <Text fontSize="sm">Total bids</Text>
                <Text fontSize="sm" fontWeight="bold">{userStats.totalBids}</Text>
              </HStack>
              <HStack justify="space-between" w="full">
                <Text fontSize="sm">Won auctions</Text>
                <Text fontSize="sm" fontWeight="bold">{userStats.wonAuctions}</Text>
              </HStack>
              <HStack justify="space-between" w="full">
                <Text fontSize="sm">Saved artworks</Text>
                <Text fontSize="sm" fontWeight="bold">{userStats.savedArtworks}</Text>
              </HStack>
              <HStack justify="space-between" w="full">
                <Text fontSize="sm">Rating</Text>
                <Text fontSize="sm" fontWeight="bold">⭐ {userStats.rating}/5</Text>
              </HStack>
            </VStack>
          </Box>
        </VStack>

        {/* Right Column - Profile Details */}
        <VStack spacing={6} align="stretch">
          <Box bg="#1e293b" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="rgba(255,255,255,0.1)">
            <HStack justify="space-between" mb={4}>
              <Heading size="md" color="text">Profile Information</Heading>
              {isEditing && (
                <Button
                  leftIcon={<CheckIcon />}
                  colorScheme="green"
                  size="sm"
                  onClick={handleSave}
                >
                  Save Changes
                </Button>
              )}
            </HStack>
            <VStack spacing={4} align="stretch">
              <Box display="grid" gridTemplateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={4}>
                <Box>
                  <Text fontWeight="bold" mb={2}>Full Name</Text>
                  <input
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid #e2e8f0',
                      borderRadius: '6px',
                      fontSize: '14px',
                      outline: 'none',
                      backgroundColor: isEditing ? 'white' : '#f7fafc'
                    }}
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    readOnly={!isEditing}
                  />
                </Box>
                <Box>
                  <Text fontWeight="bold" mb={2}>Email</Text>
                  <input
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid #e2e8f0',
                      borderRadius: '6px',
                      fontSize: '14px',
                      outline: 'none',
                      backgroundColor: isEditing ? 'white' : '#f7fafc'
                    }}
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    readOnly={!isEditing}
                  />
                </Box>
              </Box>
              
              <Box>
                <Text fontWeight="bold" mb={2}>Bio</Text>
                <textarea
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '6px',
                    fontSize: '14px',
                    outline: 'none',
                    minHeight: '80px',
                    fontFamily: 'inherit',
                    backgroundColor: isEditing ? 'white' : '#f7fafc'
                  }}
                  value={formData.bio}
                  onChange={(e) => setFormData({...formData, bio: e.target.value})}
                  readOnly={!isEditing}
                  rows={3}
                />
              </Box>
              
              <Box display="grid" gridTemplateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={4}>
                <Box>
                  <Text fontWeight="bold" mb={2}>Location</Text>
                  <input
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid #e2e8f0',
                      borderRadius: '6px',
                      fontSize: '14px',
                      outline: 'none',
                      backgroundColor: isEditing ? 'white' : '#f7fafc'
                    }}
                    value={formData.location}
                    onChange={(e) => setFormData({...formData, location: e.target.value})}
                    readOnly={!isEditing}
                  />
                </Box>
                <Box>
                  <Text fontWeight="bold" mb={2}>Phone</Text>
                  <input
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid #e2e8f0',
                      borderRadius: '6px',
                      fontSize: '14px',
                      outline: 'none',
                      backgroundColor: isEditing ? 'white' : '#f7fafc'
                    }}
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    readOnly={!isEditing}
                  />
                </Box>
              </Box>
              
              <Box>
                <Text fontWeight="bold" mb={2}>Website</Text>
                <input
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '6px',
                    fontSize: '14px',
                    outline: 'none',
                    backgroundColor: isEditing ? 'white' : '#f7fafc'
                  }}
                  value={formData.website}
                  onChange={(e) => setFormData({...formData, website: e.target.value})}
                  readOnly={!isEditing}
                />
              </Box>
            </VStack>
          </Box>

          {/* Notification Preferences */}
          <Box bg="#1e293b" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="rgba(255,255,255,0.1)">
            <Heading size="md" color="text" mb={4}>Notification Preferences</Heading>
            <VStack spacing={4} align="stretch">
              <HStack justify="space-between">
                <VStack align="start" spacing={0}>
                  <Text fontWeight="medium">Bid Updates</Text>
                  <Text fontSize="sm" color="#94a3b8">Get notified when you're outbid</Text>
                </VStack>
                <Button
                  size="sm"
                  colorScheme={notifications.bidUpdates ? "green" : "gray"}
                  onClick={() => handleNotificationChange('bidUpdates', !notifications.bidUpdates)}
                >
                  {notifications.bidUpdates ? 'On' : 'Off'}
                </Button>
              </HStack>
              
              <HStack justify="space-between">
                <VStack align="start" spacing={0}>
                  <Text fontWeight="medium">Auction Reminders</Text>
                  <Text fontSize="sm" color="#94a3b8">Reminders before auctions end</Text>
                </VStack>
                <Button
                  size="sm"
                  colorScheme={notifications.auctionReminders ? "green" : "gray"}
                  onClick={() => handleNotificationChange('auctionReminders', !notifications.auctionReminders)}
                >
                  {notifications.auctionReminders ? 'On' : 'Off'}
                </Button>
              </HStack>
              
              <HStack justify="space-between">
                <VStack align="start" spacing={0}>
                  <Text fontWeight="medium">New Artworks</Text>
                  <Text fontSize="sm" color="#94a3b8">Notify when new artworks are added</Text>
                </VStack>
                <Button
                  size="sm"
                  colorScheme={notifications.newArtworks ? "green" : "gray"}
                  onClick={() => handleNotificationChange('newArtworks', !notifications.newArtworks)}
                >
                  {notifications.newArtworks ? 'On' : 'Off'}
                </Button>
              </HStack>
              
              <HStack justify="space-between">
                <VStack align="start" spacing={0}>
                  <Text fontWeight="medium">Price Alerts</Text>
                  <Text fontSize="sm" color="#94a3b8">Alert when watched items hit target price</Text>
                </VStack>
                <Button
                  size="sm"
                  colorScheme={notifications.priceAlerts ? "green" : "gray"}
                  onClick={() => handleNotificationChange('priceAlerts', !notifications.priceAlerts)}
                >
                  {notifications.priceAlerts ? 'On' : 'Off'}
                </Button>
              </HStack>
              
              <HStack justify="space-between">
                <VStack align="start" spacing={0}>
                  <Text fontWeight="medium">Marketing Emails</Text>
                  <Text fontSize="sm" color="#94a3b8">Receive promotional emails</Text>
                </VStack>
                <Button
                  size="sm"
                  colorScheme={notifications.marketingEmails ? "green" : "gray"}
                  onClick={() => handleNotificationChange('marketingEmails', !notifications.marketingEmails)}
                >
                  {notifications.marketingEmails ? 'On' : 'Off'}
                </Button>
              </HStack>
            </VStack>
          </Box>

          {/* Recent Activity */}
          <Box bg="#1e293b" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="rgba(255,255,255,0.1)">
            <Heading size="md" color="text" mb={4}>Recent Activity</Heading>
            <VStack spacing={3} align="stretch">
              {recentActivity.map((activity) => (
                <HStack key={activity.id} spacing={3} p={3} bg="gray.50" borderRadius="md">
                  <Text fontSize="lg">{getActivityIcon(activity.type)}</Text>
                  <VStack align="start" spacing={0} flex={1}>
                    <Text fontSize="sm" fontWeight="medium">{activity.description}</Text>
                    <Text fontSize="xs" color="#94a3b8">
                      {new Date(activity.date).toLocaleDateString()}
                    </Text>
                  </VStack>
                  {activity.amount && (
                    <Text fontSize="sm" fontWeight="bold" color="primary">
                      ${activity.amount}
                    </Text>
                  )}
                </HStack>
              ))}
            </VStack>
          </Box>

          {/* Account Settings */}
          <Box bg="#1e293b" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="rgba(255,255,255,0.1)">
            <Heading size="md" color="text" mb={4}>Account Settings</Heading>
            <VStack spacing={3} align="stretch">
              <Button variant="outline" colorScheme="primary">
                Change Password
              </Button>
              <Button variant="outline" colorScheme="yellow">
                Download My Data
              </Button>
              <Box h="1px" bg="rgba(255,255,255,0.1)" />
              <Button variant="outline" colorScheme="red">
                Delete Account
              </Button>
            </VStack>
          </Box>
        </VStack>
        </Box>
      </Container>
    </Box>
  )
}

export default ProfilePage