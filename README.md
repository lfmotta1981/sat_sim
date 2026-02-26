# 📡 sat_sim — Minimal LEO Constellation & VDES RF Simulator

`sat_sim` é uma ferramenta em Python para **análise de constelações LEO pequenas (≈ 1–20 satélites)** com foco em:

- mecânica orbital clara e auditável  
- análise de acesso geométrico  
- link budget VDE-SAT  
- trade-off arquitetural orientado a requisitos  
- execução via linha de comando (CLI)  

O objetivo não é visualização 3D sofisticada.  
O objetivo é **engenharia de sistemas orbitais e RF de forma minimalista, reproduzível e controlável**.

---

# ✨ Capacidades Principais

## 🛰 Mecânica Orbital

- Propagação two-body
- Perturbação J2
- Elementos orbitais clássicos (COE)
- Geração de constelações Walker (n planos × sats por plano)

---

## 📡 Acesso Geométrico

- Visibilidade satélite–estação
- Elevação mínima configurável
- Cálculo de:
  - número de passes
  - duração de passes
  - gap máximo
  - revisit time médio
- Timeline de acesso agregado

---

## 📶 RF — VDE-SAT Uplink

- Link budget simplificado VDE-SAT
- Critério baseado em fechamento de link (SNR mínimo)
- Substituição do critério puramente geométrico por critério RF real
- Métricas locais:
  - disponibilidade percentual
  - gap máximo RF
  - revisit RF

---

## 📊 Trade-off Arquitetural

- Sweep automático de arquiteturas
- Filtro por requisitos:
  - `--max-gap`
  - `--min-availability`
- Ranking por gap
- Export CSV com header técnico (metadados da simulação)

---

# 🗂 Estrutura do Projeto

```
sat_sim/
│
├── constants.py
├── time.py
├── ground/
├── orbits/
├── frames/
├── access/
│   └── vdes_access.py
├── rf/
│   └── vdes/
│
examples/
│   ├── single_access.py
│   ├── single_access_vdes.py
│   ├── local_availability_vdes.py
│   ├── architecture_tradeoff.py
│   ├── architecture_sweep_full.py
│   └── architecture_sweep_local_rf.py
│
results/
```

O diretório `results/` é criado automaticamente para armazenar CSVs.

---

# 🚀 Fluxo Recomendado de Uso

---

## 1️⃣ Validação Orbital Básica

### `single_access.py`

Simula:
- 1 satélite
- 1 estação
- acesso puramente geométrico

Uso:

```bash
python examples/single_access.py
```

---

## 2️⃣ Validação RF VDE-SAT

### `single_access_vdes.py`

Substitui visibilidade geométrica por fechamento RF.

Uso:

```bash
python examples/single_access_vdes.py
```

Resultado:
- número de instantes com uplink fechado
- duração total
- primeiro acesso

---

## 3️⃣ Disponibilidade RF Local

### `local_availability_vdes.py`

Calcula:
- disponibilidade percentual
- gap máximo
- revisit médio

Exemplo:

```bash
python examples/local_availability_vdes.py \
    --lat 57.02868 \
    --lon 9.94350 \
    --n-planes 2 \
    --sats-per-plane 2
```

---

## 4️⃣ Trade-off Direto de Arquiteturas

### `architecture_tradeoff.py`

Compara arquiteturas específicas para uma estação.

Parâmetros principais:

- `--lat`, `--lon`
- `--altitude`
- `--inclination`
- `--duration`
- `--dt`

Uso:

```bash
python examples/architecture_tradeoff.py \
    --lat 57.0 \
    --lon 10.0
```

---

## 5️⃣ Sweep Global (Geométrico)

### `architecture_sweep_full.py`

Varre arquiteturas até `N_max` satélites.

Critério primário:
- gap máximo em ROI

Uso:

```bash
python examples/architecture_sweep_full.py --n-max 8
```

---

## 6️⃣ Sweep Local RF (VDES)

### `architecture_sweep_local_rf.py`

Motor principal de decisão RF.

Calcula, para cada arquitetura:

- disponibilidade (%)
- gap máximo (min)

Permite requisitos automáticos:

- `--max-gap`
- `--min-availability`

---

### Exemplos

### Ranking completo

```bash
python examples/architecture_sweep_local_rf.py --n-max 12
```

---

### Requisito de gap

```bash
python examples/architecture_sweep_local_rf.py \
    --n-max 12 \
    --max-gap 45
```

---

### Requisito combinado

```bash
python examples/architecture_sweep_local_rf.py \
    --n-max 12 \
    --max-gap 45 \
    --min-availability 40
```

---

# 📄 CSV Export

O sweep gera automaticamente:

```
results/architecture_sweep_local_rf.csv
```

Se houver filtro por requisitos:

```
results/architecture_sweep_local_rf_filtered.csv
```

---

## Header Técnico

Cada CSV contém metadados completos:

```
# Local RF Architecture Sweep
# Latitude [deg]: 57.02868
# Longitude [deg]: 9.94350
# Altitude [km]: 550.0
# Inclination [deg]: 98.0
# Duration [h]: 24.0
# Time step [s]: 30.0
# N_max: 12
# Max gap requirement [min]: 45
# Min availability requirement [%]: 40
#
n_planes,sats_per_plane,total_sats,availability_percent,worst_gap_min
...
```

Isso garante:

- reprodutibilidade
- auditabilidade
- rastreabilidade de resultados

---

# 🛰 Estação Default

Estação padrão:

```
Latitude: 57.02868
Longitude: 9.94350
Nome informal: sternula
```

Pode ser sobrescrita via:

```
--lat
--lon
```

---

# ⚙️ Parâmetros Orbitais

Parâmetros configuráveis via CLI:

| Argumento | Descrição | Default |
|-----------|-----------|---------|
| `--altitude` | Altitude orbital [km] | 550 |
| `--inclination` | Inclinação [deg] | 98 |
| `--duration` | Duração da simulação [h] | 24 |
| `--dt` | Passo temporal [s] | 30 |
| `--n-max` | Máximo total de satélites | 8 |

---

# 📡 Modelo RF Atual

O link budget VDE-SAT considera:

- frequência VHF satélite
- perda de espaço livre
- ganho de antena
- requisito mínimo de SNR
- fechamento de link booleano

O modelo é simplificado mas estruturado para futura expansão por LinkID.

---

# 🧠 Filosofia do Projeto

`sat_sim` segue princípios:

- simplicidade estrutural
- separação clara entre orbital e RF
- CLI como interface primária
- resultados determinísticos
- foco em engenharia, não visualização

---

# 📌 Roadmap Natural

Possíveis evoluções futuras:

- modelagem por LinkID VDE-SAT
- grid RF coverage
- Pareto frontier multi-objetivo
- sweep de altitude e inclinação
- paralelização
- timestamp e git hash automático nos CSVs

---

# 📦 Versionamento

- `v0.1` — núcleo orbital
- `v0.2` — engine RF + sweep orientado a requisitos

---

# 🏁 Conclusão

`sat_sim` já é capaz de:

- dimensionar constelações LEO pequenas
- avaliar disponibilidade VDE-SAT local
- comparar arquiteturas sob requisitos reais
- exportar resultados auditáveis

É um **mission analysis engine minimalista com camada RF integrada**.

---

```
