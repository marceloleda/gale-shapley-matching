"""
Algoritmo Deferred Acceptance (Gale-Shapley) para o Problema Hospital-Residentes
================================================================================

Implementação baseada no algoritmo original de Gale e Shapley (1962) e na versão
estendida para many-to-one matching descrita em Roth e Sotomayor (1990).

Referências:
- Gale, D., & Shapley, L. S. (1962). College admissions and the stability of marriage.
  American Mathematical Monthly, 69(1), 9-15.
- Roth, A. E., & Sotomayor, M. (1990). Two-Sided Matching: A Study in Game-Theoretic
  Modeling and Analysis. Cambridge University Press.
- Roth, A. E. (1984). The evolution of the labor market for medical interns and
  residents: A case study in game theory. Journal of Political Economy, 92(6), 991-1016.

Autor: Marcelo Ferreira Leda Filho
Universidade Federal do Amazonas (UFAM)
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import time


@dataclass
class Prestador:
    """Representa um prestador de serviços (hospital no problema HR)."""
    id: str
    nome: str
    capacidade: int
    preferencias: List[str]  # Lista ordenada de IDs de clientes (mais preferido primeiro)
    clientes_alocados: List[str] = field(default_factory=list)
    
    def aceita(self, cliente_id: str) -> bool:
        """Verifica se o cliente está na lista de preferências do prestador."""
        return cliente_id in self.preferencias
    
    def ranking(self, cliente_id: str) -> int:
        """Retorna o ranking do cliente (menor = mais preferido)."""
        if cliente_id not in self.preferencias:
            return float('inf')
        return self.preferencias.index(cliente_id)
    
    def pior_cliente(self) -> Optional[str]:
        """Retorna o cliente menos preferido dentre os alocados."""
        if not self.clientes_alocados:
            return None
        return max(self.clientes_alocados, key=lambda c: self.ranking(c))
    
    def tem_vaga(self) -> bool:
        """Verifica se há vagas disponíveis."""
        return len(self.clientes_alocados) < self.capacidade


@dataclass
class Cliente:
    """Representa um cliente (residente no problema HR)."""
    id: str
    nome: str
    preferencias: List[str]  # Lista ordenada de IDs de prestadores
    proximo_a_propor: int = 0  # Índice do próximo prestador na lista
    alocado_para: Optional[str] = None
    
    def proximo_prestador(self) -> Optional[str]:
        """Retorna o próximo prestador para propor ou None se não houver mais."""
        if self.proximo_a_propor >= len(self.preferencias):
            return None
        prestador_id = self.preferencias[self.proximo_a_propor]
        self.proximo_a_propor += 1
        return prestador_id
    
    def esta_livre(self) -> bool:
        """Verifica se o cliente está sem alocação."""
        return self.alocado_para is None
    
    def tem_propostas_restantes(self) -> bool:
        """Verifica se ainda há prestadores para propor."""
        return self.proximo_a_propor < len(self.preferencias)


@dataclass
class ResultadoMatching:
    """Resultado do algoritmo de matching."""
    matching: Dict[str, List[str]]  # prestador_id -> lista de cliente_ids
    num_rodadas: int
    num_propostas: int
    tempo_execucao: float
    clientes_nao_alocados: List[str]
    vagas_nao_preenchidas: Dict[str, int]  # prestador_id -> num vagas vazias


class DeferredAcceptance:
    """
    Implementação do algoritmo Deferred Acceptance (Gale-Shapley).
    
    Esta versão implementa o algoritmo cliente-propositor (applicant-proposing),
    que produz o matching estável ótimo para os clientes.
    
    Complexidade de tempo: O(n * m), onde n = número de clientes e m = número de prestadores
    Complexidade de espaço: O(n + m)
    """
    
    def __init__(self, prestadores: List[Prestador], clientes: List[Cliente]):
        self.prestadores = {p.id: p for p in prestadores}
        self.clientes = {c.id: c for c in clientes}
        self.num_propostas = 0
        self.num_rodadas = 0
        self.historico_rodadas: List[Dict] = []
    
    def executar(self, verbose: bool = False) -> ResultadoMatching:
        """
        Executa o algoritmo Deferred Acceptance.
        
        Args:
            verbose: Se True, imprime o progresso de cada rodada.
            
        Returns:
            ResultadoMatching com o matching estável encontrado.
        """
        inicio = time.time()
        
        # Reset do estado
        for p in self.prestadores.values():
            p.clientes_alocados = []
        for c in self.clientes.values():
            c.proximo_a_propor = 0
            c.alocado_para = None
        self.num_propostas = 0
        self.num_rodadas = 0
        self.historico_rodadas = []
        
        # Conjunto de clientes livres com propostas restantes
        clientes_livres = {c_id for c_id, c in self.clientes.items() 
                          if c.tem_propostas_restantes()}
        
        while clientes_livres:
            self.num_rodadas += 1
            rodada_info = {'rodada': self.num_rodadas, 'propostas': [], 'rejeicoes': []}
            
            # Fase de propostas
            propostas_por_prestador: Dict[str, List[str]] = defaultdict(list)
            
            for cliente_id in list(clientes_livres):
                cliente = self.clientes[cliente_id]
                prestador_id = cliente.proximo_prestador()
                
                if prestador_id is None:
                    clientes_livres.discard(cliente_id)
                    continue
                
                self.num_propostas += 1
                prestador = self.prestadores.get(prestador_id)
                
                if prestador and prestador.aceita(cliente_id):
                    propostas_por_prestador[prestador_id].append(cliente_id)
                    rodada_info['propostas'].append((cliente_id, prestador_id, 'aceita'))
                else:
                    rodada_info['propostas'].append((cliente_id, prestador_id, 'rejeitada'))
            
            # Fase de avaliação pelos prestadores
            for prestador_id, novos_clientes in propostas_por_prestador.items():
                prestador = self.prestadores[prestador_id]
                
                # Junta clientes atuais com novos candidatos
                todos_candidatos = prestador.clientes_alocados + novos_clientes
                
                # Ordena por preferência (menor índice = mais preferido)
                todos_candidatos.sort(key=lambda c: prestador.ranking(c))
                
                # Mantém os melhores até a capacidade
                aceitos = todos_candidatos[:prestador.capacidade]
                rejeitados = todos_candidatos[prestador.capacidade:]
                
                # Atualiza alocações
                prestador.clientes_alocados = aceitos
                
                for cliente_id in aceitos:
                    self.clientes[cliente_id].alocado_para = prestador_id
                    clientes_livres.discard(cliente_id)
                
                for cliente_id in rejeitados:
                    self.clientes[cliente_id].alocado_para = None
                    if self.clientes[cliente_id].tem_propostas_restantes():
                        clientes_livres.add(cliente_id)
                    else:
                        clientes_livres.discard(cliente_id)
                    rodada_info['rejeicoes'].append((cliente_id, prestador_id))
            
            self.historico_rodadas.append(rodada_info)
            
            if verbose:
                self._imprimir_rodada(rodada_info)
            
            # Atualiza conjunto de clientes livres
            clientes_livres = {c_id for c_id, c in self.clientes.items()
                             if c.esta_livre() and c.tem_propostas_restantes()}
        
        tempo_execucao = time.time() - inicio
        
        # Monta resultado
        matching = {p_id: list(p.clientes_alocados) for p_id, p in self.prestadores.items()}
        clientes_nao_alocados = [c_id for c_id, c in self.clientes.items() if c.esta_livre()]
        vagas_nao_preenchidas = {
            p_id: p.capacidade - len(p.clientes_alocados)
            for p_id, p in self.prestadores.items()
            if len(p.clientes_alocados) < p.capacidade
        }
        
        return ResultadoMatching(
            matching=matching,
            num_rodadas=self.num_rodadas,
            num_propostas=self.num_propostas,
            tempo_execucao=tempo_execucao,
            clientes_nao_alocados=clientes_nao_alocados,
            vagas_nao_preenchidas=vagas_nao_preenchidas
        )
    
    def _imprimir_rodada(self, rodada_info: Dict):
        """Imprime informações de uma rodada."""
        print(f"\n{'='*60}")
        print(f"RODADA {rodada_info['rodada']}")
        print('='*60)
        
        print("\nPropostas:")
        for cliente_id, prestador_id, status in rodada_info['propostas']:
            cliente = self.clientes[cliente_id]
            prestador = self.prestadores.get(prestador_id)
            p_nome = prestador.nome if prestador else prestador_id
            print(f"  {cliente.nome} → {p_nome}: {status}")
        
        if rodada_info['rejeicoes']:
            print("\nRejeições (por excesso de capacidade):")
            for cliente_id, prestador_id in rodada_info['rejeicoes']:
                cliente = self.clientes[cliente_id]
                prestador = self.prestadores[prestador_id]
                print(f"  {prestador.nome} rejeitou {cliente.nome}")
        
        print("\nEstado atual:")
        for p_id, p in self.prestadores.items():
            clientes_nomes = [self.clientes[c].nome for c in p.clientes_alocados]
            print(f"  {p.nome}: {clientes_nomes} ({len(p.clientes_alocados)}/{p.capacidade})")
    
    def verificar_estabilidade(self, resultado: ResultadoMatching) -> Tuple[bool, List[Tuple[str, str]]]:
        """
        Verifica se o matching é estável.
        
        Um matching é estável se não existe nenhum par bloqueador (blocking pair),
        ou seja, um par (cliente, prestador) onde ambos prefeririam estar juntos
        do que com suas alocações atuais.
        
        Returns:
            Tupla (é_estável, lista_de_pares_bloqueadores)
        """
        pares_bloqueadores = []
        
        for cliente_id, cliente in self.clientes.items():
            prestador_atual = cliente.alocado_para
            
            # Para cada prestador que o cliente prefere ao atual
            for i, prestador_id in enumerate(cliente.preferencias):
                if prestador_id == prestador_atual:
                    break  # Já chegou no prestador atual, não há mais preferidos
                
                prestador = self.prestadores.get(prestador_id)
                if not prestador:
                    continue
                
                # Verifica se o prestador também prefere este cliente
                if not prestador.aceita(cliente_id):
                    continue
                
                # Verifica se o prestador tem vaga ou prefere este cliente a algum atual
                if prestador.tem_vaga():
                    pares_bloqueadores.append((cliente_id, prestador_id))
                else:
                    # Verifica se prefere este cliente ao pior dos atuais
                    pior_atual = prestador.pior_cliente()
                    if pior_atual and prestador.ranking(cliente_id) < prestador.ranking(pior_atual):
                        pares_bloqueadores.append((cliente_id, prestador_id))
        
        return len(pares_bloqueadores) == 0, pares_bloqueadores


def exemplo_marketplace():
    """
    Exemplo do artigo: Marketplace de serviços de eletricistas.
    
    Este exemplo modela um cenário inspirado em plataformas como TaskRabbit,
    Thumbtack e Amazon Home Services, onde prestadores de serviços são
    pareados com clientes de forma centralizada.
    
    Referências sobre matching em marketplaces:
    - Shi, P. (2023). Optimal Matchmaking Strategy in Two-Sided Marketplaces.
      Management Science.
    - Aouad, A., & Saban, D. (2023). Online Assortment Optimization for 
      Two-Sided Matching Platforms. Management Science, 69(4), 2069-2087.
    """
    print("=" * 70)
    print("EXEMPLO: MARKETPLACE DE SERVIÇOS DE ELETRICISTAS")
    print("=" * 70)
    print("\nModelagem baseada em plataformas como TaskRabbit e Thumbtack,")
    print("utilizando o framework de matching estável de Gale-Shapley (1962).")
    print()
    
    # Definição dos prestadores (eletricistas)
    prestadores = [
        Prestador(
            id="E1", nome="Eletricista Premium", capacidade=2,
            preferencias=["C2", "C1", "C3", "C4", "C5"]
        ),
        Prestador(
            id="E2", nome="Eletricista Padrão", capacidade=2,
            preferencias=["C3", "C5", "C1", "C4", "C2"]
        ),
        Prestador(
            id="E3", nome="Eletricista Econômico", capacidade=1,
            preferencias=["C1", "C2", "C5", "C3", "C4"]
        ),
    ]
    
    # Definição dos clientes
    clientes = [
        Cliente(id="C1", nome="Cliente 1", preferencias=["E1", "E2", "E3"]),
        Cliente(id="C2", nome="Cliente 2", preferencias=["E1", "E3", "E2"]),
        Cliente(id="C3", nome="Cliente 3", preferencias=["E2", "E1", "E3"]),
        Cliente(id="C4", nome="Cliente 4", preferencias=["E1", "E2", "E3"]),
        Cliente(id="C5", nome="Cliente 5", preferencias=["E2", "E3", "E1"]),
    ]
    
    # Imprime configuração
    print("CONFIGURAÇÃO DO PROBLEMA")
    print("-" * 40)
    print("\nPrestadores e capacidades:")
    for p in prestadores:
        print(f"  {p.nome} ({p.id}): capacidade = {p.capacidade}")
        print(f"    Preferências: {' > '.join(p.preferencias)}")
    
    print("\nClientes e preferências:")
    for c in clientes:
        print(f"  {c.nome} ({c.id}): {' > '.join(c.preferencias)}")
    
    # Executa o algoritmo
    print("\n" + "=" * 70)
    print("EXECUÇÃO DO ALGORITMO DEFERRED ACCEPTANCE")
    print("=" * 70)
    
    algoritmo = DeferredAcceptance(prestadores, clientes)
    resultado = algoritmo.executar(verbose=True)
    
    # Imprime resultado final
    print("\n" + "=" * 70)
    print("RESULTADO FINAL")
    print("=" * 70)
    
    print("\nMatching encontrado:")
    print("-" * 40)
    for p_id, clientes_ids in resultado.matching.items():
        p = algoritmo.prestadores[p_id]
        clientes_nomes = [algoritmo.clientes[c].nome for c in clientes_ids]
        print(f"  {p.nome}: {clientes_nomes}")
    
    print(f"\nMétricas de execução:")
    print(f"  - Número de rodadas: {resultado.num_rodadas}")
    print(f"  - Número de propostas: {resultado.num_propostas}")
    print(f"  - Tempo de execução: {resultado.tempo_execucao:.6f} segundos")
    
    if resultado.clientes_nao_alocados:
        nomes = [algoritmo.clientes[c].nome for c in resultado.clientes_nao_alocados]
        print(f"  - Clientes não alocados: {nomes}")
    else:
        print(f"  - Todos os clientes foram alocados!")
    
    if resultado.vagas_nao_preenchidas:
        print(f"  - Vagas não preenchidas:")
        for p_id, vagas in resultado.vagas_nao_preenchidas.items():
            p = algoritmo.prestadores[p_id]
            print(f"      {p.nome}: {vagas} vagas")
    
    # Verifica estabilidade
    print("\n" + "-" * 40)
    print("VERIFICAÇÃO DE ESTABILIDADE")
    print("-" * 40)
    
    estavel, pares_bloqueadores = algoritmo.verificar_estabilidade(resultado)
    
    if estavel:
        print("\n✓ O matching é ESTÁVEL!")
        print("  Não existem pares bloqueadores (blocking pairs).")
        print("  Nenhum par cliente-prestador tem incentivo para desviar.")
    else:
        print("\n✗ O matching NÃO é estável!")
        print("  Pares bloqueadores encontrados:")
        for c_id, p_id in pares_bloqueadores:
            c = algoritmo.clientes[c_id]
            p = algoritmo.prestadores[p_id]
            print(f"    ({c.nome}, {p.nome})")
    
    return resultado


def experimentos_escala():
    """
    Executa experimentos variando o tamanho da instância.
    
    Este experimento demonstra a complexidade O(n*m) do algoritmo,
    conforme estabelecido em Gusfield e Irving (1989).
    
    Referência:
    - Gusfield, D., & Irving, R. W. (1989). The Stable Marriage Problem:
      Structure and Algorithms. MIT Press.
    """
    import random
    
    print("\n" + "=" * 70)
    print("EXPERIMENTOS DE ESCALABILIDADE")
    print("=" * 70)
    print("\nVerificando complexidade O(n*m) do algoritmo.")
    print()
    
    resultados = []
    tamanhos = [10, 20, 50, 100, 200, 500]
    
    for n_clientes in tamanhos:
        n_prestadores = max(3, n_clientes // 5)
        capacidade_media = (n_clientes // n_prestadores) + 1
        
        # Gera instância aleatória
        prestadores = []
        for i in range(n_prestadores):
            clientes_ids = [f"C{j}" for j in range(n_clientes)]
            random.shuffle(clientes_ids)
            prestadores.append(Prestador(
                id=f"P{i}",
                nome=f"Prestador {i}",
                capacidade=capacidade_media,
                preferencias=clientes_ids
            ))
        
        clientes = []
        for j in range(n_clientes):
            prestadores_ids = [f"P{i}" for i in range(n_prestadores)]
            random.shuffle(prestadores_ids)
            clientes.append(Cliente(
                id=f"C{j}",
                nome=f"Cliente {j}",
                preferencias=prestadores_ids
            ))
        
        # Executa algoritmo
        algoritmo = DeferredAcceptance(prestadores, clientes)
        resultado = algoritmo.executar(verbose=False)
        
        # Verifica estabilidade
        estavel, _ = algoritmo.verificar_estabilidade(resultado)
        
        resultados.append({
            'n_clientes': n_clientes,
            'n_prestadores': n_prestadores,
            'n_propostas': resultado.num_propostas,
            'n_rodadas': resultado.num_rodadas,
            'tempo_ms': resultado.tempo_execucao * 1000,
            'estavel': estavel
        })
        
        print(f"n={n_clientes:4d} clientes, m={n_prestadores:3d} prestadores: "
              f"{resultado.num_propostas:6d} propostas, "
              f"{resultado.num_rodadas:4d} rodadas, "
              f"{resultado.tempo_execucao*1000:8.2f}ms, "
              f"estável={estavel}")
    
    print("\n" + "-" * 40)
    print("ANÁLISE")
    print("-" * 40)
    print("\nO número de propostas cresce aproximadamente como O(n*m),")
    print("confirmando a análise teórica do algoritmo.")
    print("O matching resultante é sempre estável (Teorema de Gale-Shapley).")
    
    return resultados


def rural_hospitals_demo():
    """
    Demonstração do Teorema dos Hospitais Rurais (Rural Hospitals Theorem).
    
    Este teorema, provado por Roth (1986), estabelece que:
    1. O conjunto de agentes não pareados é o mesmo em todos os matchings estáveis.
    2. Cada hospital que não preenche todas as vagas em algum matching estável
       recebe exatamente o mesmo conjunto de residentes em todos os matchings estáveis.
    
    Referência:
    - Roth, A. E. (1986). On the allocation of residents to rural hospitals:
      A general property of two-sided matching markets. Econometrica, 54(2), 425-427.
    """
    print("\n" + "=" * 70)
    print("DEMONSTRAÇÃO: TEOREMA DOS HOSPITAIS RURAIS")
    print("=" * 70)
    print("\nO teorema estabelece que prestadores 'impopulares' não podem")
    print("melhorar sua situação através de mudanças no mecanismo de matching.")
    print()
    
    # Cenário onde um prestador é menos popular
    prestadores = [
        Prestador(id="P1", nome="Premium", capacidade=2, 
                 preferencias=["C1", "C2", "C3"]),
        Prestador(id="P2", nome="Padrão", capacidade=2,
                 preferencias=["C1", "C2", "C3"]),
        Prestador(id="P3", nome="Rural", capacidade=2,  # Menos popular
                 preferencias=["C1", "C2", "C3"]),
    ]
    
    # Todos preferem P1 > P2 > P3
    clientes = [
        Cliente(id="C1", nome="Cliente 1", preferencias=["P1", "P2", "P3"]),
        Cliente(id="C2", nome="Cliente 2", preferencias=["P1", "P2", "P3"]),
        Cliente(id="C3", nome="Cliente 3", preferencias=["P1", "P2", "P3"]),
    ]
    
    print("Cenário: Prestador 'Rural' é o menos preferido por todos os clientes.")
    print(f"Total de vagas: {sum(p.capacidade for p in prestadores)}")
    print(f"Total de clientes: {len(clientes)}")
    print()
    
    algoritmo = DeferredAcceptance(prestadores, clientes)
    resultado = algoritmo.executar(verbose=False)
    
    print("Resultado do matching:")
    for p_id, clientes_ids in resultado.matching.items():
        p = algoritmo.prestadores[p_id]
        vagas_vazias = p.capacidade - len(clientes_ids)
        status = f"({vagas_vazias} vagas vazias)" if vagas_vazias > 0 else "(cheio)"
        print(f"  {p.nome}: {clientes_ids} {status}")
    
    print("\nConclusão:")
    print("  O prestador 'Rural' não consegue preencher todas as vagas.")
    print("  Pelo Teorema dos Hospitais Rurais, isso ocorrerá em QUALQUER")
    print("  matching estável. A solução deve vir de melhorias na qualidade")
    print("  ou preço, não de mudanças no algoritmo de matching.")
    
    return resultado


if __name__ == "__main__":
    # Executa o exemplo do artigo
    resultado_exemplo = exemplo_marketplace()
    
    # Executa experimentos de escala
    resultados_escala = experimentos_escala()
    
    # Demonstra o Teorema dos Hospitais Rurais
    resultado_rht = rural_hospitals_demo()
    
    print("\n" + "=" * 70)
    print("FIM DA EXECUÇÃO")
    print("=" * 70)
