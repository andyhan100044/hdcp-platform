FROM node:18-alpine

WORKDIR /opt/app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy Strapi application
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S strapi -u 1001

# Build Strapi admin
RUN npm run build

# Change ownership
RUN chown -R strapi:nodejs /opt/app
USER strapi

# Expose port
EXPOSE 1337

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:1337/_health || exit 1

# Start Strapi
CMD ["npm", "run", "develop"]
