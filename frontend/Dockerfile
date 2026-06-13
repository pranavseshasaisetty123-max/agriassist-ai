# Stage 1: Build the React Application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package descriptors and install dependencies
COPY package*.json ./
RUN npm ci

# Copy the rest of the application files
COPY . .

# Set Vite build arguments and environment variables
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Build Vite static bundle
RUN npm run build

# Stage 2: Serve using Nginx
FROM nginx:stable-alpine

# Copy custom Nginx routing configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy build assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
