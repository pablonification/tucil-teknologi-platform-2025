import secrets
import base64
import pyotp
import uvicorn
import random
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import FileResponse, HTMLResponse
from sqlmodel import create_engine, Session, SQLModel, select
from typing import Annotated
from model import MOTD, MOTDBase

# SQLite Database
sqlite_file_name = "motd.db"
sqlite_url = f"sqlite:////{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session
SessionDep = Annotated[Session, Depends(get_session)]

# FastAPI
app = FastAPI(docs_url=None, redoc_url=None)
security = HTTPBasic()

# Users - lengkapi dengan userid dan shared_secret yang sesuai
users = {
    "sister": "ii2210_sister_keren", # Kredensial Asisten
    "arqila": "ii2210_arqila"        # Kredensial Sendiri
}

@app.get("/")
async def root():

    # Silahkan lengkapi dengan kode untuk memberikan index.html
    return FileResponse("index.html")

@app.get("/motd", response_class=HTMLResponse)
async def get_motd_html(session: SessionDep):
    statement = select(MOTD)
    results = session.exec(statement).all()
    
    html_content_base = """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pesan Hari Ini</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
            
            body {{
                font-family: 'Poppins', sans-serif;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                color: #333;
            }}
            .motd-container {{
                background-color: rgba(255, 255, 255, 0.9);
                padding: 30px 40px;
                border-radius: 15px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                text-align: center;
                max-width: 600px;
                width: 90%;
            }}
            h1 {{
                color: #2c3e50;
                margin-bottom: 20px;
                font-weight: 600;
            }}
            p.motd-text {{
                font-size: 1.2em;
                color: #555;
                line-height: 1.6;
                margin-bottom: 0;
                font-weight: 300;
                font-style: italic;
            }}
            p.error-text {{
                font-size: 1.1em;
                color: #e74c3c;
                font-weight: 400;
            }}
            a {{
                color: #3498db;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="motd-container">
            {content}
        </div>
    </body>
    </html>
    """

    if not results:
        # Jika tidak ada MOTD, tampilkan pesan error dalam HTML
        error_content = """
            <h1>Pesan Tidak Ditemukan</h1>
            <p class="error-text">Message of the day tidak dapat ditemukan.</p>
            <p>Silahkan coba lagi di lain waktu.</p>
            <p><a href="/">Kembali ke Main Page</a></p>
        """
        # Kembalikan HTMLResponse dengan status 404
        return HTMLResponse(content=html_content_base.format(content=error_content), status_code=404)
    
    # Pilih satu MOTD secara acak
    random_motd = random.choice(results)
    
    # Buat konten spesifik untuk MOTD yang ditemukan
    motd_content = f"""
        <h1>Message of the Day</h1>
        <p class="motd-text">"{random_motd.motd}"</p>
    """
    
    # Kembalikan HTMLResponse dengan konten MOTD
    return HTMLResponse(content=html_content_base.format(content=motd_content))

@app.post("/motd")
async def post_motd(message: MOTDBase, session: SessionDep, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):

	current_password_bytes = credentials.password.encode("utf8")

	valid_username, valid_password = False, False

	try:

		if credentials.username in users:
			valid_username = True
			s = base64.b32encode(users.get(credentials.username).encode("utf-8")).decode("utf-8")
			totp = pyotp.TOTP(s=s,digest="SHA256",digits=8)
			valid_password = secrets.compare_digest(current_password_bytes,totp.now().encode("utf8"))

			if valid_password and valid_username:
				
				# Silahkan lengkapi dengan kode untuk menambahkan message of the day ke basis data
				new_motd = MOTD(motd=message.motd)
				session.add(new_motd)
				session.commit()
				session.refresh(new_motd)
				return {"message": "MOTD berhasil ditambahkan"}
			
			else:

				raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid userid or password.") 
			
		else:

			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid userid or password.")
		
	except HTTPException as e:

	    raise e

if __name__ == "__main__":
	
	# Silahkan lengkapi dengan kode untuk menjalankan server
	create_db_and_tables()
	uvicorn.run("main:app", host="0.0.0.0", port=17787, reload=True)