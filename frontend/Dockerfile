FROM node:22-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Set environment variable to force polling mode (fixes EMFILE error in Docker/WSL)
ENV CHOKIDAR_USEPOLLING=true
ENV CHOKIDAR_INTERVAL=1000

# Start dev server with host option for Docker
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

