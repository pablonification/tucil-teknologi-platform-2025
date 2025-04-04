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
                --nav-highlight: #ffb7c3;
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
                flex-direction: column;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                margin: 0;
                padding: 20px;
            }}

            .navbar {{
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                z-index: 50;
                padding: 12px;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 16px;
            }}

            .nav-container {{
                background-color: black;
                color: white;
                border-radius: 20px;
                padding: 4px 6px;
                display: flex;
                align-items: center;
                position: relative;
                overflow: hidden;
            }}

            .nav-highlight {{
                position: absolute;
                height: 85%;
                transform: translateX(0);
                background-color: var(--nav-highlight);
                border-radius: 16px;
                transition: all 0.5s ease-out;
                opacity: 0.75;
            }}

            .nav-icon {{
                position: relative;
                padding: 4px 8px;
                display: inline-block;
            }}

            .nav-icon img {{
                width: 24px;
                height: 24px;
                position: relative;
                z-index: 10;
                transition: transform 0.5s;
            }}

            .nav-link {{
                position: relative;
                padding: 4px 8px;
                font-size: 16px;
                font-weight: 500;
                white-space: nowrap;
                transition: color 0.3s;
                text-decoration: none;
                color: rgba(255, 255, 255, 0.9);
            }}

            .nav-link span {{
                position: relative;
                z-index: 10;
                transition: color 0.3s;
            }}

            .motd-link {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                color: black;
                text-decoration: none;
                font-weight: 500;
                padding: 8px 16px;
                border-radius: 20px;
                transition: all 0.3s;
                background: white;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                white-space: nowrap;
                font-size: 14px;
            }}

            .motd-link:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
            }}

            .motd-arrow {{
                width: 16px;
                height: 16px;
                transition: transform 0.3s;
            }}

            .motd-link:hover .motd-arrow {{
                transform: translateX(4px);
            }}

            @media (max-width: 480px) {{
                .navbar {{
                    padding: 8px;
                    gap: 8px;
                }}

                .nav-container {{
                    padding: 4px 6px;
                }}

                .nav-link {{
                    font-size: 13px;
                    padding: 4px 6px;
                }}

                .motd-link {{
                    padding: 4px 10px;
                    font-size: 13px;
                    height: 28px;
                }}

                .nav-icon img {{
                    width: 18px;
                    height: 18px;
                }}
            }}

            @media (max-width: 360px) {{
                .nav-link span {{
                    display: none;
                }}

                .nav-link[data-tab="home"] span {{
                    display: inline;
                }}
            }}

            .content {{
                flex: 1;
                display: flex;
                justify-content: center;
                align-items: center;
                padding-top: 80px;
            }}

            .motd-container {{
                background-color: white;
                padding: 32px;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
                text-align: center;
                max-width: 600px;
                width: 90%;
                position: relative;
                overflow: hidden;
            }}

            .motd-container::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
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

            .creator-text {{
                font-size: 0.9em;
                color: #666;
                margin-bottom: 24px;
            }}

            .error-text {{
                font-size: 1.1em;
                color: #e74c3c;
                font-weight: 400;
                margin-bottom: 16px;
            }}
        </style>
    </head>
    <body>
        <nav class="navbar">
            <div class="nav-container">
                <div class="nav-highlight"></div>
                <a href="/" class="nav-icon">
                    <img src="https://raw.githubusercontent.com/pablonification/portfolio-arqila/refs/heads/main/public/iconamoon_confused-face-fill.svg" alt="Navigation icon">
                </a>
                <a href="/" class="nav-link" data-tab="home">
                    <span>Home</span>
                </a>
            </div>
            <a href="/motd" class="motd-link">
                <span>✨ MOTD</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="motd-arrow">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
            </a>
        </nav>
        <div class="content">
            <div class="motd-container">
                {content}
            </div>
        </div>
    </body>
    </html>
    """

    if not results:
        error_content = """
            <h1>Message Not Found</h1>
            <p class="error-text">No message of the day available at the moment.</p>
            <p class="creator-text">Try again later or add a new message!</p>
        """
        return HTMLResponse(content=html_content_base.format(content=error_content), status_code=404)
    
    random_motd = random.choice(results)
    
    motd_content = f"""
        <h1>Message of the Day</h1>
        <p class="motd-text">{random_motd.motd}</p>
        <p class="creator-text">Posted by {random_motd.creator}</p>
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