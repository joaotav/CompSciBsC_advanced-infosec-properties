#!/usr/bin/env python3
import socket, base64, hmac, hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

TAM_PAYLOAD = 512

def derivar_chave(chave):
    ''' Deriva uma chave para ser usada com o algoritmo de criptografia fernet
    a partir da chave gerada pelo processo de diffie-hellman '''
    salt = b''
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=10000,
    backend=default_backend())
    chave = base64.urlsafe_b64encode(kdf.derive(chave))

    return chave


def criptografar(mensagem, chave):
    ''' Criptografa uma string usando uma chave e o algoritmo Fernet '''
    mecanismo = Fernet(chave)
    return mecanismo.encrypt((mensagem).encode())


def decodificar(mensagem, chave):
    ''' Decodifica uma mensagem utilizando uma chave e o algoritmo Fernet '''
    mecanismo = Fernet(chave)
    mensagem = mecanismo.decrypt(mensagem.encode()).decode()
    return mensagem


def gerar_hmac(chave, info):
    ''' Gera um codigo HMAC para permitir a verificacao da integridade de uma string '''
    h = hmac.new(chave, info, hashlib.sha256)
    return h.hexdigest()


def verificar_hmac(payload, chave):
    ''' Verifica a integridade do payload recebido atraves do codigo HMAC '''
    payload = remover_padding(payload)
    msg_hmac = payload[-64:] # Os últimos 64 caracteres do payload são o HMAC
    dados = payload[:-64]
    h = hmac.new(chave, dados.encode(), hashlib.sha256)
    if h.hexdigest() == msg_hmac:
        return 'OK'
    else:
        return 'NOK'


def adicionar_padding(mensagem):
    ''' Preenche a mensagem com espacos vazios ate atingir o tamanho do payload '''
    encoded_size = len(bytes(mensagem.encode()))
    padding = (TAM_PAYLOAD - encoded_size + len(mensagem))
    # Preenche o final da mensagem com espaços vazios
    return mensagem.ljust(padding, ' ')


def remover_padding(mensagem):
    ''' Remove os espacos vazios ao final da mensagem, recuperando os dados originais '''
    # Remove o preenchimento ao final da mensagem
    return mensagem.decode().rstrip(' ')


def conectar(PORTA):
    ''' Estabelece uma conexao com o endereco 127.0.0.1 e a porta especificada '''
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Instancia um socket
        sock.connect((socket.gethostname(), PORTA))
        print("[+] Conexão com {} estabelecida.\n".format(sock.getsockname()))
    except ConnectionError:
        print("[+] Erro na conexão com o servidor.")
        raise SystemExit
    return sock


