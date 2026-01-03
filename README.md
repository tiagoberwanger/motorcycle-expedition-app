## Motorcycle Expedition Planning App

Uma API construída com FastAPI para planejamento de rotas de motocicleta a longa distância. O sistema identifica automaticamente pontos de abastecimento baseados na autonomia da moto e alerta sobre "trechos críticos" onde não há postos operacionais disponíveis.

### ✨ Funcionalidades
Roteamento Inteligente: Utiliza a Google Routes API (v2) otimizada para motocicletas (`TWO_WHEELER`).

Busca de Postos por "Distância de asfalto": Integra a nova Google Places API com `routingSummaries` para ignorar postos inacessíveis (ex: outro lado de rios sem ponte ou fronteiras).

Cálculo de Autonomia: Identifica pontos de gatilho para reabastecimento considerando uma margem de segurança.

Linha do Tempo (Timeline): Retorna um cronograma unificado de paradas sugeridas e avisos de perigo.

Link de Navegação: URL pronta para abrir no aplicativo Google Maps com todos os waypoints.

### 🛠️ Tecnologias

FastAPI - Framework de alta performance.

Httpx - Cliente HTTP assíncrono.

Polyline - Manipulação de geometrias do Google Maps.


### 🚀 Como Rodar
1. Configuração do Ambiente
Clone o repositório e instale as dependências:

```Bash
pip install -r requirements.txt
```

2. Criar uma **API KEY** e liberar as seguintes APIs do Google:

- Routes API

- Places API (New)

- Maps Static API

3. Adicionar a variável de ambiente

`GOOGLE_API_KEY = "SUA_CHAVE_AQUI"`

4. Iniciar o Servidor

`uvicorn main:app --reload`

📖 Exemplo de Uso (Payload)

POST /route-plan

```JSON
{
  "origin": "Jaraguá do Sul, SC",
  "destination": "Belo Horizonte, MG",
  "motorcycle": {
    "fuel_autonomy": 350.0,
    "fuel_safety_margin": 50.0
  }
}