# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

# Copy prisma schema and generate client
COPY prisma ./prisma
RUN npx prisma generate

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
COPY --from=builder /app/package.json ./
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/prisma ./prisma

EXPOSE 3000

# Create a shell script to run migrations and start the application
COPY <<-"EOF" /docker-entrypoint.sh
#!/bin/sh
set -e

echo "Running Prisma migrations..."
npx prisma migrate deploy || { echo "Prisma migration failed"; exit 1; }

echo "Starting Next.js server..."
node server.js || { echo "Failed to start Next.js server"; exit 1; }
EOF

RUN chmod +x /docker-entrypoint.sh

CMD ["/docker-entrypoint.sh"] 