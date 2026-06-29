# ====================================================================
# RADIX Placements Portal Frontend Dockerfile
# Place in: Final/frontend/Dockerfile
# ====================================================================

FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy codebase and compile Next.js application
COPY . .
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# Expose Next.js server port
EXPOSE 3000

# Start Next.js server
CMD ["npm", "run", "start"]
