# 1. Aşama: Derleme (Build) Aşaması
FROM node:22-alpine AS build

WORKDIR /app

# Monorepo yapısına uygun olarak sadece frontend bağımlılıklarını kopyalıyoruz
COPY apps/frontend/package.json apps/frontend/package-lock.json* ./
RUN npm install

# Tüm frontend kaynak kodunu konteyner içine alıyoruz
COPY apps/frontend/ ./

# Üretim çıktısını (dist klasörünü) oluşturuyoruz
RUN npm run build

# 2. Aşama: Canlı Yayın (Production/Nginx) Aşaması
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Nginx varsayılan olarak 80 portunda çalışır
EXPOSE 80