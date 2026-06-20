# Stage 1: Build static assets
FROM node:20-alpine AS build

WORKDIR /app

# Copy package requirements and install dependencies
COPY package*.json ./
RUN npm ci

# Copy codebase and compile React production bundle
COPY . .
RUN npm run build

# Stage 2: Serve using Nginx
FROM nginx:alpine

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy production assets from Stage 1
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
