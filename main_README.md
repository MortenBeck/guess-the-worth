# Guess The Worth

A web application for an artist collective selling paintings through an innovative "bid what you want" system with secret price thresholds. Built as a comprehensive DevOps course project demonstrating full-stack development, containerization, CI/CD, and modern deployment practices.

## Installation Guide

### Prerequisites
- **macOS**: Install [Homebrew](https://brew.sh)
- **Windows**: Install [Chocolatey](https://chocolatey.org) or use Windows Package Manager
- Git installed on your system

### Installation Steps

#### macOS
```bash
# Install Docker
brew install --cask docker

# Install Node.js and npm
brew install node

# Install Python 3.9+
brew install python

# Clone the repository
git clone <repository-url>
cd guess-the-worth

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Start the application with Docker
cd ..
docker-compose up
```

#### Windows
```bash
# Install Docker Desktop
choco install docker-desktop
# OR
winget install Docker.DockerDesktop

# Install Node.js and npm
choco install nodejs
# OR
winget install OpenJS.NodeJS

# Install Python 3.9+
choco install python
# OR
winget install Python.Python.3

# Clone the repository
git clone <repository-url>
cd guess-the-worth

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Start the application with Docker
cd ..
docker-compose up
```

### Environment Setup
1. Copy `.env.example` to `.env` in both backend and frontend directories
2. Configure your database, Auth0, and Stripe credentials
3. Access the application at `http://localhost:3000`

## Project Structure

```
guess-the-worth/
├── backend/                    # FastAPI backend application
│   ├── config/                # Configuration files
│   ├── database/              # Database models and migrations
│   ├── routers/               # API route handlers
│   ├── utils/                 # Utility functions
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Backend container configuration
├── frontend/                  # React frontend application
│   ├── public/               # Static assets
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── config/          # App configuration
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── store/           # State management
│   │   ├── theme/           # Chakra UI theme
│   │   └── test/            # Test utilities
│   ├── package.json         # Node.js dependencies
│   └── Dockerfile          # Frontend container configuration
├── docker-compose.yml        # Multi-container configuration
└── README.md                # Project documentation
```

## Features

### Core Functionality
- **Secret Threshold Bidding**: Artists set hidden minimum prices for their artwork
- **Real-time Bidding**: Live updates using WebSocket connections
- **Instant Sales**: Automatic purchase when bid meets or exceeds secret threshold
- **Multi-user Support**: Separate interfaces for buyers, sellers, and admins

### User Experience
- **Social Authentication**: Login with Google, Facebook, or other providers via Auth0
- **Responsive Design**: Mobile-friendly interface using Chakra UI components
- **File Upload**: Drag-and-drop image upload with validation
- **Payment Processing**: Secure transactions through Stripe integration
- **Bid History**: Track all bids and auction activity

### Technical Features
- **Real-time Communication**: WebSocket connections for live bidding updates
- **Image Processing**: Automatic image optimization and validation
- **Role-based Access**: Different permissions for buyers, sellers, and admins
- **API Documentation**: Auto-generated docs with FastAPI
- **Containerized Deployment**: Docker containers for consistent environments

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework with async support
- **PostgreSQL** - SQL database with advanced features
- **SQLAlchemy** - Python ORM for database operations
- **Socket.IO** - Real-time WebSocket communication for live bidding
- **Auth0** - Social authentication and user management
- **Stripe** - Payment processing (test mode)
- **Aiofiles** - Async file handling for image uploads
- **Pillow** - Image processing and validation

### Frontend
- **React 19** - Component-based UI framework
- **Zustand** - Lightweight state management
- **TanStack Query** - Server state management and caching
- **Chakra UI v3** - Accessible component library
- **Socket.io-client** - WebSocket client for real-time bidding
- **React-dropzone** - File upload component
- **Auth0 React SDK** - Social authentication integration
- **Vite** - Build tool and development server

### DevOps & Deployment
- **Docker** - Containerization
- **GitHub Actions** - CI/CD pipeline for testing and deployment
- **Render** - Free tier cloud hosting platform
- **PostgreSQL** - Managed database hosting

### Testing
- **Pytest** - Backend testing framework
- **Vitest** - Fast frontend testing framework
- **React Testing Library** - Component testing utilities

---

**Note**: This is a DevOps student project developed at DTU (Technical University of Denmark) as part of coursework demonstrating modern software development and deployment practices.
