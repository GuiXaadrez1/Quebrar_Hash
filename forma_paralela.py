from multiprocessing import Pool, cpu_count
import hashlib
import string
import time
import os

def sha256_hash(s):
    """Calcula o hash SHA-256 de uma string."""
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def combina_indice(indice, caracteres, tamanho):
    """Gera a combinação correspondente ao índice."""
    base = len(caracteres)
    combinacao = []
    for _ in range(tamanho):
        combinacao.append(caracteres[indice % base])
        indice //= base
    return ''.join(reversed(combinacao))

def divide_tarefas(caracteres, tamanho, partes):
    """Divide o espaço de busca em partes sem gerar todas as combinações."""
    total_combinacoes = len(caracteres) ** tamanho
    parte_tamanho = total_combinacoes // partes
    tarefas = []

    for i in range(partes):
        inicio = i * parte_tamanho
        fim = inicio + parte_tamanho
        if i == partes - 1:  # Última parte pega o restante
            fim = total_combinacoes
        tarefas.append((inicio, fim))
    return tarefas

def verifica_hash_range(target_hash, inicio, fim, caracteres, tamanho):
    """Verifica hashes em um intervalo de índices."""
    for indice in range(inicio, fim):
        if indice % 10000000 == 0:  # Exibe progresso a cada 10 milhões de registros
            print(f"Progresso: Verificado até o índice {indice}")
        tentativa = combina_indice(indice, caracteres, tamanho)
        if sha256_hash(tentativa) == target_hash:
            return tentativa
    return None

def busca_paralela(target_hash):
    """Busca paralela pela string que corresponde ao hash alvo."""
    # Aumenta a prioridade do processo principal
    try:
        if os.name == "posix":  # Unix/Linux
            os.nice(-10)  # Diminui o valor de 'nice' para aumentar prioridade (superusuário pode usar valores menores)
        elif os.name == "nt":  # Windows
            import psutil
            psutil.Process(os.getpid()).nice(psutil.HIGH_PRIORITY_CLASS)
    except Exception as e:
        print(f"Não foi possível ajustar a prioridade do processo: {e}")

    caracteres = string.ascii_lowercase  # Letras de 'a' a 'z'
    tamanho = 7  # Tamanho da string
    num_processos = cpu_count()  # Número de CPUs disponíveis
    tarefas = divide_tarefas(caracteres, tamanho, num_processos)

    # Inicia os processos paralelos
    with Pool(processes=num_processos) as pool:
        resultados = pool.starmap(
            verifica_hash_range,
            [(target_hash, inicio, fim, caracteres, tamanho) for inicio, fim in tarefas]
        )

    # Verifica os resultados
    for resultado in resultados:
        if resultado:
            return resultado
    return None

if __name__ == "__main__":
    # Hash alvo
    target_hash = "70502ff6bb85356055ea52ff0a657afd09a52324a33734ccfb7bdedf05634925"

    print("Iniciando busca...")
    start_time = time.time()
    resultado = busca_paralela(target_hash)
    end_time = time.time()

    if resultado:
        print(f"String encontrada: {resultado}")
    else:
        print("String não encontrada.")
    print(f"Tempo total: {end_time - start_time:.2f} segundos.")
