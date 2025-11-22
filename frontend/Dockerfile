# Builder stage - build the application
FROM node:20-alpine AS builder

WORKDIR /app

# Update Alpine packages and install dependencies
RUN apk update && \
    apk upgrade && \
    rm -rf /var/cache/apk/*

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application files
COPY . .

# Accept build arguments for environment variables
ARG VITE_API_BASE_URL
ARG VITE_SOCKET_URL
ARG VITE_AUTH0_DOMAIN
ARG VITE_AUTH0_CLIENT_ID
ARG VITE_AUTH0_AUDIENCE
ARG VITE_SENTRY_DSN

# Set environment variables for build
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_SOCKET_URL=$VITE_SOCKET_URL
ENV VITE_AUTH0_DOMAIN=$VITE_AUTH0_DOMAIN
ENV VITE_AUTH0_CLIENT_ID=$VITE_AUTH0_CLIENT_ID
ENV VITE_AUTH0_AUDIENCE=$VITE_AUTH0_AUDIENCE
ENV VITE_SENTRY_DSN=$VITE_SENTRY_DSN

# Build the application
RUN npm run build

# Dependencies stage - install production dependencies
FROM node:20-alpine AS dependencies

WORKDIR /app

# Update Alpine packages
RUN apk update && \
    apk upgrade && \
    rm -rf /var/cache/apk/*

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production

# Production stage - alpine for compatibility
FROM node:20-alpine

WORKDIR /app

# Create non-root user for security (use node user that already exists in alpine)
RUN chown -R node:node /app

# Copy production dependencies from dependencies stage
COPY --from=dependencies /app/node_modules ./node_modules

# Copy built files from builder
COPY --from=builder /app/dist ./dist

# Copy server file
COPY --chown=node:node server.cjs ./

# Switch to non-root user
USER node

# Expose port (Azure will override this with PORT env var)
EXPOSE 8080

# Start the Express server
CMD ["node", "server.cjs"]