# Build stage
FROM node:18-alpine AS builder

# Add build-time dependencies
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Next.js build arg
ARG NEXT_PUBLIC_WS_URL
ENV NEXT_PUBLIC_WS_URL=${NEXT_PUBLIC_WS_URL}

# Cache dependencies layer
COPY package*.json ./
RUN npm ci

# Copy prisma schema and generate client
COPY prisma ./prisma
RUN npx prisma generate

# Copy source with proper .dockerignore
COPY . .
RUN npm run build

# Production stage
FROM node:18-slim AS runner

WORKDIR /app

# Install OpenSSL and other required dependencies
RUN apt-get update -y && \
    apt-get install -y openssl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install prisma as a production dependency for migrations
RUN npm install prisma

COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/prisma ./prisma
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma

EXPOSE 3000

# Create entrypoint script
COPY <<-"EOF" /docker-entrypoint.sh
#!/bin/sh
set -e

echo "Running Prisma migrations..."
npx prisma migrate deploy || { echo "Prisma migration failed"; exit 1; }

echo "Starting Next.js server..."
exec node server.js
EOF

RUN chmod +x /docker-entrypoint.sh

CMD ["/docker-entrypoint.sh"] 