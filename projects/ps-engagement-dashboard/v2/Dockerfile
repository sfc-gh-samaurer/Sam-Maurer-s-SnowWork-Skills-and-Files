# Pre-built deployment image
# Build output is created locally via `npm run build`, then this Dockerfile
# packages the standalone output with linux-native dependencies.
# This avoids running Next.js SWC compilation under QEMU emulation.

FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV HOSTNAME=0.0.0.0
ENV PORT=8080
ENV NEXT_TELEMETRY_DISABLED=1

# Security: run as non-root
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy pre-built standalone output (from local `npm run build`)
COPY .next/standalone ./
COPY .next/static ./.next/static
COPY public ./public

# Replace darwin-arm64 sharp binaries with linux-musl equivalents
RUN rm -rf node_modules/@img/sharp-darwin-arm64 \
          node_modules/@img/sharp-libvips-darwin-arm64 && \
    npm install --os=linux --cpu=x64 --libc=musl sharp@0.33.5 --no-save 2>/dev/null || true

# Set ownership
RUN chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 8080

CMD ["node", "server.js"]
