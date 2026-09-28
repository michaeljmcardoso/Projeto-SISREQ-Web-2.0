"""
Exporta o banco SISREQ e envia um commit ao GitHub pela API.
"""
import base64
import json
import os
import re
import sqlite3
import tempfile
import time
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from core_config import get_config


GITHUB_ENABLED = get_config(
    'GITHUB_ENABLED', 'false', section='github'
).lower() == 'true'
GITHUB_MODO_TESTE = get_config(
    'GITHUB_MODO_TESTE', 'false', section='github'
).lower() == 'true'
GITHUB_REPOSITORY = get_config('GITHUB_REPOSITORY', section='github').strip()
GITHUB_BRANCH = get_config('GITHUB_BRANCH', 'main', section='github').strip()
GITHUB_TOKEN = get_config('GITHUB_TOKEN', section='github').strip()
GITHUB_USER_NAME = get_config(
    'GITHUB_USER_NAME', 'SISREQ Bot', section='github'
).strip()
GITHUB_USER_EMAIL = get_config(
    'GITHUB_USER_EMAIL', 'bot@sisreq.local', section='github'
).strip()
DB_PATH = os.path.abspath(get_config('DB_PATH', 'sisreq.db'))
GITHUB_API = 'https://api.github.com'
GITHUB_MAX_BLOB_BYTES = 100 * 1024 * 1024


class GitHubSync:
    """Cria commits do banco e dos dados exportados no repositório configurado."""

    def __init__(self):
        self.repository = GITHUB_REPOSITORY
        self.branch = GITHUB_BRANCH
        self.token = GITHUB_TOKEN

    def _api(self, method: str, endpoint: str, payload: dict = None) -> dict:
        body = json.dumps(payload).encode('utf-8') if payload is not None else None
        request = Request(
            f'{GITHUB_API}{endpoint}',
            data=body,
            method=method,
            headers={
                'Accept': 'application/vnd.github+json',
                'Authorization': f'Bearer {self.token}',
                'X-GitHub-Api-Version': '2022-11-28',
                'User-Agent': 'SISREQ-Streamlit',
                'Content-Type': 'application/json',
            },
        )
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))

    def _snapshot(self) -> tuple[bytes, dict]:
        if not os.path.isfile(DB_PATH):
            raise FileNotFoundError(f'Banco SQLite não encontrado: {DB_PATH}')

        with tempfile.TemporaryDirectory() as temp_dir:
            snapshot_path = os.path.join(temp_dir, 'sisreq.db')
            source = sqlite3.connect(DB_PATH)
            destination = sqlite3.connect(snapshot_path)
            try:
                source.backup(destination)
            finally:
                destination.close()
                source.close()

            snapshot = sqlite3.connect(snapshot_path)
            snapshot.row_factory = sqlite3.Row
            try:
                integrity = snapshot.execute('PRAGMA integrity_check').fetchone()
                if not integrity or integrity[0] != 'ok':
                    raise sqlite3.DatabaseError(
                        f'Falha na verificação de integridade do banco: {integrity}'
                    )

                files = {
                    'sisreq.db': _read_bytes(snapshot_path),
                    'dados/sisreq.db': _read_bytes(snapshot_path),
                    'dados/processos.json': self._exportar_tabela(
                        snapshot, 'processos', 'processos'
                    ),
                    'dados/usuarios.json': self._exportar_usuarios(snapshot),
                    'dados/logs_acesso.json': self._exportar_logs(snapshot),
                }
                return files['sisreq.db'], files
            finally:
                snapshot.close()

    @staticmethod
    def _json_bytes(conteudo: dict) -> bytes:
        return json.dumps(
            conteudo, ensure_ascii=False, indent=2, default=str
        ).encode('utf-8')

    def _exportar_tabela(self, conn: sqlite3.Connection, tabela: str,
                         chave: str) -> bytes:
        registros = [dict(registro) for registro in conn.execute(
            f'SELECT * FROM {tabela}'
        ).fetchall()]
        return self._json_bytes({
            'exportado_em': datetime.now().isoformat(),
            f'total_{chave}': len(registros),
            chave: registros,
        })

    def _exportar_usuarios(self, conn: sqlite3.Connection) -> bytes:
        try:
            usuarios = [dict(registro) for registro in conn.execute("""
                SELECT id, usuario,
                       CASE
                           WHEN usuario = 'admin' THEN 'admin'
                           WHEN usuario = 'visitante' THEN 'visitante'
                           ELSE 'comum'
                       END AS perfil
                FROM usuarios
            """).fetchall()]
        except sqlite3.OperationalError:
            usuarios = []
        return self._json_bytes({
            'exportado_em': datetime.now().isoformat(),
            'total_usuarios': len(usuarios),
            'nota': 'Hashes de senha não são exportados neste arquivo.',
            'usuarios': usuarios,
        })

    def _exportar_logs(self, conn: sqlite3.Connection) -> bytes:
        try:
            logs = [dict(registro) for registro in conn.execute("""
                SELECT usuario, data_hora, data, hora, dia_semana,
                       ip_local, hostname, sistema, origem
                FROM logs_acesso
                ORDER BY id DESC
                LIMIT 5000
            """).fetchall()]
        except sqlite3.OperationalError:
            logs = []
        return self._json_bytes({
            'exportado_em': datetime.now().isoformat(),
            'total_logs': len(logs),
            'nota': 'Últimos 5000 acessos registrados.',
            'logs': logs,
        })

    def exportar_dados(self) -> dict:
        try:
            banco, arquivos = self._snapshot()
            if len(banco) > GITHUB_MAX_BLOB_BYTES:
                return {
                    'success': False,
                    'error': 'O banco excede o limite de 100 MB da API do GitHub.',
                }
            return {'success': True, 'files': arquivos}
        except (OSError, sqlite3.Error) as erro:
            return {'success': False, 'error': str(erro)}

    def commit_e_push(self, mensagem: str, arquivos: dict) -> dict:
        if GITHUB_MODO_TESTE:
            return {
                'success': True,
                'message': 'Modo de teste ativo: nenhum commit foi enviado.',
            }

        repository_path = '/repos/' + '/'.join(
            quote(parte, safe='') for parte in self.repository.split('/')
        )
        try:
            blobs = []
            for path, content in arquivos.items():
                if len(content) > GITHUB_MAX_BLOB_BYTES:
                    return {
                        'success': False,
                        'error': f'O arquivo {path} excede o limite de 100 MB.',
                    }
                blob = self._api('POST', f'{repository_path}/git/blobs', {
                    'content': base64.b64encode(content).decode('ascii'),
                    'encoding': 'base64',
                })
                blobs.append({
                    'path': path,
                    'mode': '100644',
                    'type': 'blob',
                    'sha': blob['sha'],
                })

            for tentativa in range(3):
                referencia = self._api(
                    'GET',
                    f'{repository_path}/git/ref/heads/{quote(self.branch, safe="")}',
                )
                sha_pai = referencia['object']['sha']
                commit_pai = self._api(
                    'GET', f'{repository_path}/git/commits/{sha_pai}'
                )
                arvore = self._api('POST', f'{repository_path}/git/trees', {
                    'base_tree': commit_pai['tree']['sha'],
                    'tree': blobs,
                })
                commit = self._api('POST', f'{repository_path}/git/commits', {
                    'message': mensagem,
                    'tree': arvore['sha'],
                    'parents': [sha_pai],
                    'author': {
                        'name': GITHUB_USER_NAME,
                        'email': GITHUB_USER_EMAIL,
                    },
                })
                try:
                    self._api(
                        'PATCH',
                        f'{repository_path}/git/refs/heads/'
                        f'{quote(self.branch, safe="")}',
                        {'sha': commit['sha'], 'force': False},
                    )
                    return {
                        'success': True,
                        'message': f'Commit enviado ao GitHub: {commit["sha"][:7]}',
                        'commit_hash': commit['sha'],
                    }
                except HTTPError as erro:
                    if erro.code not in (409, 422) or tentativa == 2:
                        raise
                    time.sleep(0.5 * (tentativa + 1))

            return {'success': False, 'error': 'Não foi possível atualizar a branch.'}
        except HTTPError as erro:
            mensagem_erro = erro.read().decode('utf-8', errors='replace')
            try:
                detalhe = json.loads(mensagem_erro).get('message', '')
            except json.JSONDecodeError:
                detalhe = ''
            return {
                'success': False,
                'error': f'GitHub API retornou HTTP {erro.code}'
                + (f': {detalhe}' if detalhe else ''),
            }
        except (URLError, TimeoutError, KeyError, ValueError) as erro:
            return {'success': False, 'error': f'Falha na sincronização: {erro}'}


def _read_bytes(path: str) -> bytes:
    with open(path, 'rb') as arquivo:
        return arquivo.read()


def sincronizar_github(tipo: str, dados: dict = None) -> dict:
    """Envia o snapshot atual do banco e os JSONs exportados ao GitHub."""
    if not GITHUB_ENABLED:
        return {
            'success': False,
            'error': 'Sincronização desativada: configure GITHUB_ENABLED=true.',
        }
    if not GITHUB_TOKEN:
        return {'success': False, 'error': 'GITHUB_TOKEN não foi configurado.'}
    if not re.fullmatch(r'[^/\s]+/[^/\s]+', GITHUB_REPOSITORY):
        return {
            'success': False,
            'error': 'GITHUB_REPOSITORY deve estar no formato proprietário/repositorio.',
        }
    if not GITHUB_BRANCH:
        return {'success': False, 'error': 'GITHUB_BRANCH não foi configurada.'}

    sync = GitHubSync()
    export = sync.exportar_dados()
    if not export['success']:
        return {'success': False, 'error': f"Exportação falhou: {export['error']}"}

    identificador = ''
    if dados:
        numero = dados.get('Numero', '')
        comunidade = dados.get('Comunidade', '')
        if numero or comunidade:
            identificador = f' — {numero} {comunidade}'.rstrip()
        else:
            referencia = (
                dados.get('Evento') or dados.get('Usuário')
                or dados.get('usuario') or ''
            )
            if referencia:
                identificador = f' — {referencia}'

    prefixos = {
        'cadastro': 'Novo processo',
        'edicao': 'Edição de processo',
        'exclusao': 'Exclusão de processo',
        'login': 'Registro de acesso',
        'manual': 'Sincronização manual',
        'contato': 'Alteração de contato',
        'usuario': 'Alteração de usuário',
    }
    prefixo = prefixos.get(tipo, 'Sincronização SISREQ')
    mensagem = (
        f'{prefixo}{identificador} '
        f'[{datetime.now():%Y-%m-%d %H:%M:%S}]'
    )
    return sync.commit_e_push(mensagem, export['files'])
