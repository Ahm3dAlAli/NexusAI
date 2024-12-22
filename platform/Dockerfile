# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Next.js build arg
ARG NEXT_PUBLIC_WS_URL
ENV NEXT_PUBLIC_WS_URL=${NEXT_PUBLIC_WS_URL}

COPY package*.json ./
RUN npm install

# Copy prisma schema and generate client
COPY prisma ./prisma
RUN npx prisma generate

COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

WORKDIR /app

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
npx prisma migrate deploy
exec node server.js
EOF

RUN chmod +x /docker-entrypoint.sh

CMD ["/docker-entrypoint.sh"] 