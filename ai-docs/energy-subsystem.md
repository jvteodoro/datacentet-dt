# Energy Layers
Source → Routing → Conditioning → Intermediate Storage → Primary Distribution → Secondary Distribution → Final Conversion → Consumption

Excelente — agora você está fazendo **engenharia de sistemas de verdade**.
Vamos **abstrair o subsistema de energia** como uma **cadeia de camadas**, independente de fabricante, tecnologia AC/DC ou topologia específica.

Vou tratar **dois fluxos** em paralelo:

1. **Energia vinda da rede**
2. **Energia vinda da geração local**

E depois **convergimos no uso final pelo servidor**.

---

# Visão geral: cadeia energética abstrata do data center

Pense no subsistema de energia como uma **pipeline em camadas**, cada uma com:

* função física
* função lógica
* pontos de observação/controle

```
[Fonte] → [Acondicionamento] → [Proteção] → [Distribuição]
       → [Conversão final] → [Consumo computacional]
```

Isso vale **tanto para rede quanto para geração**.

---

# 1. Camada 0 – Fontes de energia

### 1.1. Fonte externa (rede elétrica)

**Abstração**

* Fonte síncrona, externa, não controlável
* Variável em qualidade e disponibilidade

**Funções**

* Fornecer potência elétrica
* Definir frequência e referência

**Observável**

* Tensão, frequência
* Qualidade (THD, afundamentos)
* Disponibilidade

**Controlável**

* Quase nada (apenas desconexão)

---

### 1.2. Fonte interna (geração local)

Inclui:

* Geradores (diesel, gás, H₂)
* Renováveis (solar, eólica)
* Armazenamento (baterias, flywheel)

**Abstração**

* Fonte controlável ou semi-controlável

**Observável**

* Potência disponível
* Estado operacional
* Combustível / SoC

**Controlável**

* Start/stop
* Setpoints de potência
* Sincronização

---

# 2. Camada 1 – Interface de entrada e comutação

### Função principal

**Selecionar e isolar fontes**

Inclui:

* ATS (Automatic Transfer Switch)
* Chaves seccionadoras
* Barramentos de entrada

**Abstração**

* Elemento de *roteamento de energia*

**Observável**

* Fonte ativa
* Estados de chaveamento

**Controlável**

* Comutar fonte
* Isolar trechos

⚠️ Camada crítica de segurança.

---

# 3. Camada 2 – Acondicionamento e estabilização

Aqui a energia começa a ser “civilizada”.

Inclui:

* UPS
* Retificadores
* Inversores
* Filtros

**Abstração**

* Transformar energia “bruta” em energia confiável

**Funções**

* Correção de tensão
* Backup instantâneo
* Isolação de falhas
* Conversão AC ↔ DC

**Observável**

* Estado da UPS
* SoC das baterias
* Modo de operação

**Controlável**

* Modo online/eco
* Limites de carga
* Testes automáticos

---

# 4. Camada 3 – Armazenamento intermediário

Pode estar embutida ou separada.

Inclui:

* Bancos de baterias
* Supercapacitores
* Flywheels

**Abstração**

* Buffer energético temporal

**Observável**

* Energia armazenada
* Temperatura
* Saúde

**Controlável**

* Taxa de carga/descarga
* Prioridade de uso

---

# 5. Camada 4 – Distribuição primária

Energia já está “segura”, agora precisa ser **levada**.

Inclui:

* Quadros de média/baixa tensão
* Transformadores
* Barramentos principais

**Abstração**

* Transporte energético confiável

**Observável**

* Corrente por ramo
* Estados de disjuntores

**Controlável**

* Abertura/fechamento
* Seccionamento

---

# 6. Camada 5 – Distribuição secundária (edge de energia)

Mais próxima da TI.

Inclui:

* PDUs
* RPPs
* Busways

**Abstração**

* Alocação energética por zona

**Observável**

* Consumo por rack
* Sobrecargas locais

**Controlável**

* Shed de carga
* Prioridades

---

# 7. Camada 6 – Conversão final (rack / servidor)

Onde energia vira computação.

Inclui:

* Fontes redundantes (PSU)
* Conversão AC → DC (48V, 12V, etc.)
* VRMs

**Abstração**

* Conversão elétrica → energia lógica

**Observável**

* Consumo por servidor
* Eficiência da PSU

**Controlável**

* Liga/desliga
* Power capping

---

# 8. Camada 7 – Consumo computacional

Aqui energia vira:

* Bits
* Cálculo
* Serviços digitais

Inclui:

* CPUs, GPUs, ASICs
* Memória
* Storage
* Network

**Abstração**

* Carga computacional

**Observável**

* Potência por workload
* Performance/Watt

**Controlável**

* DVFS
* Throttling
* Migração de carga

---

# 9. Unificando rede e geração (visão integrada)

```
[ Rede ] ─┐
          ├─→ [ Comutação ] → [ UPS ] → [ Distribuição ] → [ Servidor ]
[ Geração ]┘
```

Energia **não carrega contexto**:

* Quem dá o contexto é o **sistema de controle**.

---

# 10. Camadas lógicas sobrepostas (meta-camadas)

Independem da fonte:

### A. Proteção

* Relés
* Fusíveis
* Intertravamentos

### B. Controle local

* PLC / IoT Controller

### C. Supervisão

* SCADA / EMS / DCIM

### D. Inteligência

* Otimização
* Digital Twin
* Planejamento

---

# 11. O ponto-chave da abstração

> **Cada camada transforma energia e reduz incerteza.**

* Rede: energia incerta
* UPS: energia previsível
* PDU: energia endereçada
* Servidor: energia útil

Essa visão é **muito poderosa** para:

* Arquitetura
* Pesquisa
* DSLs
* Digital Twins
* Discussões de sustentabilidade e resiliência

