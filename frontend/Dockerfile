FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Update Alpine packages and install dependencies
RUN apk update && \
    apk upgrade && \
    rm -rf /var/cache/apk/* && \
    npm ci

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

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Update Alpine packages and install production dependencies
RUN apk update && \
    apk upgrade && \
    rm -rf /var/cache/apk/* && \
    npm ci --only=production

# Copy built files and server from builder
COPY --from=builder /app/dist ./dist
COPY server.cjs ./

# Expose port (Azure will override this with PORT env var)
EXPOSE 8080

# Start the Express server
CMD ["node", "server.cjs"]