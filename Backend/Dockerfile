FROM node:22-alpine

WORKDIR /app

# Install dependencies with exact lockfile
COPY package*.json ./
RUN npm ci --omit=dev

# Copy source code
COPY . .
RUN chown -R node:node /app

USER node

EXPOSE 5000

ENV NODE_ENV=production
ENV PORT=5000

CMD ["node", "src/index.js"]
