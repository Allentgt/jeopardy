import yaml
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
logger = logging.getLogger(__name__)
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
    "questions_left": 25,
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
    return templates.TemplateResponse("game.html", {"request": request, "teams": team_names, "game_data": game_data,
                                                    "scores": game_state["scores"], "board": game_state["board"],
                                                    "questions_left": game_state["questions_left"]})


@app.get("/question/{index}/{value}", response_class=HTMLResponse)
async def get_question(request: Request, index: int, value: int):
    value = int((value / 100) - 1)
    if game_state["board"][index][value]:
        raise HTTPException(status_code=400, detail="Question already answered")
    question = game_data["categories"][index]["questions"][value]
    context = {"request": request, "question": question, "teams": game_state["teams"], "index": index, "value": value}
    return templates.TemplateResponse("question.html", context)


@app.post("/answer", response_class=HTMLResponse)
async def submit_answer(request: Request, team: str = Form(...), index: int = Form(...), value: int = Form(...),
                        answer: str = Form(...)):
    question = game_data["categories"][index]["questions"][value]
    if answer.lower() == question["answer"].lower():
        game_state["scores"][team] += question["points"]
    game_state["board"][index][value] = True  # Mark question as answered
    game_state["questions_left"] -= 1
    if game_state["questions_left"] == 0:
        return templates.TemplateResponse("game_over.html",
                                          {"request": request, "teams": game_state["teams"], "game_data": game_data,
                                           "scores": game_state["scores"], "winner": max(game_state["scores"], key=game_state["scores"].get)})
    context = {"request": request, "teams": game_state["teams"], "game_data": game_data, "scores": game_state["scores"],
               "board": game_state["board"], "questions_left": game_state["questions_left"]}
    return templates.TemplateResponse("game.html", context)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
