from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import yaml

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Load configuration
with open("config.yaml", "r") as file:
    game_data = yaml.safe_load(file)

# Store game state
game_state = {
    "teams": [],
    "scores": {},
    "board": [[False] * 5 for _ in range(5)]  # Track whether a question is answered
}

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/start_game", response_class=HTMLResponse)
async def start_game(request: Request, team_names: str = Form(...)):
    team_names = team_names.split(',')
    game_state["teams"] = team_names
    game_state["scores"] = {team: 0 for team in team_names}
    game_state["board"] = [[False] * 5 for _ in range(5)]  # Reset board
    print(game_data)
    return templates.TemplateResponse("game.html", {"request": request, "teams": team_names, "game_data": game_data, "scores": game_state["scores"]})

@app.get("/question/{index}/{value}", response_class=HTMLResponse)
async def get_question(request: Request, index: int, value: int):
    value = int((value / 100) - 1)
    if game_state["board"][index][value]:
        raise HTTPException(status_code=400, detail="Question already answered")
    question = game_data["categories"][index]["questions"][value]
    return templates.TemplateResponse("question.html", {"request": request, "question": question, "teams": game_state["teams"]})

@app.post("/answer", response_class=HTMLResponse)
async def submit_answer(request: Request, team: str = Form(...), category: int = Form(...), value: int = Form(...), answer: str = Form(...)):
    print(team, category, value, answer)
    question = game_data["categories"][category]["questions"][value]
    if answer.lower() == question["answer"].lower():
        game_state["scores"][team] += question["points"]
    game_state["board"][category][value] = True  # Mark question as answered
    return templates.TemplateResponse("game.html", {"request": request, "teams": game_state["teams"], "game_data": game_data, "scores": game_state["scores"]})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app" , host="0.0.0.0", port=8000, reload=True)
