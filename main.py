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
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Message of the Day</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary-color: #FFB7C3;
                --secondary-color: #BCF4F5;
                --card-bg: #F5F5F5;
                --text-color: #575757;
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Inter', sans-serif;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                margin: 0;
                padding: 20px;
            }}

            .motd-container {{
                background-color: white;
                padding: 32px;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
                text-align: center;
                max-width: 600px;
                width: 90%;
                transition: transform 0.3s ease;
            }}

            .motd-container:hover {{
                transform: translateY(-8px);
            }}

            h1 {{
                color: #2c3e50;
                margin-bottom: 20px;
                font-weight: 600;
                font-size: clamp(1.6rem, 2vw, 1.875rem);
                letter-spacing: -0.05em;
            }}

            .motd-text {{
                font-size: clamp(1.25rem, 1.5vw, 1.5rem);
                color: var(--text-color);
                line-height: 1.6;
                font-weight: 300;
                font-style: italic;
                margin-bottom: 24px;
                letter-spacing: -0.05em;
            }}

            .error-text {{
                font-size: 1.1em;
                color: #e74c3c;
                font-weight: 400;
                margin-bottom: 16px;
            }}

            a {{
                color: #3498db;
                text-decoration: none;
                font-weight: 500;
                transition: color 0.3s;
            }}

            a:hover {{
                color: #2980b9;
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
        error_content = """
            <h1>Message Not Found</h1>
            <p class="error-text">No message of the day available at the moment.</p>
            <p><a href="/">← Back to Home</a></p>
        """
        return HTMLResponse(content=html_content_base.format(content=error_content), status_code=404)
    
    random_motd = random.choice(results)
    
    motd_content = f"""
        <h1>Message of the Day</h1>
        <p class="motd-text">"{random_motd.motd}"</p>
        <p><a href="/">← Back to Home</a></p>
    """
    
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
				new_motd = MOTD(motd=message.motd, creator=credentials.username)
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