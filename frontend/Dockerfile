# ==============================================================================
# Multi-stage production Dockerfile for Next.js frontend
# ==============================================================================

# --- Stage 1: Dependencies ---
FROM node:20-alpine AS deps

WORKDIR /app
COPY package.json package-lock.json* yarn.lock* ./
RUN npm ci --legacy-peer-deps 2>/dev/null || npm install

# --- Stage 2: Builder ---
FROM node:20-alpine AS builder

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
ENV NEXT_PUBLIC_API_URL=http://localhost:8000

RUN npm run build

# --- Stage 3: Production ---
FROM node:20-alpine AS production

# Security: non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["node", "server.js"]
