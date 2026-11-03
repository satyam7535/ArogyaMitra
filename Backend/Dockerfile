# Stage 1: Dependency resolution and install
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

# Stage 2: Hardened runtime without npm CLI
FROM node:22-alpine

WORKDIR /app

# Eliminate bundled npm CLI and binaries from runtime container to eliminate npm CLI CVEs
RUN rm -rf /usr/local/lib/node_modules/npm /usr/local/bin/npm /usr/local/bin/npx

# Copy production node_modules from builder stage
COPY --from=builder /app/node_modules ./node_modules

# Copy application source
COPY . .
RUN chown -R node:node /app

USER node

EXPOSE 5000

ENV NODE_ENV=production
ENV PORT=5000

CMD ["node", "src/index.js"]
