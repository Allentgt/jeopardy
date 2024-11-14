import logging
import os

import uvicorn
import yaml
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()
# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount media files for questions (images, audio, etc.)
app.mount("/media", StaticFiles(directory="media"), name="media")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Load configuration
config_path = os.getenv("CONFIG_PATH", "config.yaml")

# Check if the config file exists
if not os.path.exists(config_path):
    raise FileNotFoundError(f"The configuration file '{config_path}' was not found.")

# Load the configuration file
with open(config_path, "r") as file:
    game_data = yaml.safe_load(file)

# Store game state
game_state = {
    "teams": [],
    "scores": {},
    "questions_left": 25,
    "board": [[False] * 5 for _ in range(5)]
}


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/start_game", response_class=HTMLResponse)
async def start_game(request: Request, team_names: str = Form(...), enable_negative_marks: bool = Form(False)):
    team_names = team_names.split(',')
    game_state["teams"] = team_names
    game_state["scores"] = {team: 0 for team in team_names}
    game_state["board"] = [[False] * 5 for _ in range(5)]
    game_state["questions_left"] = 25
    if enable_negative_marks:
        game_state["enable_negative_marks"] = True
        logger.info("*** Enabled negative marks ***")
    else:
        game_state["enable_negative_marks"] = False
        logger.info("*** Disabled negative marks ***")

    context = {
        "request": request,
        "game_data": game_data,
        "scores": game_state["scores"],
        "board": game_state["board"],
        "questions_left": game_state["questions_left"]
    }
    logger.info("Started the Game.")
    return templates.TemplateResponse("game.html", context)


@app.get("/question/{index}/{value}", response_class=HTMLResponse)
async def get_question(request: Request, index: int, value: int):
    value = int((value / 100) - 1)
    if game_state["board"][index][value]:
        raise HTTPException(status_code=400, detail="Question already answered")
    question = game_data["categories"][index]["questions"][value]
    context = {
        "request": request,
        "question": question,
        "teams": game_state["teams"],
        "index": index,
        "value": value
    }
    return templates.TemplateResponse("question.html", context)


@app.post("/answer", response_class=HTMLResponse)
async def submit_answer(request: Request, team: str = Form(...), index: int = Form(...), value: int = Form(...),
                        answer: str = Form(...)):
    question = game_data["categories"][index]["questions"][value]
    if answer.lower() in [question["answer"].lower(), "correct_answer"]:
        game_state["scores"][team] += question["points"]
    elif answer.lower() == "skip_question":
        logger.info("Skipping Question...")
    else:
        if game_state["enable_negative_marks"]:
            game_state["scores"][team] -= question["points"]
            logger.info("Wrong Answer! :(")
        else:
            logger.info("Wrong Answer! No -ve marking though :)")
    game_state["board"][index][value] = True
    game_state["questions_left"] -= 1
    if game_state["questions_left"] == 23:
        max_score = max(game_state["scores"].values())
        print(max_score)
        teams_with_max_score = [team for team, score in game_state["scores"].items() if score == max_score]
        tie = False
        if len(teams_with_max_score) > 1:
            tie = True
        context = {
            "request": request,
            "game_data": game_data,
            "scores": game_state["scores"],
            "winner": teams_with_max_score,
            "tie": tie
        }
        print(context)
        return templates.TemplateResponse("game_over.html", context)
    context = {
        "request": request,
        "game_data": game_data,
        "scores": game_state["scores"],
        "board": game_state["board"],
        "questions_left": game_state["questions_left"]
    }
    return templates.TemplateResponse("game.html", context)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
