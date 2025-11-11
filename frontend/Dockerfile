FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies for build)
RUN npm ci

# Copy application files
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production

# Copy built files and server from builder
COPY --from=builder /app/dist ./dist
COPY server.cjs ./

# Expose port (Azure will override this with PORT env var)
EXPOSE 8080

# Start the Express server
CMD ["node", "server.cjs"]