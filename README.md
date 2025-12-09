# Algoritmo Deferred Acceptance (Gale-Shapley)

Implementação em Python do algoritmo Deferred Acceptance para o Problema Hospital-Residentes.

Trabalho desenvolvido para a disciplina de Teoria dos Grafos - UFAM 2025.

## Sobre

O algoritmo Deferred Acceptance foi proposto por Gale e Shapley (1962) para encontrar matchings estáveis entre dois conjuntos de agentes com preferências. Esta implementação segue a versão many-to-one descrita em Roth e Sotomayor (1990).

## Como executar

```bash
python3 deferred_acceptance.py
```

## Validação contra biblioteca matching (JOSS)

Para validar a implementação contra a biblioteca `matching` de Wilde et al. (2020):

```bash
python3 -m venv venv
source venv/bin/activate
pip install matching
python3 validacao_matching.py
```

## Estrutura

- `Prestador`: classe que representa prestadores/hospitais com capacidade
- `Cliente`: classe que representa clientes/residentes
- `DeferredAcceptance`: implementação do algoritmo
- `exemplo_marketplace()`: exemplo do artigo com eletricistas e clientes
- `experimentos_escala()`: testes de escalabilidade
- `rural_hospitals_demo()`: demonstração do Teorema dos Hospitais Rurais

## Referências

- Gale, D., & Shapley, L. S. (1962). College admissions and the stability of marriage. American Mathematical Monthly, 69(1), 9-15.
- Roth, A. E., & Sotomayor, M. (1990). Two-Sided Matching: A Study in Game-Theoretic Modeling and Analysis. Cambridge University Press.

