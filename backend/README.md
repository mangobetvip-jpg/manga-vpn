# Manga VPN API

## Local setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Preencha `SUPABASE_URL` com a URL do projeto Supabase. Não coloque a chave `service_role`, senha do banco ou segredos no frontend.

Execute:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Endpoints

- `GET /api/health`: saúde da API.
- `GET /api/regions`: regiões cadastradas.
- `GET /api/me`: valida o JWT do Supabase e retorna o ID autenticado.
- `POST /api/wireguard/config`: recebe região, dispositivo, tipo de IP e chave pública WireGuard; ainda responde 503 até conectar servidores e regras de assinatura.
- `POST /api/proxy/session`: permanece desativado.

Envie o access token do Supabase no cabeçalho `Authorization: Bearer <access_token>`.

## Importante

O cliente deve gerar o par de chaves WireGuard localmente e enviar somente a chave pública. A chave privada nunca deve ser enviada à API ou armazenada no Supabase.

A validação JWT usa o endpoint JWKS do Supabase. Se o projeto ainda estiver usando tokens assinados com o segredo legado HS256, migre para chaves assimétricas antes de usar esta validação.

Esta API ainda não fornece túneis VPN: faltam servidores WireGuard, alocação de endereços, persistência de dispositivos, controle de assinatura e automação de provisionamento.
