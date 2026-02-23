# Copyright (c) 2026 NyxeraLabs
# Author: José María Micoli
# Licensed under BSL 1.1
# Change Date: 2033-02-22 -> Apache-2.0
#
# You may:
# Study
# Modify
# Use for internal security testing
#
# You may NOT:
# Offer as a commercial service
# Sell derived competing products


FROM node:22.11.0-alpine3.20 AS deps
WORKDIR /app
COPY package.json ./
RUN npm install

FROM node:22.11.0-alpine3.20 AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:22.11.0-alpine3.20 AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup -S spectra && adduser -S spectra -G spectra
RUN mkdir -p /var/lib/spectrastrike && chown -R spectra:spectra /var/lib/spectrastrike

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

USER spectra
EXPOSE 3000
CMD ["node", "server.js"]
