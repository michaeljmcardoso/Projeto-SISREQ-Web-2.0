"""
Módulo de sincronização com GitHub para o SISREQ.
Exporta o sisreq.db + um JSON resumido e faz commit/push.
"""
import os
import json
import sqlite3
import shutil
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# TENTAR IMPORTAR GITPYTHON
# =========================================================
try:
    from git import Repo
    GIT_DISPONIVEL = True
except ImportError:
    GIT_DISPONIVEL = False
    print("⚠️ GitPython não instalado. Rode: pip install GitPython")


# =========================================================
# CONFIGURAÇÕES
# =========================================================
GITHUB_ENABLED   = os.getenv('GITHUB_ENABLED', 'False').lower() == 'true'
GITHUB_MODO_TESTE = os.getenv('GITHUB_MODO_TESTE', 'True').lower() == 'true'
GITHUB_REPO_PATH = os.getenv('GITHUB_REPO_PATH', os.getcwd())
GITHUB_BRANCH    = os.getenv('GITHUB_BRANCH', 'main')
GITHUB_USER_NAME  = os.getenv('GITHUB_USER_NAME', 'SISREQ Bot')
GITHUB_USER_EMAIL = os.getenv('GITHUB_USER_EMAIL', 'bot@sisreq.local')
GITHUB_TOKEN      = os.getenv('GITHUB_TOKEN', '')


class GitHubSync:
    """Gerencia commit + push do sisreq.db para o GitHub."""

    def __init__(self):
        self.enabled   = GITHUB_ENABLED
        self.modo_teste = GITHUB_MODO_TESTE
        self.repo_path = GITHUB_REPO_PATH
        self.branch    = GITHUB_BRANCH
        self.token     = GITHUB_TOKEN
        self.repo      = None

        if self.enabled and GIT_DISPONIVEL:
            self._carregar_repo()

    def _carregar_repo(self):
        try:
            if not os.path.isdir(self.repo_path):
                print(f"⚠️ Pasta do repositório não existe: {self.repo_path}")
                return
            self.repo = Repo(self.repo_path)
            print(f"✅ Repositório Git carregado: {self.repo_path}")
        except Exception as e:
            print(f"❌ Erro ao carregar repositório: {e}")

    # -----------------------------------------------------
    # EXPORTAR DADOS
    # -----------------------------------------------------
        # -----------------------------------------------------
    # EXPORTAR DADOS
    # -----------------------------------------------------
    def exportar_dados(self):
        """
        Exporta os dados do SISREQ para <repo>/dados/:
          1) processos.json    — todos os processos
          2) usuarios.json     — usuários (SEM hashes de senha!)
          3) logs_acesso.json  — histórico de acessos (últimos 5000)
          4) sisreq.db         — cópia completa (SOMENTE se permitido)

        Modo de cópia do .db:
          - .env:  GITHUB_COPIAR_DB=True
          - Detecta automaticamente se está no Streamlit Cloud
          - Repositório deve ser PRIVADO (sua responsabilidade)
        """
        if not self.repo:
            return {'success': False, 'error': 'Repositório não carregado'}

        try:
            dados_dir = os.path.join(self.repo_path, 'dados')
            os.makedirs(dados_dir, exist_ok=True)

            db_origem = os.path.join(os.getcwd(), 'sisreq.db')
            db_destino = os.path.join(dados_dir, 'sisreq.db')

            if not os.path.exists(db_origem):
                return {'success': False, 'error': f'Banco não encontrado: {db_origem}'}

            # ═════════════════════════════════════════════
            # 0) DECIDIR SE COPIA O .db
            # ═════════════════════════════════════════════
            copiar_db = self._deve_copiar_db()
            db_copiado = False
            db_tamanho_mb = 0.0

            if copiar_db:
                try:
                    # Verificar integridade antes de copiar
                    if self._verificar_integridade_db(db_origem):
                        # Fazer checkpoint do WAL (se houver)
                        self._checkpoint_sqlite(db_origem)

                        shutil.copy2(db_origem, db_destino)
                        db_copiado = True
                        db_tamanho_mb = os.path.getsize(db_destino) / (1024 * 1024)

                        print(f"✅ [sync] sisreq.db copiado "
                              f"({db_tamanho_mb:.2f} MB)")
                    else:
                        print("⚠️ [sync] Banco corrompido — cópia abortada")
                except Exception as e:
                    print(f"⚠️ [sync] Erro ao copiar .db: {e}")
            else:
                print("ℹ️ [sync] Cópia do .db desabilitada neste ambiente")

            # ═════════════════════════════════════════════
            # 1) PROCESSOS
            # ═════════════════════════════════════════════
            conn = sqlite3.connect(db_origem)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            try:
                cursor.execute("SELECT * FROM processos")
                processos = [dict(r) for r in cursor.fetchall()]
            except Exception as e:
                processos = []
                print(f"⚠️ Erro ao ler processos: {e}")

            processos_path = os.path.join(dados_dir, 'processos.json')
            with open(processos_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'exportado_em': datetime.now().isoformat(),
                    'total_processos': len(processos),
                    'processos': processos
                }, f, ensure_ascii=False, indent=2)

            # ═════════════════════════════════════════════
            # 2) USUÁRIOS (SEM SENHAS!)
            # ═════════════════════════════════════════════
            try:
                cursor.execute("""
                    SELECT id, usuario,
                           CASE
                               WHEN usuario = 'admin'     THEN 'admin'
                               WHEN usuario = 'visitante' THEN 'visitante'
                               ELSE 'comum'
                           END AS perfil
                    FROM usuarios
                """)
                usuarios = [dict(r) for r in cursor.fetchall()]
            except Exception as e:
                usuarios = []
                print(f"⚠️ Erro ao ler usuários: {e}")

            usuarios_path = os.path.join(dados_dir, 'usuarios.json')
            with open(usuarios_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'exportado_em': datetime.now().isoformat(),
                    'total_usuarios': len(usuarios),
                    'nota': 'Hashes de senha NÃO são exportados por segurança.',
                    'usuarios': usuarios
                }, f, ensure_ascii=False, indent=2)

            # ═════════════════════════════════════════════
            # 3) LOGS DE ACESSO (métricas)
            # ═════════════════════════════════════════════
            try:
                cursor.execute("""
                    SELECT usuario, data_hora, data, hora, dia_semana,
                           ip_local, hostname, sistema, origem
                    FROM logs_acesso
                    ORDER BY id DESC
                    LIMIT 5000
                """)
                logs = [dict(r) for r in cursor.fetchall()]
            except Exception as e:
                logs = []
                print(f"ℹ️ Logs de acesso não disponíveis: {e}")

            logs_path = os.path.join(dados_dir, 'logs_acesso.json')
            with open(logs_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'exportado_em': datetime.now().isoformat(),
                    'total_logs': len(logs),
                    'nota': 'Últimos 5000 acessos registrados.',
                    'logs': logs
                }, f, ensure_ascii=False, indent=2)

            conn.close()

            # ═════════════════════════════════════════════
            # Retorno consolidado
            # ═════════════════════════════════════════════
            return {
                'success': True,
                'total_processos':  len(processos),
                'total_usuarios':   len(usuarios),
                'total_logs':       len(logs),
                'db_copiado':       db_copiado,
                'db_tamanho_mb':    round(db_tamanho_mb, 2),
                'db_path':          db_destino,
                'processos_path':   processos_path,
                'usuarios_path':    usuarios_path,
                'logs_path':        logs_path,
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}
            

    # -----------------------------------------------------
    # COMMIT + PUSH
    # -----------------------------------------------------
    def commit_e_push(self, mensagem: str):
        if not self.repo:
            return {'success': False, 'error': 'Repositório não carregado'}

        try:
            # Configurar usuário
            with self.repo.config_writer() as cw:
                cw.set_value('user', 'name', GITHUB_USER_NAME)
                cw.set_value('user', 'email', GITHUB_USER_EMAIL)

            # Stage tudo em dados/
            self.repo.git.add(A=True)

            # Verificar se há mudanças
            if not self.repo.is_dirty(untracked_files=True):
                return {'success': True, 'message': 'Nada a sincronizar (sem mudanças)'}

            # Commit
            commit = self.repo.index.commit(mensagem)

            if self.modo_teste:
                return {
                    'success': True,
                    'message': f'[MODO TESTE] Commit local: {commit.hexsha[:7]}',
                    'commit_hash': commit.hexsha,
                }

            # Push
            if self.token:
                # Atualizar remote com token
                remote_url = self.repo.remotes.origin.url
                if 'https://' in remote_url and '@' not in remote_url:
                    auth_url = remote_url.replace('https://', f'https://{self.token}@')
                    self.repo.remotes.origin.set_url(auth_url)

            self.repo.remotes.origin.push(refspec=f'{self.branch}:{self.branch}')
            return {
                'success': True,
                'message': f'Push realizado: {commit.hexsha[:7]}',
                'commit_hash': commit.hexsha,
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


# =========================================================
# FUNÇÃO DE ALTO NÍVEL — é a que os módulos chamam
# =========================================================
def sincronizar_github(tipo: str, dados: dict = None):
    """
    Exporta os dados + faz commit/push.

    tipo: 'cadastro' | 'edicao' | 'exclusao' | 'manual'
    """
    if not GITHUB_ENABLED:
        return {'success': False, 'error': 'GITHUB_ENABLED=False'}

    sync = GitHubSync()
    if not sync.repo:
        return {'success': False, 'error': 'Repositório Git não carregado'}

    # 1) Exportar
    export = sync.exportar_dados()
    if not export['success']:
        return {'success': False, 'error': f"Exportação falhou: {export.get('error')}"}

    # 2) Mensagem de commit por tipo
    comunidade = ''
    if dados:
        comunidade = dados.get('Comunidade', '')
        numero = dados.get('Numero', '')
    else:
        numero = ''

    prefixos = {
        'cadastro': '➕ Novo processo',
        'edicao':   '✏️ Edição de processo',
        'exclusao': '🗑️ Exclusão de processo',
        'login':    '🔐 Registro de acesso',
        'manual':   '🔄 Sincronização manual',
    }
    prefixo = prefixos.get(tipo, '🔄 Sync')
    msg = f"{prefixo} — {numero} {comunidade} [{datetime.now():%d/%m/%Y %H:%M}]"

    # 3) Commit + push
    result = sync.commit_e_push(msg)
    return result

# -----------------------------------------------------
# DECIDIR SE DEVE COPIAR O .db
# -----------------------------------------------------
def _deve_copiar_db(self) -> bool:
    """
    Retorna True se o .db deve ser copiado para o repositório.

    Regras:
        1. Se GITHUB_COPIAR_DB=False no .env  → NUNCA copia
        2. Se GITHUB_COPIAR_DB=True           → SEMPRE copia
        3. Se não definido                    → só copia no Streamlit Cloud
    """
    env_value = os.getenv('GITHUB_COPIAR_DB', '').lower()

    if env_value == 'true':
        return True
    if env_value == 'false':
        return False

    # Auto-detecção: está no Streamlit Cloud?
    return self._is_streamlit_cloud()

# -----------------------------------------------------
# DETECTAR STREAMLIT CLOUD
# -----------------------------------------------------
def _is_streamlit_cloud(self) -> bool:
    """
    Detecta se está rodando no Streamlit Community Cloud.
    Baseado em variáveis de ambiente que o Cloud injeta.
    """
    # O Streamlit Cloud define essas variáveis:
    indicadores = [
        'STREAMLIT_SHARING_MODE',   # legado
        'STREAMLIT_RUNTIME_ENV',    # atual
        'IS_STREAMLIT_CLOUD',
    ]

    for var in indicadores:
        if os.getenv(var):
            return True

    # Fallback: o path típico do Cloud é /mount/src/...
    cwd = os.getcwd()
    if cwd.startswith('/mount/src/'):
        return True

    # Fallback: pasta .streamlit/config.toml com serverHeadless=true
    # costuma indicar ambiente headless (Cloud)
    if os.path.exists('/home/adminuser') or os.path.exists('/home/appuser'):
        return True

    return False

# -----------------------------------------------------
# VERIFICAR INTEGRIDADE DO SQLITE
# -----------------------------------------------------
def _verificar_integridade_db(self, db_path: str) -> bool:
    """
    Executa PRAGMA integrity_check para garantir que o banco
    não está corrompido antes de copiar.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        resultado = cursor.fetchone()
        conn.close()

        if resultado and resultado[0] == 'ok':
            return True

        print(f"⚠️ [sync] integrity_check retornou: {resultado}")
        return False
    except Exception as e:
        print(f"⚠️ [sync] Erro no integrity_check: {e}")
        return False

# -----------------------------------------------------
# CHECKPOINT DO WAL (evita copiar .db incompleto)
# -----------------------------------------------------
def _checkpoint_sqlite(self, db_path: str):
    """
    Força o SQLite a escrever o WAL no arquivo principal.
    Sem isso, você pode copiar um .db sem as últimas transações.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA wal_checkpoint(FULL)")
        conn.commit()
        conn.close()
        print("✅ [sync] WAL checkpoint concluído")
    except Exception as e:
        print(f"⚠️ [sync] Erro no WAL checkpoint: {e}")