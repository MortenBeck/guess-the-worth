import { useState, useEffect } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Alert,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react'
// Simple custom icons
const CheckIcon = () => <span>✓</span>
const WarningIcon = () => <span>⚠️</span>
const InfoIcon = () => <span>ℹ️</span>
import socketService from '../services/socket'

const NotificationSystem = () => {
  const [notifications, setNotifications] = useState([])

  useEffect(() => {
    const handleNotification = (notification) => {
      const newNotification = {
        id: Date.now() + Math.random(),
        ...notification,
        timestamp: new Date(),
      }
      
      setNotifications(prev => [newNotification, ...prev.slice(0, 4)]) // Keep max 5 notifications
      
      // Auto remove after 5 seconds
      setTimeout(() => {
        removeNotification(newNotification.id)
      }, 5000)
    }

    // Listen for various notification types
    socketService.on('bid_placed', (data) => {
      handleNotification({
        type: 'info',
        title: 'New Bid Placed',
        message: `A bid of $${data.amount} was placed on "${data.artworkTitle}"`,
      })
    })

    socketService.on('bid_won', (data) => {
      handleNotification({
        type: 'success',
        title: 'Congratulations!',
        message: `You won the artwork "${data.artworkTitle}" with your bid of $${data.amount}!`,
      })
    })

    socketService.on('auction_ended', (data) => {
      handleNotification({
        type: 'warning',
        title: 'Auction Ended',
        message: `The auction for "${data.artworkTitle}" has ended.`,
      })
    })

    socketService.on('new_artwork', (data) => {
      handleNotification({
        type: 'info',
        title: 'New Artwork Available',
        message: `"${data.title}" by ${data.artist} is now available for bidding!`,
      })
    })

    return () => {
      socketService.off('bid_placed')
      socketService.off('bid_won')
      socketService.off('auction_ended')
      socketService.off('new_artwork')
    }
  }, [])

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id))
  }

  const getAlertStatus = (type) => {
    switch (type) {
      case 'success': return 'success'
      case 'error': return 'error'
      case 'warning': return 'warning'
      default: return 'info'
    }
  }

  return (
    <Box
      position="fixed"
      top="80px"
      right="4"
      zIndex={2000}
      maxW="400px"
      w="full"
    >
      <VStack spacing={2} align="stretch">
        {notifications.map((notification) => (
          <Alert
            key={notification.id}
            status={getAlertStatus(notification.type)}
            variant="solid"
            borderRadius="md"
            boxShadow="lg"
          >
            <Text fontSize="lg" mr={2}>
              {notification.type === 'success' ? '✅' : 
               notification.type === 'error' ? '❌' : 
               notification.type === 'warning' ? '⚠️' : 'ℹ️'}
            </Text>
            <Box flex="1">
              <AlertTitle fontSize="sm">
                {notification.title}
              </AlertTitle>
              <AlertDescription fontSize="xs">
                {notification.message}
              </AlertDescription>
            </Box>
            <CloseButton
              size="sm"
              onClick={() => removeNotification(notification.id)}
            />
          </Alert>
        ))}
      </VStack>
    </Box>
  )
}

export default NotificationSystem