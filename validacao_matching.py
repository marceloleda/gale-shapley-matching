"""
Validação da implementação contra a biblioteca matching (JOSS)
==============================================================

Conforme descrito na Seção 5.1 do artigo, este script compara os resultados
da implementação própria com a biblioteca matching de Wilde et al. (2020).

Referência:
- Wilde, H., Knight, V., & Gillard, J. (2020). Matching: A python library
  for solving matching games. Journal of Open Source Software, 5(48), 2169.
"""

from matching.games import HospitalResident
from deferred_acceptance import (
    Prestador, Cliente, DeferredAcceptance
)


def validar_cenario(nome, prestadores_config, clientes_config):
    """
    Valida um cenário comparando implementação própria vs biblioteca matching.
    """
    print(f"\n{'='*60}")
    print(f"CENÁRIO: {nome}")
    print('='*60)

    # === IMPLEMENTAÇÃO PRÓPRIA ===
    prestadores = [
        Prestador(id=p['id'], nome=p['nome'], capacidade=p['capacidade'],
                  preferencias=p['preferencias'])
        for p in prestadores_config
    ]
    clientes = [
        Cliente(id=c['id'], nome=c['nome'], preferencias=c['preferencias'])
        for c in clientes_config
    ]

    algoritmo = DeferredAcceptance(prestadores, clientes)
    resultado = algoritmo.executar(verbose=False)

    # === BIBLIOTECA MATCHING ===
    # Formato: {residente: [lista de hospitais preferidos]}
    resident_prefs = {
        c['id']: c['preferencias'] for c in clientes_config
    }

    # Formato: {hospital: [lista de residentes preferidos]}
    hospital_prefs = {
        p['id']: p['preferencias'] for p in prestadores_config
    }

    # Capacidades
    capacities = {
        p['id']: p['capacidade'] for p in prestadores_config
    }

    # Cria e resolve o jogo
    game = HospitalResident.create_from_dictionaries(
        resident_prefs, hospital_prefs, capacities
    )
    matching_lib = game.solve()

    # === COMPARAÇÃO ===
    print("\nResultado - Implementação própria:")
    for p_id, clientes_ids in sorted(resultado.matching.items()):
        print(f"  {p_id}: {sorted(clientes_ids)}")

    print("\nResultado - Biblioteca matching (JOSS):")
    for hospital, residents in sorted(matching_lib.items(), key=lambda x: str(x[0])):
        residents_ids = sorted([r.name for r in residents])
        print(f"  {hospital.name}: {residents_ids}")

    # Verifica se são idênticos
    identico = True
    for hospital, residents in matching_lib.items():
        lib_residents = set(r.name for r in residents)
        proprio_residents = set(resultado.matching.get(hospital.name, []))
        if lib_residents != proprio_residents:
            identico = False
            break

    print(f"\n{'✓ IDÊNTICO' if identico else '✗ DIFERENTE'}")
    return identico


def main():
    print("="*60)
    print("VALIDAÇÃO: Implementação vs Biblioteca matching (JOSS)")
    print("="*60)
    print("\nConforme Seção 5.1 do artigo, comparando resultados com a")
    print("biblioteca matching de Wilde et al. (2020).")

    resultados = []

    # CENÁRIO 1: Marketplace (exemplo do artigo)
    prestadores_marketplace = [
        {'id': 'E1', 'nome': 'Eletricista Premium', 'capacidade': 2,
         'preferencias': ['C2', 'C1', 'C3', 'C4', 'C5']},
        {'id': 'E2', 'nome': 'Eletricista Padrão', 'capacidade': 2,
         'preferencias': ['C3', 'C5', 'C1', 'C4', 'C2']},
        {'id': 'E3', 'nome': 'Eletricista Econômico', 'capacidade': 1,
         'preferencias': ['C1', 'C2', 'C5', 'C3', 'C4']},
    ]
    clientes_marketplace = [
        {'id': 'C1', 'nome': 'Cliente 1', 'preferencias': ['E1', 'E2', 'E3']},
        {'id': 'C2', 'nome': 'Cliente 2', 'preferencias': ['E1', 'E3', 'E2']},
        {'id': 'C3', 'nome': 'Cliente 3', 'preferencias': ['E2', 'E1', 'E3']},
        {'id': 'C4', 'nome': 'Cliente 4', 'preferencias': ['E1', 'E2', 'E3']},
        {'id': 'C5', 'nome': 'Cliente 5', 'preferencias': ['E2', 'E3', 'E1']},
    ]
    resultados.append(('Marketplace (artigo)',
                       validar_cenario('Marketplace (artigo)',
                                      prestadores_marketplace,
                                      clientes_marketplace)))

    # CENÁRIO 2: Tipo NRMP (8 residentes, 3 hospitais)
    prestadores_nrmp = [
        {'id': 'H1', 'nome': 'Hospital 1', 'capacidade': 3,
         'preferencias': ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8']},
        {'id': 'H2', 'nome': 'Hospital 2', 'capacidade': 3,
         'preferencias': ['R2', 'R1', 'R4', 'R3', 'R6', 'R5', 'R8', 'R7']},
        {'id': 'H3', 'nome': 'Hospital 3', 'capacidade': 2,
         'preferencias': ['R3', 'R4', 'R1', 'R2', 'R7', 'R8', 'R5', 'R6']},
    ]
    clientes_nrmp = [
        {'id': 'R1', 'nome': 'Residente 1', 'preferencias': ['H1', 'H2', 'H3']},
        {'id': 'R2', 'nome': 'Residente 2', 'preferencias': ['H1', 'H2', 'H3']},
        {'id': 'R3', 'nome': 'Residente 3', 'preferencias': ['H2', 'H1', 'H3']},
        {'id': 'R4', 'nome': 'Residente 4', 'preferencias': ['H2', 'H3', 'H1']},
        {'id': 'R5', 'nome': 'Residente 5', 'preferencias': ['H1', 'H2', 'H3']},
        {'id': 'R6', 'nome': 'Residente 6', 'preferencias': ['H1', 'H2', 'H3']},
        {'id': 'R7', 'nome': 'Residente 7', 'preferencias': ['H3', 'H2', 'H1']},
        {'id': 'R8', 'nome': 'Residente 8', 'preferencias': ['H3', 'H1', 'H2']},
    ]
    resultados.append(('Tipo NRMP',
                       validar_cenario('Tipo NRMP',
                                      prestadores_nrmp,
                                      clientes_nrmp)))

    # CENÁRIO 3: Hospitais Rurais (3 residentes, 3 hospitais)
    prestadores_rural = [
        {'id': 'P1', 'nome': 'Premium', 'capacidade': 2,
         'preferencias': ['C1', 'C2', 'C3']},
        {'id': 'P2', 'nome': 'Padrão', 'capacidade': 1,
         'preferencias': ['C1', 'C2', 'C3']},
        {'id': 'P3', 'nome': 'Rural', 'capacidade': 1,
         'preferencias': ['C1', 'C2', 'C3']},
    ]
    clientes_rural = [
        {'id': 'C1', 'nome': 'Cliente 1', 'preferencias': ['P1', 'P2', 'P3']},
        {'id': 'C2', 'nome': 'Cliente 2', 'preferencias': ['P1', 'P2', 'P3']},
        {'id': 'C3', 'nome': 'Cliente 3', 'preferencias': ['P1', 'P2', 'P3']},
    ]
    resultados.append(('Hospitais Rurais',
                       validar_cenario('Hospitais Rurais',
                                      prestadores_rural,
                                      clientes_rural)))

    # RESUMO FINAL
    print("\n" + "="*60)
    print("RESUMO DA VALIDAÇÃO")
    print("="*60)
    print("\nConforme Tabela 1 do artigo:")
    print("-"*40)
    print(f"{'Cenário':<25} {'Resultado':<15}")
    print("-"*40)
    for nome, ok in resultados:
        status = "Idêntico" if ok else "Diferente"
        print(f"{nome:<25} {status:<15}")
    print("-"*40)

    todos_ok = all(r[1] for r in resultados)
    if todos_ok:
        print("\n✓ VALIDAÇÃO COMPLETA: Todos os cenários produziram")
        print("  resultados idênticos à biblioteca matching (JOSS).")
    else:
        print("\n✗ FALHA: Alguns cenários divergiram.")

    return todos_ok


if __name__ == "__main__":
    main()
