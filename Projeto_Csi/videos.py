import yt_dlp
import mysql.connector
import re

# Configuração do banco de dados MySQL
database_db = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'sql10751878'
}

def converter_para_embed(url):
    match = re.search(r'(?:v=|be/|embed/)([a-zA-Z0-9_-]{11})', url)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}"
    return url

# Conecta ao banco
conn = mysql.connector.connect(**database_db)
cursor = conn.cursor()

# Criação da tabela, se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS aulas (
    curso_id INT,
    titulo TEXT,
    descricao TEXT,
    duracao INT,
    video_url TEXT,
    episodio INT,
    imagem TEXT
)
""")
episodio = 0
while True:
    url = input("\n🔗 Cole o link do vídeo do YouTube (ou digite 'sair' para finalizar): ").strip()
    if url.lower() == 'sair':
        break

    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            video_url_normal = info.get("webpage_url", url)
            video_url_embed = converter_para_embed(video_url_normal)

            dados = {
                "curso_id": 1,
                "titulo": info.get("title", ""),
                "descricao": info.get("description", ""),
                "duracao": int(info.get("duration", 0)),
                "video_url": video_url_embed,  # já no formato embed
                "episodio": episodio,
                "imagem": info.get("thumbnail", "")
            }

            cursor.execute("""
            INSERT INTO aulas (curso_id, titulo, descricao, duracao, video_url, episodio, imagem)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                dados["curso_id"],
                dados["titulo"],
                dados["descricao"],
                dados["duracao"],
                dados["video_url"],
                dados["episodio"],
                dados["imagem"]
            ))

            conn.commit()
            print(f"✅ Vídeo '{dados['titulo']}' inserido com sucesso com link embed.")
            episodio=+1
    except Exception as e:
        print(f"❌ Erro ao processar o vídeo: {e}")

cursor.close()
conn.close()
print("✅ Conexão com o banco encerrada.")


