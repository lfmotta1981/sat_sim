# 📡 sat_sim — Simulador minimalista de constelações LEO

`sat_sim` é uma ferramenta em Python para **análise e trade-off de constelações LEO pequenas (≈ 4–20 satélites)**, inspirada em fluxos do ANSYS STK, com foco em:

- clareza física
- extensibilidade
- estudos de arquitetura
- uso via linha de comando (CLI)

O objetivo **não é visualização 3D sofisticada**, e sim **engenharia de sistemas orbitais**.

---

## ✨ Capacidades principais

- Propagação orbital two-body + J2
- Geração de constelações Walker (n planos × sats por plano)
- Cálculo de acesso satélite–solo
- Análise de cobertura temporal
- Métricas:
  - gap máximo sem cobertura
  - revisit time médio
  - cobertura acumulada
- Visualizações 2D:
  - timelines de acesso
  - mapas de cobertura
  - mapas de gap máximo
  - snapshots de constelação

---

## 🗂 Estrutura do projeto

- sat_sim/ → core da biblioteca (física, acesso, cobertura)
- examples/ → scripts executáveis (casos de uso)
- results/ → outputs gerados (CSV, mapas)

O core não depende de CLI.  
Os scripts em examples/ são a interface principal para o usuário.

---

## 🚀 Fluxo recomendado de uso

### 1️⃣ Acesso básico (sanity check)
examples/single_access.py

O que faz:
- Simula acesso de 1 satélite × 1 estação
- Lista passes, duração e gaps

Quando usar:
- Validar a física do modelo
- Entender efeito de altitude, inclinação e elevação mínima

Resultado esperado:
- Lista de passes ao longo do dia
- Durações realistas (ordem de minutos)

---

### 2️⃣ Acesso agregado de constelação
examples/constellation.py

O que faz:
- Simula múltiplos satélites
- Mostra timelines individuais e acesso agregado

Quando usar:
- Visualizar redução de gaps com mais satélites
- Comparar arranjos geométricos de constelação

---

### 3️⃣ Comparação dirigida de arquiteturas
examples/architecture_tradeoff.py

O que faz:
- Compara arquiteturas candidatas
- Calcula gap máximo e revisit médio
- Salva resultados em CSV

Quando usar:
- Quando o total de satélites já é conhecido
- Avaliar como distribuí-los entre planos orbitais

Resultado esperado:
- Tabela-resumo no terminal
- Arquivo architecture_tradeoff.csv

---

### 4️⃣ Exploração automática de arquiteturas (sweep)
examples/architecture_sweep_full.py

O que faz:
- Varre arquiteturas até um número máximo de satélites
- Avalia cobertura global e gap máximo
- Usa uma ROI (ponto) como critério primário
- Gera ranking e CSV

Quando usar:
- Estudos de trade-off
- Descobrir arquiteturas promissoras automaticamente

---

### 5️⃣ Mapas de decisão (7C)
examples/architecture_maps_7c.py

O que faz:
- Gera mapas para arquiteturas selecionadas:
  - cobertura temporal
  - gap máximo
- Destaque visual da ROI
- Saída em PNG

Quando usar:
- Apoio à tomada de decisão
- Comunicação com públicos não técnicos

---

### 6️⃣ Snapshot estrutural da constelação
examples/constellation_snapshot.py

O que faz:
- Mostra posição dos satélites (lat/lon) em um instante
- Inclui mapa-múndi para contexto geográfico

Quando usar:
- Entender a geometria orbital
- Visualização explicativa da constelação

---

## 🛰 Estações terrestres

O projeto utiliza um catálogo simples de estações, com possibilidade de override manual.

Estação default:
- sternula
  - Latitude: 57.02868
  - Longitude: 9.94350

Uso:
- --station svalbard
- --lat 60.0 --lon 15.0

Prioridade de seleção:
1. lat/lon manual
2. estação do catálogo
3. default: sternula

---

## 📍 Região de Interesse (ROI)

Atualmente suportado:
- ponto geográfico

Formato:
- --roi point:lat,lon

A ROI é usada como critério primário de decisão, tipicamente o gap máximo local.

---

## 📊 Interpretação das métricas

- Gap máximo: pior intervalo sem cobertura
- Revisit médio: frequência média de acesso
- Cobertura acumulada: tempo total com visibilidade

Regra prática:
- menor gap → maior robustez
- maior cobertura → maior disponibilidade
- trade-offs são esperados

---

## 🔧 Argumentos de linha de comando (CLI)

### architecture_tradeoff.py

Avalia arquiteturas específicas para uma estação terrestre.

Uso básico:
- python examples/architecture_tradeoff.py

Estação:
- --station <nome>  (sternula, svalbard, kiruna, troll, alaska)
- --lat <graus>
- --lon <graus>

Órbita:
- --altitude <km>       (default: 550)
- --inclination <deg>   (default: 98)
- --min-elev <deg>      (default: 10)

Tempo:
- --duration <h>  (default: 24)
- --dt <s>        (default: 30)

Arquitetura:
- --total-sats <N>  (gera automaticamente arquiteturas com N satélites)

Se total-sats não for fornecido, o script avalia um conjunto default.

---

### architecture_sweep_full.py

Explora automaticamente arquiteturas até um número máximo de satélites, usando ROI como critério primário.

Uso básico:
- python examples/architecture_sweep_full.py

Órbita:
- --altitude <km>     (default: 550)
- --inclination <deg> (default: 98)

Espaço de arquiteturas:
- --n-max <N> (default: 4)

ROI:
- --roi point:lat,lon
- default: point:57.02868,9.94350

---

## Next version:

- Link budget / RF

## Escopo (o que o projeto NÃO faz)

- Atitude
- Manobras
- 3D interativo em tempo real
- Otimização automática avançada

---

## 🧠 Filosofia do projeto

- scripts > GUI
- clareza > performance
- decisões explícitas > automação cega
- extensível, sem inchaço
